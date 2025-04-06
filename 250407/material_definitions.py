# material_definitions.py

MATERIAL_DEFINITIONS = {
    "Foam": {
        "properties": [
            {"name": "thickness", "label": "Thickness [mm]"},
            {"name": "viscous_cl", "label": "Viscous CL [m]"},
            {"name": "thermal_cl", "label": "Thermal CL [m]"},
            {"name": "density", "label": "Density [kg/m3]"},
            {"name": "airflow_resistivity", "label": "Airflow resistivity [Pa*s/m2]"},
            {"name": "tortuosity", "label": "Tortuosity"},
            {"name": "porosity", "label": "Porosity"},
            {"name": "loss_factor", "label": "Loss Factor"},
            {"name": "poissons_ratio", "label": "Poisson's Ratio"}
        ],
        "color": "orange",
        "image": None
    },
    "Aluminum": {
        "properties": [
            {"name": "thickness", "label": "Thickness [mm]"},
            {"name": "loss_factor", "label": "Loss Factor"},
            {"name": "youngs_modulus", "label": "Static Young's Modulus [Pa]"},
            {"name": "poissons_ratio", "label": "Poisson's Ratio"},
            {"name": "density", "label": "Density [kg/m3]"}
        ],
        "color": "royalblue",
        "image": None
    }
}