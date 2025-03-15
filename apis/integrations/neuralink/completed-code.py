def main():
    """
    Demo function showing the framework in action
    """
    print("Initializing Neural Information Integration Framework...")
    framework = ConsciousnessResearchFramework(input_size=64, hidden_size=32)
    
    print("\nProcessing sample inputs...")
    results = []
    
    # Generate and process sample inputs
    for i in range(20):
        # Create structured input with some patterns
        if i % 5 == 0:
            # Visual-dominant input
            sample_input = np.zeros(64)
            sample_input[:16] = np.random.random(16) * 0.8 + 0.2
        elif i % 5 == 1:
            # Auditory-dominant input
            sample_input = np.zeros(64)
            sample_input[16:32] = np.random.random(16) * 0.8 + 0.2
        elif i % 5 == 2:
            # Language-dominant input
            sample_input = np.zeros(64)
            sample_input[32:48] = np.random.random(16) * 0.8 + 0.2
        elif i % 5 == 3:
            # Executive-dominant input
            sample_input = np.zeros(64)
            sample_input[48:64] = np.random.random(16) * 0.8 + 0.2
        else:
            # Mixed input
            sample_input = np.random.random(64) * 0.5
        
        # Process input and collect results
        result = framework.process_input(sample_input)
        results.append(result)
    
    # Analyze consciousness correlates
    print("\nAnalyzing consciousness correlates...")
    analysis = framework.analyze_consciousness_correlates()
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Mean Phi (Integrated Information): {np.mean([r['phi_value'] for r in results]):.4f}")
    print(f"Mean Awareness Index: {np.mean([r['metrics']['awareness_index'] for r in results]):.4f}")
    print(f"Mean Prediction Error: {np.mean([r['prediction_error'] for r in results]):.4f}")
    
    # Display key findings
    print("\nKey Findings:")
    for finding, value in analysis['key_findings'].items():
        if isinstance(value, list):
            print(f"- {finding}: {', '.join(value)}")
        elif isinstance(value, dict):
            print(f"- {finding}:")
            for k, v in value.items():
                print(f"  - {k}: {v}")
        else:
            print(f"- {finding}: {value}")
    
    # Visualize results
    print("\nGenerating visualizations...")
    visualization_data = framework.visualize_consciousness_metrics()
    
    # Plot time series of key metrics
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.plot(visualization_data['time_series']['phi'])
    plt.title('Integrated Information (Phi)')
    plt.xlabel('Time Step')
    
    plt.subplot(2, 2, 2)
    plt.plot(visualization_data['time_series']['awareness_index'])
    plt.title('Awareness Index')
    plt.xlabel('Time Step')
    
    plt.subplot(2, 2, 3)
    plt.plot(visualization_data['time_series']['workspace_activation'])
    plt.title('Workspace Activation')
    plt.xlabel('Time Step')
    
    plt.subplot(2, 2, 4)
    plt.plot(visualization_data['time_series']['prediction_error'])
    plt.title('Prediction Error')
    plt.xlabel('Time Step')
    
    plt.tight_layout()
    plt.savefig('consciousness_metrics.png')
    print("Visualizations saved to 'consciousness_metrics.png'")
    
    # Create network visualization
    plt.figure(figsize=(10, 8))
    G = nx.DiGraph()
    
    # Add nodes for modules
    for i, module in enumerate(framework.global_workspace.specialist_modules):
        G.add_node(module['name'], size=module['activation']*1000 + 500)
    
    # Add global workspace node
    G.add_node('workspace', size=2000)
    
    # Add edges
    for module in framework.global_workspace.specialist_modules:
        G.add_edge(module['name'], 'workspace', 
                  weight=module['activation'], 
                  width=module['activation']*5)
        
    # Draw network
    pos = nx.spring_layout(G)
    node_sizes = [G.nodes[n]['size'] for n in G.nodes]
    
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, 
            node_color='skyblue', font_weight='bold', 
            edge_color='gray', width=[G.edges[e]['width'] for e in G.edges],
            alpha=0.7)
    
    plt.title('Global Workspace Network Structure')
    plt.savefig('gwt_network.png')
    print("Network visualization saved to 'gwt_network.png'")
    
    print("\nDemo completed successfully.")
    return framework, results, analysis


