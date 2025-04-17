import numpy as np

def bc_matrix(upper, lower, phi=None, phi2=None):
    # poro and air
    if upper == 'poro' and lower == 'fluid':
        B_pos = np.array([[0,       0,   0, 1, 0, 0],
                          [0,       0,   0, 0, 0, 1],
                          [0, 1 - phi, phi, 0, 0, 0],
                          [0,       0,   0, 0, 1, 0]])
        B_neg = np.array([[-(1 - phi), 0],
                          [      -phi, 0],
                          [         0, 1],
                          [         0, 0]])
    elif upper == 'fluid' and lower == 'poro':
        B_neg = np.array([[0,       0,   0, 1, 0, 0],
                          [0,       0,   0, 0, 0, 1],
                          [0, 1 - phi, phi, 0, 0, 0],
                          [0,       0,   0, 0, 1, 0]])
        B_pos = np.array([[-(1 - phi), 0],
                          [      -phi, 0],
                          [         0, 1],
                          [         0, 0]])

    # stiff panel and air
    elif upper == 'stiff panel' and lower == 'fluid':
        B_pos = np.array([
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        B_neg = np.array([
            [0, 1],
            [1, 0],
            [0, 0]
        ])
    elif upper == 'fluid' and lower == 'stiff panel':
        B_neg = np.array([
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        B_pos = np.array([
            [0, 1],
            [1, 0],
            [0, 0]
        ])

    # plastic and air
    elif upper == 'plastic' and lower == 'fluid':
        B_pos = np.array([
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        B_neg = np.array([
            [0, 1],
            [-1, 0],
            [0, 0]
        ])
    elif upper == 'fluid' and lower == 'plastic':
        B_neg = np.array([
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        B_pos = np.array([
            [0, 1],
            [-1, 0],
            [0, 0]
        ])

    # poro and stiff panel
    elif upper == 'poro' and lower == 'stiff panel':
        B_pos = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 0]
        ])
        B_neg = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0,-1, 0],
            [0, 0, 0, 1]
        ])
    elif upper == 'stiff panel' and lower == 'poro':
        B_neg = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 0]
        ])
        B_pos = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0,-1, 0],
            [0, 0, 0, 1]
        ])

    # poro and plastic
    elif upper == 'poro' and lower == 'plastic':
        B_pos = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 0]
        ])
        B_neg = np.array([
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    elif upper == 'plastic' and lower == 'poro':
        B_neg = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 0]
        ])
        B_pos = np.array([
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    # plastic and stiff panel
    elif upper == 'plastic' and lower == 'stiff panel':
        B_pos = np.array([
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0]
        ])
        B_neg = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0,-1, 0],
            [0, 0, 0, 1]
        ])
    elif upper == 'stiff panel' and lower == 'plastic':
        B_neg = np.array([
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0]
        ])
        B_pos = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0,-1, 0],
            [0, 0, 0, 1]
        ])


    # same type layer
    elif upper == 'poro' and lower == 'poro':
        B_pos = np.eye(6)
        B_neg = np.eye(6)
        B_pos[2, 1] = 1 - phi
        B_neg[2, 1] = 1 - phi2
        B_pos[2, 2] = phi
        B_neg[2, 2] = phi2
        B_pos[3, 5] = 1
        B_neg[3, 5] = 1
        B_pos[5, 5] = 1 / phi
        B_neg[5, 5] = 1 / phi2

    elif upper == 'stiff panel' and lower == 'stiff panel':
        B_pos = np.eye(4)
        B_neg = np.eye(4)

    elif upper == 'plastic' and lower == 'plastic':
        B_pos = np.eye(4)
        B_neg = np.eye(4)

    elif upper == 'fluid' and lower == 'fluid':
        B_pos = np.eye(2)
        B_neg = np.eye(2)

    else:
        raise ValueError(f"Unsupported interface combination: {upper} - {lower} (phi={phi})")

    return B_pos, B_neg