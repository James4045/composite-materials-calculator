import numpy as np

def one_layer_pred(B1_pos, B1_neg, B2_pos, B2_neg, Phi, Lambda):
    N = B1_pos.shape[1] + B1_neg.shape[1]
    B1_h = B1_pos.shape[0]

    Lambda_inv = np.linalg.inv(Lambda)

    A = np.zeros((N, N), dtype=np.complex128)
    A[:B1_h, :2] = B1_pos
    A[:B1_h, 2:] = -B1_neg @ Phi
    A[B1_h:, 2:] = B2_pos @ Phi @ Lambda_inv

    A_inv = np.linalg.inv(A)

    # 추출할 열 개수 = B2_neg.shape[0] (ex: 3)
    num_output = B2_neg.shape[0]
    TM_block = A_inv[:2, -num_output:]  # (2, 3)
    TM = TM_block @ B2_neg              # (2, 2)

    return TM
