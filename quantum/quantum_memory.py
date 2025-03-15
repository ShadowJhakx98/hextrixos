class QuantumMemory:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.memory = []

    def store(self, state):
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)
        self.memory.append(state)

    def retrieve(self, index: int):
        if index < 0 or index >= len(self.memory):
            raise IndexError("Index out of range.")
        return self.memory[index]

    def clear(self):
        self.memory.clear()

    def list_memory(self):
        return [str(state) for state in self.memory]

    def size(self):
        return len(self.memory)
