import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import List, Dict, Tuple, Optional, Union, Callable

class NeuronGroup:
    """Represents a group of neurons with similar functional properties."""
    
    def __init__(self, n_neurons: int, 
                 threshold: float = 0.5, 
                 refractory_period: float = 0.1,
                 decay_constant: float = 0.95):
        """
        Initialize a group of neurons.
        
        Parameters:
        -----------
        n_neurons : int
            Number of neurons in the group
        threshold : float
            Firing threshold for neurons
        refractory_period : float
            Refractory period after firing (in seconds)
        decay_constant : float
            Membrane potential decay constant
        """
        self.n_neurons = n_neurons
        self.threshold = threshold
        self.refractory_period = refractory_period
        self.decay_constant = decay_constant
        
        # State variables
        self.membrane_potentials = np.zeros(n_neurons)
        self.refractory_timers = np.zeros(n_neurons)
        self.firing_history = np.zeros((100, n_neurons))  # Store last 100 timesteps
        self.timestep = 0
        
    def update(self, inputs: np.ndarray, dt: float = 0.001) -> np.ndarray:
        """
        Update neuron states for one timestep.
        
        Parameters:
        -----------
        inputs : np.ndarray
            Input current for each neuron
        dt : float
            Time step size in seconds
            
        Returns:
        --------
        np.ndarray : Spike output (0 or 1) for each neuron
        """
        # Decrease refractory timers
        self.refractory_timers = np.maximum(0, self.refractory_timers - dt)
        
        # Update membrane potentials for non-refractory neurons
        non_refractory = self.refractory_timers <= 0
        self.membrane_potentials[non_refractory] = (
            self.decay_constant * self.membrane_potentials[non_refractory] + 
            inputs[non_refractory]
        )
        
        # Determine which neurons fire
        firing = np.logical_and(
            self.membrane_potentials >= self.threshold,
            non_refractory
        )
        
        # Reset membrane potentials and set refractory timers for firing neurons
        self.membrane_potentials[firing] = 0
        self.refractory_timers[firing] = self.refractory_period
        
        # Update firing history
        self.firing_history[self.timestep % 100] = firing
        self.timestep += 1
        
        return firing.astype(float)
    
    def get_firing_rate(self, window: int = 100) -> np.ndarray:
        """
        Calculate firing rate over the specified window of timesteps.
        
        Parameters:
        -----------
        window : int
            Number of timesteps to consider
            
        Returns:
        --------
        np.ndarray : Firing rate for each neuron
        """
        actual_window = min(window, self.timestep)
        if actual_window == 0:
            return np.zeros(self.n_neurons)
        
        # Calculate the indices of the history to use
        indices = [(self.timestep - i - 1) % 100 for i in range(actual_window)]
        
        # Sum the firing history over the window
        return np.mean(self.firing_history[indices], axis=0)


