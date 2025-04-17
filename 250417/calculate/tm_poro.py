import numpy as np

def tm_poro(w, d, phi, E, Kf, nu, theta, c0, rho11, rho12, rho22):
    kt = w / c0 * np.sin(theta)  # transverse wave number

    Kb = E / (3 * (1 - 2 * nu))
    N = E / (2 * (1 + nu))
    P = 4 / 3 * N + Kb + Kf * (1 - phi) ** 2
    Q = Kf * phi * (1 - phi)
    R = Kf * phi ** 2

    delta = (P * rho22 + R * rho11 - 2 * Q * rho12) ** 2 - \
            4 * (P * R - Q ** 2) * (rho11 * rho22 - rho12 ** 2)

    k1 = np.sqrt((w ** 2 * (P * rho22 + R * rho11 - 2 * Q * rho12 - np.sqrt(delta))) /
                 (2 * (P * R - Q ** 2)))
    k2 = np.sqrt((w ** 2 * (P * rho22 + R * rho11 - 2 * Q * rho12 + np.sqrt(delta))) /
                 (2 * (P * R - Q ** 2)))
    k3 = np.sqrt(w ** 2 * (rho11 * rho22 - rho12 ** 2) / (N * rho22))

    K = np.array([k1, k2, k3])  # shape (3, len(w))

    k13 = np.sqrt(k1 ** 2 - kt ** 2)
    k23 = np.sqrt(k2 ** 2 - kt ** 2)
    k33 = np.sqrt(k3 ** 2 - kt ** 2)

    mu1 = (P * k1 ** 2 - w ** 2 * rho11) / (w ** 2 * rho12 - Q * k1 ** 2)
    mu2 = (P * k2 ** 2 - w ** 2 * rho11) / (w ** 2 * rho12 - Q * k2 ** 2)
    mu3 = -rho12 / rho22

    D1 = (P + Q * mu1) * k1 ** 2 - 2 * N * kt ** 2
    D2 = (P + Q * mu2) * k2 ** 2 - 2 * N * kt ** 2
    E1 = (R * mu1 + Q) * k1 ** 2
    E2 = (R * mu2 + Q) * k2 ** 2

    Taux = np.zeros((6, 6, len(w)), dtype=np.complex128)
    Lambda = np.zeros((6, 6, len(w)), dtype=np.complex128)

    for i in range(len(w)):
        Taux[:, :, i] = np.array([
            [w[i]*kt[i],  w[i]*kt[i],  w[i]*kt[i],  w[i]*kt[i], -w[i]*k33[i],  w[i]*k33[i]],
            [w[i]*k13[i], -w[i]*k13[i], w[i]*k23[i], -w[i]*k23[i], w[i]*kt[i], w[i]*kt[i]],
            [w[i]*k13[i]*mu1[i], -w[i]*k13[i]*mu1[i], w[i]*k23[i]*mu2[i], -w[i]*k23[i]*mu2[i], w[i]*kt[i]*mu3, w[i]*kt[i]*mu3],
            [-D1[i], -D1[i], -D2[i], -D2[i], -2*N*k33[i]*kt[i], 2*N*k33[i]*kt[i]],
            [-2*N*kt[i]*k13[i], 2*N*kt[i]*k13[i], -2*N*kt[i]*k23[i], 2*N*kt[i]*k23[i], N*(k33[i]**2 - kt[i]**2), N*(k33[i]**2 - kt[i]**2)],
            [-E1[i], -E1[i], -E2[i], -E2[i], 0, 0]
        ])

        Alpha = np.array([
            -1j * k13[i], 1j * k13[i], -1j * k23[i],
            1j * k23[i], -1j * k33[i], 1j * k33[i]
        ])
        Lambda[:, :, i] = np.diag(np.exp(Alpha * -d))

    return Taux, Lambda