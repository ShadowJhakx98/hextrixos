class QuantumOptimizer:
    def __init__(self, cost_function, num_params: int):
        self.cost_function = cost_function
        self.num_params = num_params

    def optimize(self, initial_params, iterations: int = 100):
        params = initial_params
        for _ in range(iterations):
            gradient = self._compute_gradient(params)
            params = [p - 0.01 * g for p, g in zip(params, gradient)]
        return params

    def _compute_gradient(self, params):
        epsilon = 1e-6
        gradient = []
        for i in range(self.num_params):
            params_plus = params.copy()
            params_plus[i] += epsilon
            params_minus = params.copy()
            params_minus[i] -= epsilon
            gradient.append((self.cost_function(params_plus) - self.cost_function(params_minus)) / (2 * epsilon))
        return gradient