class DataGenerator:
    """
    Utility class to generate realistic test data for the consciousness framework
    """
    def __init__(self, input_size=64):
        self.input_size = input_size
        self.pattern_library = {}
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize pattern library with common input patterns"""
        # Visual patterns (first quarter of input)
        visual_range = slice(0, self.input_size // 4)
        self.pattern_library['visual_simple'] = self._create_pattern(visual_range, pattern_type='gaussian')
        self.pattern_library['visual_complex'] = self._create_pattern(visual_range, pattern_type='sinusoidal')
        
        # Auditory patterns (second quarter)
        auditory_range = slice(self.input_size // 4, self.input_size // 2)
        self.pattern_library['auditory_simple'] = self._create_pattern(auditory_range, pattern_type='gaussian')
        self.pattern_library['auditory_complex'] = self._create_pattern(auditory_range, pattern_type='sinusoidal')
        
        # Language patterns (third quarter)
        language_range = slice(self.input_size // 2, 3 * self.input_size // 4)
        self.pattern_library['language_simple'] = self._create_pattern(language_range, pattern_type='gaussian')
        self.pattern_library['language_complex'] = self._create_pattern(language_range, pattern_type='structured')
        
        # Executive patterns (last quarter)
        executive_range = slice(3 * self.input_size // 4, self.input_size)
        self.pattern_library['executive_simple'] = self._create_pattern(executive_range, pattern_type='gaussian')
        self.pattern_library['executive_control'] = self._create_pattern(executive_range, pattern_type='control')
    
    def _create_pattern(self, input_range, pattern_type='gaussian'):
        """Create a specific type of pattern for a given input range"""
        pattern = np.zeros(self.input_size)
        
        if pattern_type == 'gaussian':
            # Bell curve pattern
            x = np.linspace(-3, 3, input_range.stop - input_range.start)
            y = np.exp(-x**2 / 2)
            pattern[input_range] = y
            
        elif pattern_type == 'sinusoidal':
            # Sine wave pattern
            x = np.linspace(0, 4*np.pi, input_range.stop - input_range.start)
            y = 0.5 * (np.sin(x) + 1)  # Rescale to [0,1]
            pattern[input_range] = y
            
        elif pattern_type == 'structured':
            # Pattern with structure (e.g., language-like)
            segment_size = (input_range.stop - input_range.start) // 4
            for i in range(4):
                segment = input_range.start + i*segment_size
                pattern[segment:segment+segment_size//2] = np.random.random(segment_size//2) * 0.5 + 0.5
                
        elif pattern_type == 'control':
            # Control signal pattern
            mid = (input_range.stop + input_range.start) // 2
            width = (input_range.stop - input_range.start) // 4
            pattern[mid-width:mid+width] = np.linspace(0.2, 1.0, width*2)
            
        else:
            # Random pattern
            pattern[input_range] = np.random.random(input_range.stop - input_range.start)
            
        return pattern
    
    def generate_input(self, dominant_modality=None, complexity=0.5, noise_level=0.1):
        """
        Generate input with specified characteristics
        
        Parameters:
        - dominant_modality: 'visual', 'auditory', 'language', 'executive', or None (mixed)
        - complexity: 0.0 (simple) to 1.0 (complex)
        - noise_level: Amount of noise to add (0.0 to 1.0)
        
        Returns:
        - input_vector: Generated input
        """
        input_vector = np.zeros(self.input_size)
        
        if dominant_modality == 'visual':
            pattern_key = 'visual_complex' if complexity > 0.5 else 'visual_simple'
            input_vector += self.pattern_library[pattern_key] * (0.8 + 0.2 * complexity)
            
            # Add some activation to other modalities
            input_vector += self.pattern_library['auditory_simple'] * 0.2 * (1-complexity)
            
        elif dominant_modality == 'auditory':
            pattern_key = 'auditory_complex' if complexity > 0.5 else 'auditory_simple'
            input_vector += self.pattern_library[pattern_key] * (0.8 + 0.2 * complexity)
            
            # Add some activation to other modalities
            input_vector += self.pattern_library['language_simple'] * 0.2 * (1-complexity)
            
        elif dominant_modality == 'language':
            pattern_key = 'language_complex' if complexity > 0.5 else 'language_simple'
            input_vector += self.pattern_library[pattern_key] * (0.8 + 0.2 * complexity)
            
            # Add some activation to other modalities
            input_vector += self.pattern_library['executive_simple'] * 0.2 * (1-complexity)
            
        elif dominant_modality == 'executive':
            pattern_key = 'executive_control' if complexity > 0.5 else 'executive_simple'
            input_vector += self.pattern_library[pattern_key] * (0.8 + 0.2 * complexity)
            
            # Add some activation to other modalities
            input_vector += self.pattern_library['visual_simple'] * 0.2 * (1-complexity)
            
        else:  # Mixed input
            # Combine all modalities with varying weights
            weights = np.random.random(4)
            weights = weights / weights.sum()  # Normalize
            
            input_vector += self.pattern_library['visual_simple'] * weights[0]
            input_vector += self.pattern_library['auditory_simple'] * weights[1]
            input_vector += self.pattern_library['language_simple'] * weights[2]
            input_vector += self.pattern_library['executive_simple'] * weights[3]
        
        # Add noise
        if noise_level > 0:
            input_vector += np.random.random(self.input_size) * noise_level
            
        # Ensure values are in [0,1]
        input_vector = np.clip(input_vector, 0, 1)
            
        return input_vector
    
    def generate_sequence(self, length=10, coherence=0.7):
        """
        Generate a coherent sequence of inputs
        
        Parameters:
        - length: Number of inputs in sequence
        - coherence: How coherent the sequence is (0.0 to 1.0)
        
        Returns:
        - sequence: List of input vectors
        """
        sequence = []
        
        # Select initial dominant modality
        modalities = ['visual', 'auditory', 'language', 'executive', None]
        current_modality = np.random.choice(modalities)
        
        # Generate sequence
        for i in range(length):
            # Possibly switch modality based on coherence
            if np.random.random() > coherence:
                current_modality = np.random.choice(modalities)
                
            # Vary complexity and noise over time
            complexity = 0.3 + 0.4 * np.sin(i/length * np.pi)
            noise = 0.05 + 0.1 * (1 - coherence)
            
            # Generate input
            input_vector = self.generate_input(
                dominant_modality=current_modality,
                complexity=complexity,
                noise_level=noise
            )
            
            sequence.append(input_vector)
            
        return sequence


def run_experiment(experiment_name="default", num_trials=50, sequence_length=20):
    """
    Run a complete experiment with the framework
    
    Parameters:
    - experiment_name: Name for saving results
    - num_trials: Number of trials to run
    - sequence_length: Length of each input sequence
    
    Returns:
    - results: Dictionary of experiment results
    """
    print(f"Starting experiment: {experiment_name}")
    
    # Initialize framework and data generator
    framework = ConsciousnessResearchFramework(input_size=64, hidden_size=32)
    data_gen = DataGenerator(input_size=64)
    
    # Store results
    trial_results = []
    awareness_indices = []
    phi_values = []
    
    # Run trials
    for trial in range(num_trials):
        print(f"Trial {trial+1}/{num_trials}...")
        
        # Generate coherent sequence with varying complexity
        coherence = 0.5 + 0.4 * np.sin(trial/num_trials * 2*np.pi)
        input_sequence = data_gen.generate_sequence(
            length=sequence_length, 
            coherence=coherence
        )
        
        # Process sequence
        sequence_results = []
        for input_data in input_sequence:
            result = framework.process_input(input_data)
            sequence_results.append(result)
            
            # Collect metrics
            awareness_indices.append(result['metrics']['awareness_index'])
            phi_values.append(result['phi_value'])
        
        # Analyze this trial
        trial_analysis = framework.analyze_consciousness_correlates()
        
        # Store trial results
        trial_results.append({
            'sequence_results': sequence_results,
            'analysis': trial_analysis,
            'coherence': coherence
        })
        
    # Analyze overall experiment
    experiment_summary = {
        'name': experiment_name,
        'num_trials': num_trials,
        'sequence_length': sequence_length,
        'mean_awareness_index': np.mean(awareness_indices),
        'mean_phi': np.mean(phi_values),
        'awareness_std': np.std(awareness_indices),
        'phi_std': np.std(phi_values)
    }
    
    # Visualize experiment results
    plt.figure(figsize=(12, 10))
    
    # Plot distribution of awareness indices
    plt.subplot(2, 2, 1)
    plt.hist(awareness_indices, bins=20)
    plt.title('Distribution of Awareness Index')
    plt.xlabel('Awareness Index')
    plt.ylabel('Frequency')
    
    # Plot distribution of phi values
    plt.subplot(2, 2, 2)
    plt.hist(phi_values, bins=20)
    plt.title('Distribution of Integrated Information (Phi)')
    plt.xlabel('Phi Value')
    plt.ylabel('Frequency')
    
    # Plot awareness vs phi
    plt.subplot(2, 2, 3)
    plt.scatter(phi_values, awareness_indices, alpha=0.5)
    plt.title('Awareness Index vs Phi')
    plt.xlabel('Phi Value')
    plt.ylabel('Awareness Index')
    
    # Plot awareness over time
    plt.subplot(2, 2, 4)
    plt.plot(awareness_indices[-100:])  # Last 100 points
    plt.title('Awareness Index Over Time (Last 100 inputs)')
    plt.xlabel('Time Step')
    plt.ylabel('Awareness Index')
    
    plt.tight_layout()
    plt.savefig(f'{experiment_name}_results.png')
    print(f"Experiment results saved to '{experiment_name}_results.png'")
    
    # Save detailed results
    experiment_results = {
        'summary': experiment_summary,
        'trial_results': trial_results,
        'awareness_indices': awareness_indices,
        'phi_values': phi_values
    }
    
    return experiment_results


if __name__ == "__main__":
    print("Neural Information Integration Framework")
    print("=" * 40)
    print("1. Run demo")
    print("2. Run experiment")
    choice = input("Select an option (1/2): ")
    
    if choice == '1':
        framework, results, analysis = main()
    elif choice == '2':
        experiment_name = input("Enter experiment name: ")
        num_trials = int(input("Number of trials: "))
        results = run_experiment(experiment_name, num_trials)
    else:
        print("Invalid choice. Exiting.")
