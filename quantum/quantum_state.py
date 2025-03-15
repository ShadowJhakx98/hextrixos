import numpy as np
import scipy.sparse as sparse

class QuantumState:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.state = sparse.csr_matrix((1, 2**num_qubits), dtype=np.complex128)
        self.state[0, 0] = 1  # Initialize to |0...0> state

    def get_vector(self) -> np.ndarray:
        return self.state.toarray().flatten()

    def set_vector(self, vector: np.ndarray):
        if vector.shape != (2**self.num_qubits,):
            raise ValueError(f"Vector shape mismatch. Expected {2**self.num_qubits}, got {vector.shape[0]}")
        self.state = sparse.csr_matrix(vector.reshape(1, -1))

    def normalize(self):
        norm = np.linalg.norm(self.state.data)
        self.state.data /= norm

    def apply_operator(self, operator: sparse.csr_matrix):
        self.state = operator.dot(self.state.T).T
        self.normalize()
