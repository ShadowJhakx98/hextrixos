"""
Neural Information Integration Framework
A research implementation of information integration measures and neural modeling
Based on established theories like Integrated Information Theory and Global Workspace
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import networkx as nx
from scipy.stats import entropy
import scipy.linalg as la
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
import torch
import torch.nn as nn
import torch.nn.functional as F


class IntegratedInformationCalculator:
    """
    Implements calculations related to Integrated Information Theory (IIT)
    Based on established research by Tononi et al.
    """
    def __init__(self, network_size: int = 8):
        self.network_size = network_size
        self.connectivity_matrix = None
        self.states = None
        
    def initialize_network(self, connectivity: Optional[np.ndarray] = None) -> None:
        """
        Initialize the network with a connectivity matrix
        If none provided, creates a random small-world network
        """
        if connectivity is not None:
            self.connectivity_matrix = connectivity
        else:
            # Create a small-world network structure (common in neuroscience)
            self.connectivity_matrix = np.zeros((self.network_size, self.network_size))
            
            # Add nearest-neighbor connections
            for i in range(self.network_size):
                self.connectivity_matrix[i, (i+1) % self.network_size] = np.random.uniform(0.5, 1.0)
                self.connectivity_matrix[i, (i-1) % self.network_size] = np.random.uniform(0.5, 1.0)
            
            # Add random long-range connections
            num_long_range = int(0.2 * self.network_size)
            for _ in range(num_long_range):
                i, j = np.random.choice(self.network_size, 2, replace=False)
                self.connectivity_matrix[i, j] = np.random.uniform(0.3, 0.7)
                
        # Initialize network states
        self.states = np.zeros(self.network_size)
        
    def update_states(self, inputs: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Update network states based on connectivity and inputs
        """
        if self.connectivity_matrix is None:
            self.initialize_network()
            
        if inputs is not None:
            # Set external inputs
            external = np.zeros_like(self.states)
            external[:len(inputs)] = inputs[:len(external)]
        else:
            external = np.zeros_like(self.states)
            
        # Update based on simple neural dynamics
        new_states = np.tanh(np.dot(self.connectivity_matrix, self.states) + external)
        self.states = 0.8 * self.states + 0.2 * new_states  # With some stability
        
        return self.states
        
    def calculate_phi(self, n_partitions: int = 1) -> float:
        """
        Calculate integrated information (Φ) based on effective information
        between system partitions
        """
        if self.states is None or self.connectivity_matrix is None:
            return 0.0
            
        # Use mutual information between partitions as a measure of integration
        phi_value = 0.0
        
        # Create partitions
        if n_partitions > 1:
            partition_size = self.network_size // n_partitions
            partitions = []
            
            for i in range(n_partitions):
                start = i * partition_size
                end = start + partition_size if i < n_partitions - 1 else self.network_size
                partitions.append(list(range(start, end)))
                
            # Calculate effective information between partitions
            for i, part1 in enumerate(partitions):
                for j, part2 in enumerate(partitions):
                    if i < j:  # Only unique pairs
                        mi = self._mutual_information_between_partitions(part1, part2)
                        phi_value += mi
                        
            # Normalize by number of partition pairs
            num_pairs = (n_partitions * (n_partitions - 1)) // 2
            if num_pairs > 0:
                phi_value /= num_pairs
        else:
            # Calculate whole-system integration using covariance
            state_series = [self.states.copy()]
            for _ in range(10):  # Generate a time series
                self.update_states()
                state_series.append(self.states.copy())
                
            state_series = np.array(state_series)
            cov_matrix = np.cov(state_series.T)
            
            # Use determinant of covariance as integration measure
            # Higher determinant = more integrated information
            if cov_matrix.shape[0] > 1:
                phi_value = max(0, np.log(np.linalg.det(cov_matrix) + 1e-10))
                
        return phi_value
        
    def _mutual_information_between_partitions(self, part1: List[int], part2: List[int]) -> float:
        """
        Calculate mutual information between two partitions of the system
        """
        if len(part1) == 0 or len(part2) == 0:
            return 0.0
            
        # Extract states for each partition
        states1 = self.states[part1]
        states2 = self.states[part2]
        
        # Extract connectivity between partitions
        conn_1to2 = self.connectivity_matrix[np.ix_(part1, part2)]
        conn_2to1 = self.connectivity_matrix[np.ix_(part2, part1)]
        
        # Simplified mutual information based on connectivity
        mi_1to2 = np.mean(np.abs(conn_1to2)) * np.std(states1) * np.std(states2)
        mi_2to1 = np.mean(np.abs(conn_2to1)) * np.std(states2) * np.std(states1)
        
        return (mi_1to2 + mi_2to1) / 2.0


