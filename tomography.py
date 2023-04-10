"""
Create a density matrix based on the histogram, measure fidelity and purity.
"""
import numpy as np
import random
from qiskit.aqua.utils import tensorproduct
import copy



def __advance_index(indexes, size, i):
    """
    Advance an N dimensional index.
    :param indexes: list of indexes
    :param size: Maximum index
    :param i: Index to advance
    :return: New list
    """
    if i == -1:
        return
    indexes[i] = indexes[i] + 1
    if indexes[i] == size:
        indexes[i] = 0
        __advance_index(indexes, size, i - 1)


def get_density_matrix(results, reduce):
    """
    Driver Method
    :param results: Qiskit Counts obj
    :return: Density Matrix
    """
    print(reduce)
    results_copy = copy.deepcopy(results)
    randomlist = random.sample(range(1, 728), reduce)
    for i in randomlist:
        for key in results_copy[i].keys():
            results_copy[i][key] = 0


    shots = sum(results_copy[0].values())
    size = 4
    array_dim = tuple([size] * len(list(results_copy[0].keys())[0]))
    array = np.zeros(array_dim)
    dims = len(list(results_copy[0].keys())[0])
    indexes = [0] * dims

    for cell in array.flat:
        array[(tuple(indexes))] = __calc_cell(results_copy, indexes, size, shots, [])
        __advance_index(indexes, size, dims - 1)
    return __get_matrix(array, size, dims, reduce)


def __calc_cell(results, indexes, size, shots, ignore):
    """
    Calculate the corresponding coefficient.
    :param results: Qiskit Result obj
    :param indexes: List of indexes
    :param size: Maximum index
    :param shots: Shots
    :param ignore: Indexes to ignore
    :return: Coefficient
    """

    options = [a for a in range(1, size)]
    cell = 0
    mult = 1
    if sum(indexes) == 0:
        return 1
    if 0 not in indexes:
        index = __get_flat_index(indexes, size)
        for x, y in results[index].items():
            j = 0
            mult = 1
            rev_x = x[::-1]
            for char in rev_x:
                j += 1
                if j - 1 in ignore:
                    continue
                mult *= pow(-1, int(char))
            cell = cell + int(mult * y)
        cell = cell / shots
        return cell
    else:
        j = 0
        for option in options:
            index_cpy = indexes.copy()
            ig_index = index_cpy.index(0)
            index_cpy[index_cpy.index(0)] = option
            ignore.append(ig_index)
            cell = cell + __calc_cell(results, index_cpy, size, shots, ignore)
            j += 1
        return cell / j


def __get_flat_index(indexes, size):
    """
    Calculates the flat index of the N-dim array.
    :param indexes: List of indexes
    :param size: Maximum Index (4)
    :return: Flat index
    """
    a = 0
    power = len(indexes) - 1
    for i in range(len(indexes)):
        a += (indexes[i] - 1) * pow(size - 1, power)
        power -= 1
    return a


def __get_matrix(array, size, dims, reduce):
    """
    Generates Matrix.
    :param array: N-dim coefficient array
    :param size: Maximum index (4)
    :param dims: array dimensions
    :return: Density matrix
    """
    identity = np.array([[1, 0], [0, 1]])
    sigma_x = np.array([[0, 1], [1, 0]])
    sigma_y = np.array([[0, -1j], [1j, 0]])
    sigma_z = np.array([[1, 0], [0, -1]])
    sigmas = [identity, sigma_x, sigma_y, sigma_z]

    indexes = [0] * dims
    matrix = np.zeros((pow(2, dims), pow(2, dims)))

    j = 0
    array_flat = []
    for cell in array.flat:
        array_flat.append(cell)
        tensor = np.array([1])
        for i in range(len(indexes) - 1, -1, -1):
            tensor = tensorproduct(tensor, sigmas[indexes[i]])
        matrix = np.add(matrix, tensor * cell * (1 / pow(2, len(indexes))))
        __advance_index(indexes, size, dims - 1)
    #abs_array = [-1*np.absolute(a) for a in array_flat]
    #print(np.sort(abs_array))
    #print(list(-1*np.sort(abs_array)))
    return matrix


def calc_purity(matrix):
    """
    Calculates purity: tr(P^2)
    :param matrix: Density matrix
    :return: purity
    """
    return np.trace(np.matmul(matrix, matrix))


def calc_fidelity(matrix, vector):
    """
    Calculate fidelity to a given vector
    :param matrix: Density matrix
    :param vector: State vector
    :return: Fidelity
    """
    return np.vdot(np.dot(vector.conjugate()._data, matrix), vector._data)

