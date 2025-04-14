import numpy as np

def jca_rigid(w, sigma, phi, a1, VCL, TCL, rho0, eta, Pr, gamma, P0):
    # Dynamic effective density (Johnson et al. 1987)
    M = sigma * phi / (1j * w * a1 * rho0)
    N = np.sqrt(1 + 4j * eta * rho0 * w * a1**2 / (sigma**2 * VCL**2 * phi**2))
    rhoeq = rho0 * a1 / phi * (1 + M * N)

    # Dynamic bulk modulus (Champoux & Allard 1991)
    Q = 8j * eta / (TCL**2 * Pr * rho0 * w)
    S = np.sqrt(1 + 1j * TCL**2 * Pr * rho0 * w / (16 * eta))
    U = (gamma - 1) / (1 - Q * S)
    Keq = gamma * P0 / phi / (gamma - U)

    return rhoeq, Keq