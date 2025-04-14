import numpy as np

def tm_panel(w_array, c0, hp, ms, Dp, D, theta_deg):
    theta = np.radians(theta_deg)
    kx = w_array / c0 * np.sin(theta)
    N = len(w_array)

    Phi = np.zeros((4, 4, N), dtype=np.complex128)
    Lambda = np.zeros((4, 4, N), dtype=np.complex128)

    for i in range(N):
        w = w_array[i]
        k = kx[i]

        C1 = Dp * k**2 - ms * w**2
        C2 = D * k**4 - ms * w**2

        # 전달행렬 직접 구성 (Taux = I)
        T = np.array([
            [1,           -1j * k * hp,                                 0,                0],
            [0,                     1,                                 0,                0],
            [k * hp / (2 * w) * C1, (1 / (1j * w)) * (k**2 * hp**2 / 4 * C1 + C2), 1, 1j * k * hp],
            [C1 / (1j * w),        -k * hp / (2 * w) * C1,              0,                1]
        ])

        # 분해: T = Phi @ Lambda @ Phi^-1
        # 여기선 Phi = I, Lambda = T (사실상 TM 자체)
        Phi[:, :, i] = np.eye(4)
        Lambda[:, :, i] = T

    return Phi, Lambda