class SynapticConnection:
    """Represents synaptic connections between neuron groups."""
    
    def __init__(self, 
                 pre_group: NeuronGroup, 
                 post_group: NeuronGroup,
                 connectivity_type: str = 'full',
                 synapse_strength: float = 0.1,
                 plasticity_enabled: bool = False,
                 learning_rate: float = 0.01):
        """
        Initialize synaptic connections between two neuron groups.
        
        Parameters:
        -----------
        pre_group : NeuronGroup
            Source neuron group
        post_group : NeuronGroup
            Target neuron group
        connectivity_type : str
            Type of connectivity ('full', 'random', or 'sparse')
        synapse_strength : float
            Initial strength of synaptic connections
        plasticity_enabled : bool
            Whether to enable synaptic plasticity
        learning_rate : float
            Learning rate for plasticity
        """
        self.pre_group = pre_group
        self.post_group = post_group
        self.plasticity_enabled = plasticity_enabled
        self.learning_rate = learning_rate
        
        # Initialize weight matrix
        if connectivity_type == 'full':
            self.weights = synapse_strength * np.ones((pre_group.n_neurons, post_group.n_neurons))
        elif connectivity_type == 'random':
            self.weights = synapse_strength * np.random.rand(pre_group.n_neurons, post_group.n_neurons)
        elif connectivity_type == 'sparse':
            self.weights = np.zeros((pre_group.n_neurons, post_group.n_neurons))
            # Connect each post-synaptic neuron to ~20% of pre-synaptic neurons
            for j in range(post_group.n_neurons):
                mask = np.random.choice([0, 1], size=(pre_group.n_neurons,), p=[0.8, 0.2])
                self.weights[:, j] = synapse_strength * mask
        else:
            raise ValueError(f"Unknown connectivity type: {connectivity_type}")
        
        # For STDP
        self.pre_trace = np.zeros(pre_group.n_neurons)
        self.post_trace = np.zeros(post_group.n_neurons)
        
    def propagate(self, pre_activity: np.ndarray) -> np.ndarray:
        """
        Propagate activity from pre to post synaptic neurons.
        
        Parameters:
        -----------
        pre_activity : np.ndarray
            Activity of pre-synaptic neurons
            
        Returns:
        --------
        np.ndarray : Input current for post-synaptic neurons
        """
        return np.dot(pre_activity, self.weights)
    
    def update_weights(self, pre_spikes: np.ndarray, post_spikes: np.ndarray, dt: float = 0.001):
        """
        Update synaptic weights according to spike-timing-dependent plasticity.
        
        Parameters:
        -----------
        pre_spikes : np.ndarray
            Spike activity of pre-synaptic neurons
        post_spikes : np.ndarray
            Spike activity of post-synaptic neurons
        dt : float
            Time step size in seconds
        """
        if not self.plasticity_enabled:
            return
            
        # Update traces
        self.pre_trace = 0.95 * self.pre_trace + pre_spikes
        self.post_trace = 0.95 * self.post_trace + post_spikes
        
        # Compute weight updates
        for i in range(self.pre_group.n_neurons):
            for j in range(self.post_group.n_neurons):
                # LTP: If pre-synaptic neuron fires before post-synaptic neuron
                if pre_spikes[i] > 0:
                    self.weights[i, j] += self.learning_rate * self.post_trace[j]
                
                # LTD: If post-synaptic neuron fires before pre-synaptic neuron
                if post_spikes[j] > 0:
                    self.weights[i, j] -= self.learning_rate * self.pre_trace[i]
        
        # Ensure weights stay in reasonable range
        self.weights = np.clip(self.weights, 0, 1)


