import numpy as np

def air_properties(P0, T, RH):
    # Specific gas constant of dry air and water vapor
    Rd = 287.058
    Rv = 461.495

    # Partial vapor pressure (Pa)
    pv = RH * 6.102 * 10 ** (7.5 * T / (T + 237.8))
    pd = P0 - pv

    # Gas constant for humid air
    Rg = P0 / (pd / Rd + pv / Rv)

    # Speed of sound [m/s]
    c0 = 20.047 * np.sqrt(273.15 + T)

    # Air density [kg/m^3]
    rho0 = 1.290 * (P0 / 101325) * (273.15 / (273.15 + T))

    # Dynamic viscosity (Sutherland's Law)
    eta = 1.716e-5 * ((T + 273.15) / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 273.15 + 110.4)

    # Prandtl number
    Pr = 0.707

    # Specific heat ratio
    gamma = 1.4

    # Molecular properties (from Venegas 2016)
    Sm = 4.3265e-19   # m^2
    m = 4.8106e-26    # kg
    Dc = 1.35e-10     # m^2/s

    return rho0, c0, gamma, eta, Pr, Rg, Dc, m, Sm
