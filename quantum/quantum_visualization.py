import matplotlib.pyplot as plt
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector

def visualize_state(state):
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(state)), np.abs(state)**2)
    plt.title("Quantum State Probabilities")
    plt.xlabel("Basis State")
    plt.ylabel("Probability")
    plt.show()

def visualize_bloch_sphere(state):
    qiskit_state = Statevector(state)
    plot_bloch_multivector(qiskit_state)
    plt.show()
