import numpy as np

def tm_solid(w_array, d, rho, E, nu, theta_deg, c0):
    theta = np.radians(theta_deg)
    k0 = w_array / c0
    kt = k0 * np.sin(theta)

    mu = E / (1 + nu) / 2  # Shear modulus
    lam = E * nu / (1 + nu) / (1 - 2 * nu)  # Lame lambda

    k1 = w_array * np.sqrt(rho / (lam + 2 * mu))
    k3 = w_array * np.sqrt(rho / mu)

    k13 = np.sqrt(np.maximum(k1**2 - kt**2, np.finfo(float).eps))
    k33 = np.sqrt(np.maximum(k3**2 - kt**2, np.finfo(float).eps))

    D1 = lam * (k13**2 + kt**2) + 2 * mu * k13**2
    D2 = 2 * mu * kt

    N = len(w_array)
    Taux = np.zeros((4, 4, N), dtype=np.complex128)
    Lambda = np.zeros((4, 4, N), dtype=np.complex128)
    Alpha = np.zeros((4, N), dtype=np.complex128)

    # Column-wise Taux construction
    Taux[0, 0, :] = w_array * kt
    Taux[1, 0, :] = w_array * k13
    Taux[2, 0, :] = -D1
    Taux[3, 0, :] = -D2 * k13

    Taux[0, 1, :] = w_array * kt
    Taux[1, 1, :] = -w_array * k13
    Taux[2, 1, :] = -D1
    Taux[3, 1, :] = D2 * k13

    Taux[0, 2, :] = -w_array * k33
    Taux[1, 2, :] = w_array * kt
    Taux[2, 2, :] = -D2 * k33
    Taux[3, 2, :] = D1

    Taux[0, 3, :] = w_array * k33
    Taux[1, 3, :] = w_array * kt
    Taux[2, 3, :] = D2 * k33
    Taux[3, 3, :] = D1

    # Wave decay/growth constants
    Alpha[0, :] = -1j * k13
    Alpha[1, :] =  1j * k13
    Alpha[2, :] = -1j * k33
    Alpha[3, :] =  1j * k33

    for i in range(N):
        Lambda[:, :, i] = np.diag(np.exp(Alpha[:, i] * -d))

    return Taux, Lambda