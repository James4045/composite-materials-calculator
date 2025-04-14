import numpy as np

def merge_layer(B1_pos, B1_neg, B2_pos, B2_neg, Phi, Lambda):
    N = Phi.shape[0]
    row_st = B1_pos.shape[0]
    col_st = B1_pos.shape[1]
    col_ed = col_st + N

    # Construct big matrix A
    N1 = row_st + B2_neg.shape[0]
    N2 = col_st + N + B2_neg.shape[1]
    A = np.zeros((N1, N2), dtype=np.complex128)

    # Fill A blockwise
    A[:row_st, :col_st] = B1_pos
    A[:row_st, col_st:col_ed] = -B1_neg @ Phi @ Lambda
    A[row_st:, col_st:col_ed] = B2_pos @ Phi
    A[row_st:, col_ed:] = -B2_neg

    # Elimination
    A_inv = A[:N, col_st:col_ed]
    A_BC = A[N:, col_st:col_ed] @ np.linalg.inv(A_inv) @ A[:N, :]

    # Compute updated BC matrices
    B1_pos_star = A[N:, :col_st] - A_BC[:, :col_st]
    B2_neg_star = -(A[N:, col_ed:] - A_BC[:, col_ed:])

    return B1_pos_star, B2_neg_star