class GlobalWorkspaceModel:
    """
    Implements a neural network model inspired by Global Workspace Theory (GWT)
    GWT is a scientific theory of consciousness by Bernard Baars
    """
    def __init__(self, input_size: int = 64, workspace_size: int = 16):
        self.input_size = input_size
        self.workspace_size = workspace_size
        self.specialist_modules = []
        self.workspace = np.zeros(workspace_size)
        self.workspace_access_threshold = 0.6
        self.attention_weights = np.ones(input_size) / input_size
        self.competition_factor = 0.8
        
    def add_specialist_module(self, name: str, input_indices: List[int], 
                             output_indices: List[int], strength: float = 1.0) -> None:
        """
        Add a specialist processing module to the system
        In GWT, specialist modules compete for access to the global workspace
        """
        module = {
            'name': name,
            'input_indices': input_indices,
            'output_indices': output_indices,
            'activation': 0.0,
            'weight_matrix': np.random.randn(len(output_indices), len(input_indices)) * strength,
            'bias': np.random.randn(len(output_indices)) * 0.1,
            'access_count': 0
        }
        self.specialist_modules.append(module)
        
    def process_input(self, inputs: np.ndarray) -> np.ndarray:
        """
        Process inputs through specialist modules and update global workspace
        Returns the workspace state
        """
        # Apply attention weights to inputs
        attended_inputs = inputs * self.attention_weights[:len(inputs)]
        
        # Process through specialist modules
        module_outputs = []
        module_activations = []
        
        for module in self.specialist_modules:
            # Extract relevant inputs for this module
            module_inputs = attended_inputs[module['input_indices']]
            
            # Process through module
            raw_output = np.tanh(np.dot(module['weight_matrix'], module_inputs) + module['bias'])
            
            # Calculate module activation level (how strongly it requests workspace access)
            activation = np.mean(np.abs(raw_output)) 
            module['activation'] = activation
            
            module_outputs.append((module['output_indices'], raw_output))
            module_activations.append(activation)
            
        # Competition for workspace access
        if module_activations:
            # Normalize activations
            total_activation = sum(module_activations) + 1e-10
            normalized_activations = [act / total_activation for act in module_activations]
            
            # Winner-takes-most competition
            max_idx = np.argmax(normalized_activations)
            for i, module in enumerate(self.specialist_modules):
                if i == max_idx:
                    # Winner gets more activation
                    module['activation'] *= self.competition_factor
                    module['access_count'] += 1
                else:
                    # Others get less
                    module['activation'] *= (1 - self.competition_factor) 
            
            # Update workspace based on winning modules
            new_workspace = np.zeros_like(self.workspace)
            
            for i, module in enumerate(self.specialist_modules):
                if module['activation'] > self.workspace_access_threshold:
                    # This module gets workspace access
                    output_indices, outputs = module_outputs[i]
                    
                    # Map to workspace indices that overlap with this module's outputs
                    for j, out_idx in enumerate(output_indices):
                        if out_idx < len(new_workspace):
                            new_workspace[out_idx] += outputs[j] * module['activation']
            
            # Update workspace with some persistence
            self.workspace = 0.7 * self.workspace + 0.3 * new_workspace
            
            # Update attention based on workspace state
            self._update_attention()
        
        return self.workspace
    
    def _update_attention(self) -> None:
        """
        Update attention weights based on workspace activity
        Implements top-down attention from workspace to inputs
        """
        # Create attention weights that prioritize inputs relevant to active workspace
        new_weights = np.ones_like(self.attention_weights) * 0.1  # Base attention
        
        # Increase attention for inputs connected to active workspace elements
        active_ws_indices = np.where(np.abs(self.workspace) > 0.3)[0]
        
        for module in self.specialist_modules:
            # Check if this module connects to active workspace areas
            if any(out_idx in active_ws_indices for out_idx in module['output_indices']):
                # Increase attention to this module's inputs
                for in_idx in module['input_indices']:
                    if in_idx < len(new_weights):
                        new_weights[in_idx] += 0.2
        
        # Normalize weights
        self.attention_weights = new_weights / np.sum(new_weights)
        
    def get_dominant_module(self) -> Dict:
        """
        Return the currently dominant module in the workspace
        """
        if not self.specialist_modules:
            return None
            
        idx = np.argmax([m['activation'] for m in self.specialist_modules])
        return self.specialist_modules[idx]
    
    def get_workspace_statistics(self) -> Dict:
        """
        Return statistics about the global workspace
        """
        return {
            'mean_activation': np.mean(np.abs(self.workspace)),
            'max_activation': np.max(np.abs(self.workspace)),
            'active_regions': np.sum(np.abs(self.workspace) > 0.5),
            'entropy': entropy(np.abs(self.workspace) + 1e-10),
            'dominant_module': self.get_dominant_module()['name'] if self.get_dominant_module() else None
        }


