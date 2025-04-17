import numpy as np
import matplotlib.pyplot as plt

from air_properties import air_properties
from bc_matrix import bc_matrix
from jca_rigid import jca_rigid
from merge_layer import merge_layer
from one_layer_pred import one_layer_pred
from tm_panel import tm_panel
from tm_poro import tm_poro
from tm_solid import tm_solid

def compute_transfer_matrix(mat_type, mat, wi, theta, theta_deg, rho0, eta, Pr, gamma, P0, c0):
    if mat_type == 'poro':
        params = [mat["airflow_resistivity"], mat["porosity"], mat["tortuosity"], mat["viscous_cl"], mat["thermal_cl"]]
        rhoeq, Keq = jca_rigid(wi, *params, rho0, eta, Pr, gamma, P0)
        rho22 = mat["porosity"] ** 2 * rhoeq
        rho12 = mat["porosity"] * rho0 - rho22
        rho11 = mat["density"] - rho12
        complex_E = mat["youngs_modulus"] * (1 + 1j * mat.get("loss_factor", 0))
        return tm_poro(np.array([wi]), mat["h"], mat["porosity"], complex_E, Keq,
                       mat["poissons_ratio"], theta, c0, rho11, rho12, rho22)
    elif mat_type == 'plastic':
        return tm_solid(np.array([wi]), mat["h"], mat["density"],
                        mat["youngs_modulus"], mat["poissons_ratio"], theta_deg, c0)
    elif mat_type == 'stiff panel':
        E = mat["youngs_modulus"] * mat["h"]
        I = mat["youngs_modulus"] * mat["h"] ** 3 / (12 * (1 - mat["poissons_ratio"] ** 2))
        return tm_panel(np.array([wi]), c0, mat["h"], mat["density"] * mat["h"], E, I, theta_deg)
    else:
        raise ValueError(f"[ERROR] Unsupported material type: {mat_type}")

def map_type(elastic_type):
    if elastic_type == "Poro-elastic":
        return "poro"
    elif elastic_type == "Viscoelastic":
        return "stiff panel"
    elif elastic_type == "Linear Elastic":
        return "plastic"
    elif elastic_type in ["Unboned", "Unbonded"]:
        return "fluid"

def run_simulation_from_ui(layer_data: list, theta_deg=0, P0=101325, T=20, RH=0.2):
    f = np.logspace(np.log10(100), np.log10(6400), 1000)
    w = 2 * np.pi * f
    theta = np.radians(theta_deg)

    rho0, c0, gamma, eta, Pr, *_ = air_properties(P0, T, RH)
    z0 = rho0 * c0

    layers = [map_type(layer["type"]) for layer in layer_data]
    material_map = {}
    for i, layer in enumerate(layer_data):
        mat_type = layers[i]
        if mat_type != "fluid":
            data = layer.copy()
            data["h"] = data.pop("thickness")
            material_map[mat_type + f"_{i}"] = data

    BC = np.empty((len(layers) + 1, 2), dtype=object)
    bc_types = []

    for i in range(len(layers) + 1):
        if i == 0:
            mat1, mat2 = "fluid", layers[0]
            phi = material_map.get(mat2 + "_0", {}).get("porosity", 0.99)
        elif i == len(layers):
            mat1, mat2 = layers[-1], "fluid"
            phi = material_map.get(mat1 + f"_{i-1}", {}).get("porosity", 0.99)
        else:
            mat1, mat2 = layers[i - 1], layers[i]
            phi = material_map.get(mat1 + f"_{i-1}", {}).get("porosity", 0.99)

        bc_types.append((mat1, mat2))
        try:
            BC[i, 0], BC[i, 1] = bc_matrix(mat1, mat2, phi)
        except:
            BC[i, 0], BC[i, 1] = bc_matrix(mat1, mat2)

    tc = np.zeros(len(w), dtype=np.complex128)
    TM_all = np.zeros((2, 2, len(w)), dtype=np.complex128)

    for i_freq, wi in enumerate(w):
        segments = []
        current_segment = []
        for i in range(len(bc_types) - 1):
            current_segment.append(i)
            _, mat2 = bc_types[i]
            if mat2 == "fluid":
                segments.append(current_segment)
                current_segment = []
        if current_segment:
            segments.append(current_segment)

        TM_total = np.eye(2, dtype=np.complex128)

        for seg in segments:
            BC_working = BC.copy()

            for j in seg:
                mat_type = bc_types[j + 1][0]
                if mat_type == 'fluid':
                    continue
                mat = material_map[mat_type + f"_{j}"]
                Phi, Lambda = compute_transfer_matrix(mat_type, mat, wi, theta, theta_deg, rho0, eta, Pr, gamma, P0, c0)

                mat1_next, mat2_next = bc_types[j + 1]
                if mat1_next != "fluid" and mat2_next != "fluid":
                    B1_pos, B2_neg = merge_layer(
                        BC_working[j, 0], BC_working[j, 1],
                        BC_working[j + 1, 0], BC_working[j + 1, 1],
                        Phi[:, :, 0], Lambda[:, :, 0])
                    BC_working[j + 1, 0], BC_working[j + 1, 1] = B1_pos, B2_neg
                else:
                    TM_seg = one_layer_pred(
                        BC_working[j, 0], BC_working[j, 1],
                        BC_working[j + 1, 0], BC_working[j + 1, 1],
                        Phi[:, :, 0], Lambda[:, :, 0])
                    TM_total = TM_total @ TM_seg

        TM_all[:, :, i_freq] = TM_total

        total_d = sum(m["h"] for k, m in material_map.items() if not k.startswith("fluid"))
        denom = (TM_total[0, 0] + TM_total[0, 1] * np.cos(theta) / z0 + TM_total[1, 0] * z0 / np.cos(theta) + TM_total[1, 1])
        tc[i_freq] = 0 if np.abs(denom) < 1e-12 else 2 * np.exp(1j * wi * total_d * np.cos(theta) / c0) / denom

    TL = 20 * np.log10(1 / np.abs(tc))
    return f, TL, tc