class IntegratedInformationCalculator:
    """Calculates integrated information (Φ) for a neural system."""
    
    def __init__(self, temporal_window: int = 10):
        """
        Initialize the calculator.
        
        Parameters:
        -----------
        temporal_window : int
            Number of timesteps to consider for integration
        """
        self.temporal_window = temporal_window
    
    def calculate_mutual_information(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Calculate mutual information between two variables.
        
        Parameters:
        -----------
        X : np.ndarray
            First variable
        Y : np.ndarray
            Second variable
            
        Returns:
        --------
        float : Mutual information I(X;Y)
        """
        # Binarize data for simplicity
        X_bin = (X > 0.5).astype(int)
        Y_bin = (Y > 0.5).astype(int)
        
        # Joint histogram
        xy_hist = np.zeros((2, 2))
        for i in range(len(X_bin)):
            xy_hist[X_bin[i], Y_bin[i]] += 1
        xy_hist /= len(X_bin)
        
        # Marginal histograms
        x_hist = np.sum(xy_hist, axis=1)
        y_hist = np.sum(xy_hist, axis=0)
        
        # Calculate mutual information
        mutual_info = 0
        for i in range(2):
            for j in range(2):
                if xy_hist[i, j] > 0:
                    mutual_info += xy_hist[i, j] * np.log2(xy_hist[i, j] / (x_hist[i] * y_hist[j]))
        
        return mutual_info
    
    def calculate_phi(self, activity_matrix: np.ndarray) -> float:
        """
        Calculate integrated information (Φ) based on activity matrix.
        
        Parameters:
        -----------
        activity_matrix : np.ndarray
            Matrix of neural activity over time (timesteps × neurons)
            
        Returns:
        --------
        float : Integrated information (Φ)
        """
        n_timesteps, n_neurons = activity_matrix.shape
        
        if n_timesteps < 2:
            return 0.0
        
        # Calculate whole system mutual information
        whole_mi = self.calculate_mutual_information(
            activity_matrix[:-1].flatten(), 
            activity_matrix[1:].flatten()
        )
        
        # Try different partitions (here simplified to just bipartitions)
        min_partition_difference = float('inf')
        
        for k in range(1, n_neurons):
            # Create bipartition
            part1 = activity_matrix[:, :k]
            part2 = activity_matrix[:, k:]
            
            # Calculate mutual information for each part
            part1_mi = self.calculate_mutual_information(
                part1[:-1].flatten(), 
                part1[1:].flatten()
            )
            
            part2_mi = self.calculate_mutual_information(
                part2[:-1].flatten(), 
                part2[1:].flatten()
            )
            
            # Difference between whole and sum of parts
            partition_difference = whole_mi - (part1_mi + part2_mi)
            min_partition_difference = min(min_partition_difference, partition_difference)
        
        # Φ is the minimum information loss across all partitions
        phi = max(0, min_partition_difference)
        return phi


class PredictiveProcessor:
    """Implements predictive processing framework."""
    
    def __init__(self, 
                 n_neurons: int, 
                 n_layers: int = 3, 
                 learning_rate: float = 0.01):
        """
        Initialize predictive processing system.
        
        Parameters:
        -----------
        n_neurons : int
            Number of neurons per layer
        n_layers : int
            Number of hierarchical layers
        learning_rate : float
            Learning rate for prediction error minimization
        """
        self.n_neurons = n_neurons
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        
        # Create layers of prediction units
        self.predictions = [np.zeros(n_neurons) for _ in range(n_layers)]
        self.prediction_errors = [np.zeros(n_neurons) for _ in range(n_layers)]
        
        # Top-down and bottom-up connection weights
        self.top_down_weights = [
            np.random.randn(n_neurons, n_neurons) * 0.1 for _ in range(n_layers-1)
        ]
        self.bottom_up_weights = [
            np.random.randn(n_neurons, n_neurons) * 0.1 for _ in range(n_layers-1)
        ]
        
        # Precision of predictions at each layer (inverse variance)
        self.precisions = [np.ones(n_neurons) for _ in range(n_layers)]
    
    def update(self, sensory_input: np.ndarray, n_iterations: int = 10) -> List[np.ndarray]:
        """
        Update the predictive processing hierarchy based on sensory input.
        
        Parameters:
        -----------
        sensory_input : np.ndarray
            Input to the lowest layer
        n_iterations : int
            Number of iterations for prediction error minimization
            
        Returns:
        --------
        List[np.ndarray] : Prediction errors at each layer
        """
        # Set the input as prediction for the bottom layer
        self.predictions[0] = sensory_input
        
        for _ in range(n_iterations):
            # Bottom-up pass: propagate prediction errors upward
            for l in range(self.n_layers - 1):
                # Compute prediction error at this layer
                if l == 0:
                    # For the bottom layer, error is difference from sensory input
                    self.prediction_errors[l] = sensory_input - self.predictions[l]
                else:
                    # For higher layers, error is difference from prediction generated by layer above
                    top_down_prediction = np.dot(self.predictions[l+1], self.top_down_weights[l])
                    self.prediction_errors[l] = self.predictions[l] - top_down_prediction
                
                # Update predictions at the layer above based on bottom-up error
                bottom_up_influence = np.dot(self.prediction_errors[l], self.bottom_up_weights[l])
                self.predictions[l+1] += self.learning_rate * bottom_up_influence * self.precisions[l+1]
            
            # Top-down pass: adjust predictions based on higher-level context
            for l in range(self.n_layers - 1, 0, -1):
                # Compute error in predictions from perspective of layer above
                if l < self.n_layers - 1:
                    top_down_prediction = np.dot(self.predictions[l+1], self.top_down_weights[l])
                    top_down_error = self.predictions[l] - top_down_prediction
                else:
                    top_down_error = np.zeros(self.n_neurons)
                
                # Update predictions at this layer
                self.predictions[l] -= self.learning_rate * top_down_error * self.precisions[l]
                
                # Propagate updated predictions to layer below
                if l > 0:
                    bottom_up_prediction = np.dot(self.predictions[l], self.top_down_weights[l-1])
                    self.predictions[l-1] = bottom_up_prediction
        
        # Update connection weights based on prediction errors
        for l in range(self.n_layers - 1):
            # Update top-down weights
            delta_td = np.outer(self.predictions[l+1], self.prediction_errors[l])
            self.top_down_weights[l] += self.learning_rate * delta_td
            
            # Update bottom-up weights
            delta_bu = np.outer(self.prediction_errors[l], self.predictions[l+1])
            self.bottom_up_weights[l] += self.learning_rate * delta_bu
        
        return self.prediction_errors
    
    def update_precisions(self, decay_factor: float = 0.99):
        """
        Update precision estimates based on prediction errors.
        
        Parameters:
        -----------
        decay_factor : float
            Factor for exponential decay of precision estimates
        """
        for l in range(self.n_layers):
            # Precision decreases (variance increases) with large prediction errors
            error_magnitude = np.abs(self.prediction_errors[l])
            precision_update = 1.0 / (1.0 + error_magnitude)
            
            # Update precision with decay
            self.precisions[l] = decay_factor * self.precisions[l] + (1 - decay_factor) * precision_update
            
            # Ensure precisions stay in reasonable range
            self.precisions[l] = np.clip(self.precisions[l], 0.1, 10.0)


class IntegratedFramework:
    """
    Integrates neurophysiological modeling, information theory, and predictive processing
    to simulate neural dynamics with cognitive constraints.
    """
    
    def __init__(self, 
                 n_input: int = 10, 
                 n_hidden: int = 20, 
                 n_output: int = 5,
                 n_layers: int = 3,
                 dt: float = 0.001):
        """
        Initialize the integrated framework.
        
        Parameters:
        -----------
        n_input : int
            Number of input neurons
        n_hidden : int
            Number of hidden neurons per layer
        n_output : int
            Number of output neurons
        n_layers : int
            Number of hierarchical layers
        dt : float
            Simulation time step in seconds
        """
        self.dt = dt
        self.time = 0.0
        
        # Create neuron groups
        self.input_layer = NeuronGroup(n_input)
        self.hidden_layers = [NeuronGroup(n_hidden) for _ in range(n_layers)]
        self.output_layer = NeuronGroup(n_output)
        
        # Create synaptic connections
        self.input_to_hidden = SynapticConnection(
            self.input_layer, 
            self.hidden_layers[0], 
            connectivity_type='random',
            plasticity_enabled=True
        )
        
        self.hidden_connections = []
        for i in range(n_layers - 1):
            conn = SynapticConnection(
                self.hidden_layers[i],
                self.hidden_layers[i+1],
                connectivity_type='sparse',
                plasticity_enabled=True
            )
            self.hidden_connections.append(conn)
        
        self.hidden_to_output = SynapticConnection(
            self.hidden_layers[-1],
            self.output_layer,
            connectivity_type='full',
            plasticity_enabled=True
        )
        
        # Create integrated information calculator
        self.phi_calculator = IntegratedInformationCalculator()
        
        # Create predictive processor
        self.predictor = PredictiveProcessor(n_hidden, n_layers)
        
        # Performance metrics
        self.phi_history = []
        self.prediction_error_history = []
        self.response_time_history = []
        
        # Activity history for analysis
        self.activity_history = {
            'input': np.zeros((0, n_input)),
            'hidden': [np.zeros((0, n_hidden)) for _ in range(n_layers)],
            'output': np.zeros((0, n_output))
        }
    
    def step(self, input_data: np.ndarray) -> np.ndarray:
        """
        Perform one simulation step.
        
        Parameters:
        -----------
        input_data : np.ndarray
            Input data for the current timestep
            
        Returns:
        --------
        np.ndarray : Output activity
        """
        # Update time
        self.time += self.dt
        
        # Process input through neural network
        input_activity = self.input_layer.update(input_data, self.dt)
        
        # Forward propagation through hidden layers
        hidden_input = self.input_to_hidden.propagate(input_activity)
        hidden_activities = []
        
        first_hidden_activity = self.hidden_layers[0].update(hidden_input, self.dt)
        hidden_activities.append(first_hidden_activity)
        
        for i, conn in enumerate(self.hidden_connections):
            next_input = conn.propagate(hidden_activities[i])
            next_activity = self.hidden_layers[i+1].update(next_input, self.dt)
            hidden_activities.append(next_activity)
        
        # Output layer
        output_input = self.hidden_to_output.propagate(hidden_activities[-1])
        output_activity = self.output_layer.update(output_input, self.dt)
        
        # Update synaptic weights (STDP)
        self.input_to_hidden.update_weights(input_activity, hidden_activities[0], self.dt)
        
        for i, conn in enumerate(self.hidden_connections):
            conn.update_weights(hidden_activities[i], hidden_activities[i+1], self.dt)
        
        self.hidden_to_output.update_weights(hidden_activities[-1], output_activity, self.dt)
        
        # Update predictive processing
        prediction_errors = self.predictor.update(input_data)
        mean_prediction_error = np.mean([np.mean(np.abs(err)) for err in prediction_errors])
        self.prediction_error_history.append(mean_prediction_error)
        
        # Store activity history
        self.activity_history['input'] = np.vstack([self.activity_history['input'], input_activity[np.newaxis, :]])
        for i, act in enumerate(hidden_activities):
            self.activity_history['hidden'][i] = np.vstack([self.activity_history['hidden'][i], act[np.newaxis, :]])
        self.activity_history['output'] = np.vstack([self.activity_history['output'], output_activity[np.newaxis, :]])
        
        # Calculate integrated information if enough data is available
        if len(self.activity_history['hidden'][0]) >= 10:
            phi = self.phi_calculator.calculate_phi(self.activity_history['hidden'][0][-10:])
            self.phi_history.append(phi)
        
        return output_activity
    
    def simulate(self, 
                input_function: Callable[[float], np.ndarray], 
                duration: float = 1.0) -> Dict[str, Union[List[float], np.ndarray]]:
        """
        Run simulation for a specified duration.
        
        Parameters:
        -----------
        input_function : Callable
            Function that generates input data given time
        duration : float
            Simulation duration in seconds
            
        Returns:
        --------
        Dict : Simulation results
        """
        n_steps = int(duration / self.dt)
        outputs = []
        
        for _ in range(n_steps):
            # Generate input
            input_data = input_function(self.time)
            
            # Simulate one step
            output = self.step(input_data)
            outputs.append(output)
        
        # Compile results
        results = {
            'outputs': np.array(outputs),
            'phi_history': self.phi_history,
            'prediction_error_history': self.prediction_error_history,
            'activity_history': self.activity_history
        }
        
        return results
    
    def analyze_performance(self) -> Dict[str, float]:
        """
        Analyze system performance metrics.
        
        Returns:
        --------
        Dict : Performance metrics
        """
        if not self.phi_history:
            return {'message': 'No simulation data available for analysis'}
        
        # Calculate metrics
        mean_phi = np.mean(self.phi_history)
        max_phi = np.max(self.phi_history)
        mean_prediction_error = np.mean(self.prediction_error_history)
        
        # Stability metrics
        phi_stability = 1.0 / (1.0 + np.var(self.phi_history))
        prediction_stability = 1.0 / (1.0 + np.var(self.prediction_error_history))
        
        # Integration metrics
        integration_score = mean_phi / (1.0 + mean_prediction_error)
        
        return {
            'mean_phi': mean_phi,
            'max_phi': max_phi,
            'mean_prediction_error': mean_prediction_error,
            'phi_stability': phi_stability,
            'prediction_stability': prediction_stability,
            'integration_score': integration_score
        }
    
    def visualize_results(self, results: Dict[str, Union[List[float], np.ndarray]]):
        """
        Visualize simulation results.
        
        Parameters:
        -----------
        results : Dict
            Simulation results from the simulate method
        """
        plt.figure(figsize=(15, 12))
        
        # Plot 1: Phi over time
        plt.subplot(3, 2, 1)
        plt.plot(results['phi_history'])
        plt.title('Integrated Information (Φ) Over Time')
        plt.xlabel('Timestep')
        plt.ylabel('Φ')
        
        # Plot 2: Prediction errors over time
        plt.subplot(3, 2, 2)
        plt.plot(results['prediction_error_history'])
        plt.title('Prediction Error Over Time')
        plt.xlabel('Timestep')
        plt.ylabel('Mean Prediction Error')
        
        # Plot 3: Neural activity heatmap (input layer)
        plt.subplot(3, 2, 3)
        plt.imshow(results['activity_history']['input'].T, aspect='auto', cmap='viridis')
        plt.title('Input Layer Activity')
        plt.xlabel('Timestep')
        plt.ylabel('Neuron Index')
        plt.colorbar(label='Activity')
        
        # Plot 4: Neural activity heatmap (first hidden layer)
        plt.subplot(3, 2, 4)
        plt.imshow(results['activity_history']['hidden'][0].T, aspect='auto', cmap='viridis')
        plt.title('First Hidden Layer Activity')
        plt.xlabel('Timestep')
        plt.ylabel('Neuron Index')
        plt.colorbar(label='Activity')
        
        # Plot 5: Neural activity heatmap (output layer)
        plt.subplot(3, 2, 5)
        plt.imshow(results['activity_history']['output'].T, aspect='auto', cmap='viridis')
        plt.title('Output Layer Activity')
        plt.xlabel('Timestep')
        plt.ylabel('Neuron Index')
        plt.colorbar(label='Activity')
        
        # Plot 6: Correlation between Phi and prediction error
        plt.subplot(3, 2, 6)
        if len(results['phi_history']) > 0 and len(results['prediction_error_history']) > 0:
            min_len = min(len(results['phi_history']), len(results['prediction_error_history']))
            plt.scatter(results['phi_history'][:min_len], results['prediction_error_history'][:min_len])
            plt.title('Φ vs Prediction Error')
            plt.xlabel('Integrated Information (Φ)')
            plt.ylabel('Prediction Error')
            
            # Add trend line
            if min_len > 1:
                z = np.polyfit(results['phi_history'][:min_len], results['prediction_error_history'][:min_len], 1)
                p = np.poly1d(z)
                plt.plot(results['phi_history'][:min_len], p(results['phi_history'][:min_len]), "r--")
        
        plt.tight_layout()
        plt.show()


# Example usage
def demo():
    # Create the integrated framework
    framework = IntegratedFramework(n_input=8, n_hidden=16, n_output=4, n_layers=3)
    
    # Define an input function (simple sine wave)
    def input_generator(t):
        base = 0.5 * (1 + np.sin(2 * np.pi * t))
        noise = 0.1 * np.random.randn(8)
        return base + noise
    
    # Run simulation
    print("Running simulation...")
    results = framework.simulate(input_generator, duration=0.5)
    
    # Analyze performance
    print("\nPerformance metrics:")
    metrics = framework.analyze_performance()
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    
    # Visualize results
    framework.visualize_results(results)


if __name__ == "__main__":
    demo()