class PredictiveCodingNetwork(nn.Module):
    """
    Neural network implementing predictive coding principles
    Based on the free energy principle and predictive processing theory
    """
    def __init__(self, input_size: int = 28*28, hidden_size: int = 128, latent_size: int = 32):
        super(PredictiveCodingNetwork, self).__init__()
        
        # Encoder network (recognition model)
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, latent_size * 2)  # Mean and log variance
        )
        
        # Decoder network (generative model)
        self.decoder = nn.Sequential(
            nn.Linear(latent_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, input_size),
            nn.Sigmoid()  # Assuming input is normalized to [0,1]
        )
        
        self.input_size = input_size
        self.latent_size = latent_size
        self.prediction_errors = []
        self.surprise_history = []
        
    def encode(self, x):
        """
        Encode input to latent distribution parameters
        """
        h = self.encoder(x)
        mu, logvar = h.chunk(2, dim=-1)
        return mu, logvar
        
    def reparameterize(self, mu, logvar):
        """
        Reparameterization trick for sampling from distribution
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
        
    def decode(self, z):
        """
        Decode latent representation to prediction
        """
        return self.decoder(z)
        
    def forward(self, x):
        """
        Forward pass through the network
        """
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_pred = self.decode(z)
        
        # Calculate prediction error
        pred_error = F.mse_loss(x_pred, x, reduction='none')
        
        # Calculate KL divergence (surprise)
        kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp(), dim=1)
        
        # Store metrics
        self.prediction_errors.append(pred_error.mean().item())
        self.surprise_history.append(kl_div.mean().item())
        
        return x_pred, pred_error, kl_div, mu, z
        
    def calculate_free_energy(self, x):
        """
        Calculate variational free energy (evidence lower bound)
        """
        x_tensor = torch.FloatTensor(x).view(1, -1)
        mu, logvar = self.encode(x_tensor)
        z = self.reparameterize(mu, logvar)
        x_pred = self.decode(z)
        
        # Reconstruction loss
        recon_loss = F.mse_loss(x_pred, x_tensor, reduction='sum')
        
        # KL divergence
        kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        
        # Free energy = reconstruction loss + KL divergence
        free_energy = recon_loss + kl_div
        
        return {
            'free_energy': free_energy.item(),
            'reconstruction_loss': recon_loss.item(),
            'kl_divergence': kl_div.item(),
            'prediction': x_pred.detach().numpy(),
            'latent': z.detach().numpy()
        }
        
    def process_sequence(self, sequence):
        """
        Process a sequence of inputs and track surprisal
        """
        surprisal = []
        predictions = []
        
        for x in sequence:
            x_tensor = torch.FloatTensor(x).view(1, -1)
            results = self.calculate_free_energy(x_tensor)
            
            surprisal.append(results['free_energy'])
            predictions.append(results['prediction'])
            
        return {
            'surprisal': surprisal,
            'predictions': predictions,
            'mean_surprisal': np.mean(surprisal),
            'surprisal_derivative': np.diff(surprisal, prepend=surprisal[0])
        }


class RecurrentAttentionNetwork(nn.Module):
    """
    Neural network with recurrent connections and attention mechanism
    Combines aspects of working memory and selective attention
    """
    def __init__(self, input_size, hidden_size, num_layers=1):
        super(RecurrentAttentionNetwork, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.Tanh(),
            nn.Linear(hidden_size, 1),
            nn.Softmax(dim=1)
        )
        
        # Recurrent layer (GRU for stability)
        self.rnn = nn.GRU(
            input_size, hidden_size, num_layers, 
            batch_first=True, bidirectional=False
        )
        
        # Output layer
        self.fc = nn.Linear(hidden_size, input_size)
        
        # Memory trace
        self.memory_trace = []
        self.attention_trace = []
        
    def forward(self, x, hidden=None):
        """
        Forward pass with attention
        x: [batch_size, sequence_length, input_size]
        """
        batch_size, seq_len, _ = x.size()
        
        # Calculate attention weights
        attn_weights = []
        for t in range(seq_len):
            x_t = x[:, t:t+1, :]  # [batch, 1, input_size]
            a_t = self.attention(x_t.view(batch_size, -1))  # [batch, 1]
            attn_weights.append(a_t)
            
        attn_weights = torch.cat(attn_weights, dim=1)  # [batch, seq_len]
        attn_weights = attn_weights.unsqueeze(2)  # [batch, seq_len, 1]
        
        # Apply attention to input
        x_weighted = x * attn_weights
        
        # Process through RNN
        if hidden is None:
            hidden = torch.zeros(
                self.num_layers, batch_size, self.hidden_size, 
                device=x.device
            )
            
        output, hidden = self.rnn(x_weighted, hidden)
        
        # Apply output layer
        output = self.fc(output)
        
        # Store states
        self.memory_trace.append(hidden.detach().numpy())
        self.attention_trace.append(attn_weights.detach().numpy())
        
        return output, hidden, attn_weights
        
    def get_attention_stats(self):
        """
        Get statistics about attention focus
        """
        if not self.attention_trace:
            return {}
            
        recent_attention = self.attention_trace[-1]
        return {
            'focus_intensity': float(np.max(recent_attention)),
            'focus_stability': float(np.std(recent_attention)),
            'attention_entropy': float(entropy(recent_attention.flatten() + 1e-10))
        }


class ConsciousnessResearchFramework:
    """
    Research framework for studying neural correlates of consciousness
    Integrates multiple theoretical approaches
    """
    def __init__(self, input_size=64, hidden_size=32):
        # Initialize component models
        self.iit_calculator = IntegratedInformationCalculator(network_size=hidden_size)
        self.global_workspace = GlobalWorkspaceModel(input_size=input_size, workspace_size=hidden_size)
        
        # Initialize PyTorch models
        self.predictive_coder = PredictiveCodingNetwork(input_size=input_size, hidden_size=hidden_size*2, latent_size=hidden_size)
        self.attention_network = RecurrentAttentionNetwork(input_size=input_size, hidden_size=hidden_size)
        
        # Performance tracking
        self.metrics_history = []
        self.input_history = deque(maxlen=100)
        
        # System configuration
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Initialize network structure
        self._setup_network_structure()
        
    def _setup_network_structure(self):
        """
        Set up the modular structure of the system
        """
        # Initialize IIT network
        self.iit_calculator.initialize_network()
        
        # Add specialist modules to global workspace
        module_specs = [
            # Visual processing module
            ("visual", list(range(0, self.input_size//4)), list(range(0, self.hidden_size//4))),
            # Auditory processing module
            ("auditory", list(range(self.input_size//4, self.input_size//2)), 
                        list(range(self.hidden_size//4, self.hidden_size//2))),
            # Language processing module
            ("language", list(range(self.input_size//2, 3*self.input_size//4)), 
                       list(range(self.hidden_size//2, 3*self.hidden_size//4))),
            # Executive control module
            ("executive", list(range(3*self.input_size//4, self.input_size)), 
                        list(range(3*self.hidden_size//4, self.hidden_size)))
        ]
        
        for name, inputs, outputs in module_specs:
            self.global_workspace.add_specialist_module(
                name=name,
                input_indices=inputs,
                output_indices=outputs,
                strength=np.random.uniform(0.8, 1.2)
            )
            
    def process_input(self, input_data):
        """
        Process input through all component models
        Returns combined results and consciousness-related metrics
        """
        # Ensure input is properly formatted
        if not isinstance(input_data, np.ndarray):
            input_data = np.array(input_data)
            
        # Reshape to expected dimensions
        input_data = input_data.flatten()[:self.input_size]
        if len(input_data) < self.input_size:
            # Pad if needed
            input_data = np.pad(input_data, (0, self.input_size - len(input_data)))
            
        # Normalize to [0,1]
        input_data = (input_data - np.min(input_data)) / (np.max(input_data) - np.min(input_data) + 1e-10)
        
        # Store in history
        self.input_history.append(input_data)
        
        # Process through Global Workspace
        workspace_state = self.global_workspace.process_input(input_data)
        
        # Process through IIT calculator
        self.iit_calculator.update_states(input_data[:self.iit_calculator.network_size])
        phi_value = self.iit_calculator.calculate_phi(n_partitions=4)
        
        # Process through Predictive Coding Network
        input_tensor = torch.FloatTensor(input_data).view(1, -1)
        with torch.no_grad():  # Inference only
            pc_output, pred_error, surprise, _, _ = self.predictive_coder(input_tensor)
            
        # Process through Attention Network
        input_sequence = torch.FloatTensor(list(self.input_history)).unsqueeze(0)  # [1, seq, features]
        with torch.no_grad():  # Inference only
            if input_sequence.size(1) > 0:  # If we have history
                attn_output, _, attn_weights = self.attention_network(input_sequence)
                
        # Calculate consciousness-related metrics
        metrics = self._calculate_consciousness_metrics(
            phi_value, workspace_state, pred_error.mean().item(), surprise.mean().item()
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Return processed results and metrics
        return {
            'workspace_state': workspace_state,
            'phi_value': phi_value,
            'prediction_error': pred_error.mean().item(),
            'surprise': surprise.mean().item(),
            'metrics': metrics,
            'dominant_module': self.global_workspace.get_dominant_module()['name'] 
                              if self.global_workspace.get_dominant_module() else None
        }
        
    def _calculate_consciousness_metrics(self, phi, workspace_state, pred_error, surprise):
        """
        Calculate metrics related to theorized aspects of consciousness
        """
        # Workspace metrics
        workspace_activation = np.mean(np.abs(workspace_state))
        workspace_complexity = entropy(np.abs(workspace_state) + 1e-10)
        
        # Dynamic complexity (integration + differentiation)
        dynamic_complexity = phi * workspace_complexity
        
        # Information processing metrics
        info_integration = phi
        info_differentiation = workspace_complexity
        
        # Calculate metrics combining multiple theories
        # Based on IIT, GWT, and predictive processing
        awareness_index = (0.4 * phi + 0.3 * workspace_activation + 
                          0.2 * (1 - pred_error) + 0.1 * (1 - surprise))
        
        # Scale to interpretable range [0, 1]
        awareness_index = np.tanh(awareness_index)
        
        return {
            'phi': phi,
            'workspace_activation': workspace_activation,
            'workspace_complexity': workspace_complexity,
            'dynamic_complexity': dynamic_complexity,
            'prediction_error': pred_error,
            'surprise': surprise,
            'awareness_index': awareness_index
        }
        
    def analyze_consciousness_correlates(self):
        """
        Analyze metrics to identify neural correlates of consciousness
        """
        if len(self.metrics_history) < 2:
            return {"error": "Not enough data for analysis"}
            
        metrics_df = pd.DataFrame(self.metrics_history)
        
        # Calculate correlations between metrics
        correlations = metrics_df.corr()
        
        # Perform PCA on metrics to find principal components
        pca = PCA(n_components=min(3, len(metrics_df.columns)))
        pca_result = pca.fit_transform(metrics_df)
        
        # Find which original metrics correlate most with principal components
        loadings = pca.components_
        
        return {
            'correlations': correlations.to_dict(),
            'principal_components': {
                'explained_variance': pca.explained_variance_ratio_.tolist(),
                'loadings': {
                    f'PC{i+1}': {
                        metrics_df.columns[j]: loadings[i, j] 
                        for j in range(len(metrics_df.columns))
                    }
                    for i in range(len(loadings))
                }
            },
            'key_findings': self._interpret_consciousness_analysis(correlations, loadings, metrics_df.columns)
        }
        
    def _interpret_consciousness_analysis(self, correlations, pca_loadings, column_names):
        """
        Generate interpretations of consciousness analysis
        """
        # Find strongest correlations
        corr_dict = correlations.to_dict()
        strong_correlations = []
        
        for i, col1 in enumerate(column_names):
            for j, col2 in enumerate(column_names):
                if i < j:  # Only look at unique pairs
                    corr = corr_dict[col1][col2]
                    if abs(corr) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            'metrics': [col1, col2],
                            'correlation': corr
                        })
                        
        # Identify metrics with strongest loadings on first principal component
        pc1_loadings = [(column_names[i], pca_loadings[0, i]) for i in range(len(column_names))]
        pc1_loadings.sort(key=lambda x: abs(x[1]), reverse=True)
        
        key_metrics = [m for m, _ in pc1_loadings[:3]]
        
        return {
            'strong_correlations': strong_correlations,
            'key_consciousness_metrics': key_metrics,
            'integrated_information_importance': 'phi' in key_metrics,
            'global_workspace_importance': 'workspace_activation' in key_metrics,
            'predictive_processing_importance': 'prediction_error' in key_metrics or 'surprise' in key_metrics
        }
        
    def visualize_consciousness_metrics(self):
        """
        Generate data for visualizing consciousness-related metrics
        """
        if not self.metrics_history:
            return None
            
        metrics_df = pd.DataFrame(self.metrics_history)
        
        # Create time series data for key metrics
        time_series = {
            'phi': metrics_df['phi'].tolist(),
            'awareness_index': metrics_df['awareness_index'].tolist(),
            'workspace_activation': metrics_df['workspace_activation'].tolist(),
            'prediction_error': metrics_df['prediction_error'].tolist()
        }
        
        # Prepare correlation data
        correlations = metrics_df.corr()
        
        # Return data for visualization
        return {
            'time_series': time_series,
            'correlations': correlations.to_dict(),
            'latest_state': metrics_df.iloc[-1].to_dict() if len(metrics_df) > 0 else {}
        }


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
