MATERIAL_DEFINITIONS = {
    "Poro-elastic": {
        "properties": [
            {"name": "material", "label": "material"},
            {"name": "thickness", "label": "Thickness [mm]"},
            {"name": "viscous_cl", "label": "Viscous CL [m]"},
            {"name": "thermal_cl", "label": "Thermal CL [m]"},
            {"name": "airflow_resistivity", "label": "Airflow resistivity [Pa*s/m2]"},
            {"name": "tortuosity", "label": "Tortuosity"},
            {"name": "porosity", "label": "Porosity"},
            {"name": "youngs_modulus", "label": "Static Young's Modulus [Pa]"},
            {"name": "loss_factor", "label": "Loss Factor"},
            {"name": "poissons_ratio", "label": "Poisson's Ratio"},
            {"name": "density", "label": "Density [kg/m3]"}
        ],
        "color": "orange",
        "image": None
    },
    "Viscoelastic": {
        "properties": [
            {"name": "material", "label": "material"},
            {"name": "thickness", "label": "Thickness [mm]"},
            {"name": "youngs_modulus", "label": "Static Young's Modulus [Pa]"},
            {"name": "loss_factor", "label": "Loss Factor"},
            {"name": "poissons_ratio", "label": "Poisson's Ratio"},
            {"name": "density", "label": "Density [kg/m3]"}
        ],
        "color": "royalblue",
        "image": None
    },
    "Linear Elastic": {
        "properties": [
            {"name": "material", "label": "material"},
            {"name": "thickness", "label": "Thickness [mm]"},
            {"name": "youngs_modulus", "label": "Static Young's Modulus [Pa]"},
            {"name": "poissons_ratio", "label": "Poisson's Ratio"},
            {"name": "density", "label": "Density [kg/m3]"}
        ],
        "color": "green",
        "image": None
    }
}
