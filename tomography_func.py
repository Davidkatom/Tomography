import numpy as np
from qiskit.aqua.utils import tensorproduct


def tomography_2q(results, shots):
    counts = [1]
    identity = np.array([[1, 0], [0, 1]])
    sigma_x = np.array([[0, 1], [1, 0]])
    sigma_y = np.array([[0, -1j], [1j, 0]])
    sigma_z = np.array([[1, 0], [0, -1]])
    sigmas = [identity, sigma_x, sigma_y, sigma_z]
    for j in range(3):
        r = ( results[j].get('00', 0)) + results[j].get('01', 0) - results[j].get('10', 0) - results[j].get('11', 0)
        r = r + results[j + 3].get('00', 0) + results[j + 3].get('01', 0) - results[j + 3].get('10', 0) - results[
            j + 3].get('11', 0)
        r = r + results[j + 6].get('00', 0) + results[j + 6].get('01', 0) - results[j + 6].get('10', 0) - results[
            j + 6].get('11', 0)
        counts.append(r / (shots * 3))
    itr = 0
    j = 0
    for i in range(len(results) + 3):
        if i % 4 == 0:
            r = +results[j].get('00', 0) - results[j].get('01', 0) + results[j].get('10', 0) - results[j].get('11', 0)
            r = r + results[j + 1].get('00', 0) - results[j + 1].get('01', 0) + results[j + 1].get('10', 0) - results[
                j + 1].get('11', 0)
            r = r + results[j + 2].get('00', 0) - results[j + 2].get('01', 0) + results[j + 2].get('10', 0) - results[
                j + 2].get('11', 0)
            counts.append(r / (shots * 3))
            j = j+3
        else:
            counts.append(
                (results[itr].get('00', 0) - results[itr].get('01', 0) - results[itr].get('10', 0) + results[itr].get(
                    '11', 0)) / shots)
            itr += 1

    rho2 = np.zeros((4, 4))
    itr = 0
    for i in range(len(sigmas)):
        for j in range(len(sigmas)):
            rho2 = rho2 + tensorproduct(sigmas[j], sigmas[i]) * (counts[itr]*0.25)
            itr += 1
    print(counts)
    return rho2
