import numpy as np
import scipy.sparse as sparse

class QuantumErrorModel:
    def __init__(self, error_rate: float):
        self.error_rate = error_rate

    def apply_noise(self, state):
        for i in range(state.num_qubits):
            if np.random.random() < self.error_rate:
                random_gate = np.random.choice(['X', 'Y', 'Z'])
                operator = {
                    'X': sparse.csr_matrix([[0, 1], [1, 0]]),
                    'Y': sparse.csr_matrix([[0, -1j], [1j, 0]]),
                    'Z': sparse.csr_matrix([[1, 0], [0, -1]])
                }[random_gate]
                state.apply_operator(operator)
