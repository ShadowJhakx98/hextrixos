"""
self_awareness.py

Contains the SelfAwareness class with capabilities for self-reflection,
code introspection, and automated self-improvement.
"""

import difflib
import inspect
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
from textblob import TextBlob

logger = logging.getLogger("SelfAwareness")
logger.setLevel(logging.INFO)

class SelfAwareness:
    """
    Provides self-reflection capabilities to analyze and improve the system's own code.
    """
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.memory = []
        self.current_model = ""
        self.update_logs = []
        self.improvement_metrics = {
            'code_quality': 0.0,
            'feature_completeness': 0.0,
            'safety_checks': 0.0,
            'performance': 0.0
        }
        self.last_update = datetime.now()
        self.reflection_count = 0
        self.self_models_dir = 'self_models'
        
        # Create directory for saving self-models if it doesn't exist
        if not os.path.exists(self.self_models_dir):
            os.makedirs(self.self_models_dir)
            
        # Initialize current model
        self.update_self_model()

    def update_self_model(self):
        """
        Update the self-model by introspecting the current state of JARVIS.
        """
        try:
            # Get current state through introspection
            current_state = self.jarvis.introspect()
            
            # Check if current_state is valid
            if current_state is None:
                logger.error("Introspection returned None")
                current_state = "# Error: Introspection failed to return valid data"
            
            # Save timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Compare with previous model if it exists
            if self.current_model:
                # Analyze differences
                diff_analysis = self.analyze_diff(self.current_model, current_state)
                
                # Log the analysis
                self.update_logs.append({
                    'timestamp': timestamp,
                    'diff_summary': diff_analysis['summary'],
                    'improvements': diff_analysis['improvements'],
                    'regressions': diff_analysis['regressions']
                })
                
                # Update improvement metrics
                self._update_improvement_metrics(diff_analysis)
            
            # Save the current state
            self.current_model = current_state
            self.memory.append({
                'timestamp': timestamp,
                'model': current_state
            })
            
            # Save to file
            self._save_current_model(timestamp)
            
            # Update last update time
            self.last_update = datetime.now()
            self.reflection_count += 1
            
            logger.info(f"Self-model updated (#{self.reflection_count})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating self-model: {str(e)}")
            return False

    def _save_current_model(self, timestamp):
        """Save current model to file."""
        try:
            # Ensure current_model is a string
            if self.current_model is None:
                self.current_model = "# Error: No model data available"
            elif not isinstance(self.current_model, str):
                self.current_model = str(self.current_model)
            
            model_path = os.path.join(self.self_models_dir, f"model_{timestamp}.py")
            with open(model_path, 'w') as f:
                f.write(self.current_model)
            
            # Also save metrics
            metrics_path = os.path.join(self.self_models_dir, f"metrics_{timestamp}.json")
            with open(metrics_path, 'w') as f:
                json.dump({
                    'metrics': self.improvement_metrics,
                    'reflection_count': self.reflection_count,
                    'timestamp': timestamp
                }, f, indent=2)
                
            logger.info(f"Self-model saved to {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving self-model: {str(e)}")
            return False

    def analyze_diff(self, old_state: str, new_state: str) -> Dict:
        """
        Analyze differences between two code states.
        
        Args:
            old_state: Previous code state
            new_state: Current code state
            
        Returns:
            Dictionary with analysis summary
        """
        # Ensure states are strings
        if not isinstance(old_state, str):
            old_state = str(old_state)
        if not isinstance(new_state, str):
            new_state = str(new_state)
            
        # Create a diff object
        differ = difflib.Differ()
        diff = list(differ.compare(old_state.splitlines(), new_state.splitlines()))
        
        # Calculate metrics
        added_lines = [line for line in diff if line.startswith('+ ')]
        removed_lines = [line for line in diff if line.startswith('- ')]
        changed_lines = len(added_lines) + len(removed_lines)
        total_lines = len(new_state.splitlines())
        change_percentage = (changed_lines / max(1, total_lines)) * 100
        
        # Identify key changes
        improvements = []
        regressions = []
        
        # Look for function additions
        function_pattern = r'def\s+(\w+)'
        old_functions = set(re.findall(function_pattern, old_state))
        new_functions = set(re.findall(function_pattern, new_state))
        
        added_functions = new_functions - old_functions
        removed_functions = old_functions - new_functions
        
        for func in added_functions:
            improvements.append(f"Added function: {func}")
        
        for func in removed_functions:
            regressions.append(f"Removed function: {func}")
        
        # Look for error handling improvements
        try_except_old = old_state.count('try:')
        try_except_new = new_state.count('try:')
        
        if try_except_new > try_except_old:
            improvements.append(f"Improved error handling: Added {try_except_new - try_except_old} try-except blocks")
        elif try_except_new < try_except_old:
            regressions.append(f"Reduced error handling: Removed {try_except_old - try_except_new} try-except blocks")
        
        # Look for logging improvements
        logging_old = old_state.count('logger.')
        logging_new = new_state.count('logger.')
        
        if logging_new > logging_old:
            improvements.append(f"Improved logging: Added {logging_new - logging_old} log statements")
        
        # Analyze added lines for specific patterns
        for line in added_lines:
            line = line[2:]  # Remove the '+ ' prefix
            
            # Check for parameter validation
            if re.search(r'if\s+.*(None|not|invalid|\<|\>)', line):
                improvements.append("Added parameter validation")
            
            # Check for memory optimization
            if re.search(r'(cache|optimize|performance)', line):
                improvements.append("Added memory or performance optimization")
        
        # Sentiment analysis on changes to detect improvements
        added_text = ' '.join([line[2:] for line in added_lines])
        removed_text = ' '.join([line[2:] for line in removed_lines])
        
        try:
            added_sentiment = TextBlob(added_text).sentiment.polarity
            removed_sentiment = TextBlob(removed_text).sentiment.polarity
            
            sentiment_diff = added_sentiment - removed_sentiment
            if sentiment_diff > 0.2:
                improvements.append(f"Positive code sentiment improvement: {sentiment_diff:.2f}")
            elif sentiment_diff < -0.2:
                regressions.append(f"Negative code sentiment change: {sentiment_diff:.2f}")
        except:
            # TextBlob might not be available or might fail
            pass
        
        # Deduplicate insights
        improvements = list(set(improvements))
        regressions = list(set(regressions))
        
        return {
            'summary': {
                'added_lines': len(added_lines),
                'removed_lines': len(removed_lines),
                'changed_lines': changed_lines,
                'total_lines': total_lines,
                'change_percentage': change_percentage,
                'added_functions': len(added_functions),
                'removed_functions': len(removed_functions)
            },
            'improvements': improvements,
            'regressions': regressions,
            'diff': diff
        }

    def _update_improvement_metrics(self, diff_analysis: Dict):
        """Update improvement metrics based on diff analysis."""
        # Update code quality metric
        improvements_count = len(diff_analysis['improvements'])
        regressions_count = len(diff_analysis['regressions'])
        
        net_improvement = improvements_count - regressions_count
        
        # Apply bounded update to metrics
        def bounded_update(current, delta, lower=0.0, upper=1.0):
            return min(upper, max(lower, current + delta))
        
        if net_improvement > 0:
            self.improvement_metrics['code_quality'] = bounded_update(
                self.improvement_metrics['code_quality'], 0.05 * net_improvement)
        elif net_improvement < 0:
            self.improvement_metrics['code_quality'] = bounded_update(
                self.improvement_metrics['code_quality'], 0.03 * net_improvement)
        
        # Update feature completeness based on added functions
        added_functions = diff_analysis['summary']['added_functions']
        if added_functions > 0:
            self.improvement_metrics['feature_completeness'] = bounded_update(
                self.improvement_metrics['feature_completeness'], 0.02 * added_functions)
        
        # Update safety checks based on try-except and validation improvements
        safety_improvements = sum(1 for imp in diff_analysis['improvements'] 
                                if 'error handling' in imp.lower() or 'validation' in imp.lower())
        if safety_improvements > 0:
            self.improvement_metrics['safety_checks'] = bounded_update(
                self.improvement_metrics['safety_checks'], 0.05 * safety_improvements)
        
        # Update performance based on optimization mentions
        performance_improvements = sum(1 for imp in diff_analysis['improvements']
                                     if 'performance' in imp.lower() or 'optimize' in imp.lower())
        if performance_improvements > 0:
            self.improvement_metrics['performance'] = bounded_update(
                self.improvement_metrics['performance'], 0.04 * performance_improvements)

    def generate_self_improvement(self, focus_area=None) -> Dict:
        """
        Generate suggestions for self-improvement based on current state.
        
        Args:
            focus_area: Optional area to focus improvements on
            
        Returns:
            Dictionary with improvement suggestions
        """
        if not self.current_model:
            logger.warning("No current model available")
            return {"error": "No model available for improvement analysis"}
        
        suggestions = []
        
        # Analyze current model for improvement opportunities
        model_lines = self.current_model.splitlines()
        
        # Look for common code issues
        todo_count = 0
        long_functions = []
        complex_conditionals = []
        missing_docstrings = []
        duplicated_code_sections = []
        
        current_function = None
        function_body = []
        function_line_start = 0
        
        for i, line in enumerate(model_lines):
            # Track TODOs
            if "TODO" in line or "FIXME" in line:
                todo_count += 1
                suggestions.append({
                    'type': 'implement_todo',
                    'description': f"Implement TODO at line {i+1}: {line.strip()}",
                    'line': i+1,
                    'priority': 'medium'
                })
            
            # Track function definitions and bodies
            if re.match(r'\s*def\s+(\w+)', line):
                # Process previous function if any
                if current_function and len(function_body) > 20:
                    long_functions.append({
                        'name': current_function,
                        'length': len(function_body),
                        'line': function_line_start + 1
                    })
                
                # Start tracking new function
                match = re.match(r'\s*def\s+(\w+)', line)
                current_function = match.group(1)
                function_body = []
                function_line_start = i
                
                # Check for missing docstring
                if i+1 < len(model_lines) and not re.match(r'\s+"""', model_lines[i+1]):
                    missing_docstrings.append({
                        'name': current_function,
                        'line': i+1
                    })
            
            # Add line to current function body
            if current_function:
                function_body.append(line)
            
            # Check for complex conditionals
            if re.search(r'if\s+.*and.*and.*and', line) or re.search(r'if\s+.*or.*or.*or', line):
                complex_conditionals.append({
                    'line': i+1,
                    'content': line.strip()
                })
        
        # Process last function if any
        if current_function and len(function_body) > 20:
            long_functions.append({
                'name': current_function,
                'length': len(function_body),
                'line': function_line_start + 1
            })
        
        # Add suggestions based on analysis
        for func in long_functions:
            suggestions.append({
                'type': 'refactor_long_function',
                'description': f"Refactor long function '{func['name']}' ({func['length']} lines) at line {func['line']}",
                'line': func['line'],
                'priority': 'high' if func['length'] > 50 else 'medium'
            })
        
        for cond in complex_conditionals:
            suggestions.append({
                'type': 'simplify_conditional',
                'description': f"Simplify complex conditional at line {cond['line']}: {cond['content']}",
                'line': cond['line'],
                'priority': 'medium'
            })
        
        for doc in missing_docstrings:
            suggestions.append({
                'type': 'add_docstring',
                'description': f"Add docstring to function '{doc['name']}' at line {doc['line']}",
                'line': doc['line'],
                'priority': 'low'
            })
        
        # Look for missing error handling
        error_handling_ratio = self.current_model.count('try:') / max(1, self.current_model.count('def '))
        if error_handling_ratio < 0.3:
            suggestions.append({
                'type': 'improve_error_handling',
                'description': f"Add more error handling. Current ratio: {error_handling_ratio:.2f} try-except blocks per function",
                'priority': 'high'
            })
        
        # Filter by focus area if specified
        if focus_area:
            focus_area = focus_area.lower()
            filtered_suggestions = []
            
            if focus_area == 'error_handling':
                filtered_suggestions = [s for s in suggestions if 'error' in s['type']]
            elif focus_area == 'performance':
                filtered_suggestions = [s for s in suggestions if 'performance' in s['description'].lower()]
            elif focus_area == 'documentation':
                filtered_suggestions = [s for s in suggestions if 'docstring' in s['type']]
            elif focus_area == 'refactoring':
                filtered_suggestions = [s for s in suggestions if 'refactor' in s['type']]
            
            suggestions = filtered_suggestions if filtered_suggestions else suggestions
        
        # Sort by priority
        priority_map = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_map.get(x.get('priority', 'low'), 3))
        
        return {
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'metrics': self.improvement_metrics,
            'suggestions': suggestions,
            'todo_count': todo_count,
            'long_functions_count': len(long_functions),
            'complex_conditionals_count': len(complex_conditionals),
            'missing_docstrings_count': len(missing_docstrings)
        }
        
    def get_improvement_history(self) -> List[Dict]:
        """Get history of improvements and metrics over time."""
        history = []
        
        for i, log in enumerate(self.update_logs):
            if i > 0:  # Skip first entry as it has no previous state to compare with
                history.append({
                    'timestamp': log['timestamp'],
                    'improvements': log['improvements'],
                    'regressions': log['regressions'],
                    'net_improvement': len(log['improvements']) - len(log['regressions'])
                })
        
        return history
    
    def generate_code_evolution_report(self) -> Dict:
        """Generate a report on code evolution over time."""
        if len(self.memory) < 2:
            return {"error": "Not enough history to generate evolution report"}
        
        first_model = self.memory[0]['model']
        latest_model = self.memory[-1]['model']
        
        # Generate a comprehensive diff
        diff_analysis = self.analyze_diff(first_model, latest_model)
        
        # Calculate growth metrics
        first_lines = len(first_model.splitlines())
        latest_lines = len(latest_model.splitlines())
        growth_percentage = ((latest_lines - first_lines) / first_lines) * 100
        
        # Count functions
        first_funcs = len(re.findall(r'def\s+(\w+)', first_model))
        latest_funcs = len(re.findall(r'def\s+(\w+)', latest_model))
        
        # Count classes
        first_classes = len(re.findall(r'class\s+(\w+)', first_model))
        latest_classes = len(re.findall(r'class\s+(\w+)', latest_model))
        
        # Identify key milestones
        milestones = []
        for i, log in enumerate(self.update_logs):
            if len(log['improvements']) > 3:
                milestones.append({
                    'timestamp': log['timestamp'],
                    'improvements': log['improvements']
                })
        
        return {
            'start_date': self.memory[0]['timestamp'],
            'end_date': self.memory[-1]['timestamp'],
            'code_growth': {
                'initial_lines': first_lines,
                'current_lines': latest_lines,
                'growth_percentage': growth_percentage,
                'initial_functions': first_funcs, 
                'current_functions': latest_funcs,
                'initial_classes': first_classes,
                'current_classes': latest_classes
            },
            'key_milestones': milestones[:5],  # Top 5 milestones
            'current_metrics': self.improvement_metrics,
            'reflection_count': self.reflection_count
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics and trends."""
        # Calculate days since first model
        if not self.memory:
            return {"error": "No performance history available"}
        
        first_date = datetime.strptime(self.memory[0]['timestamp'], "%Y%m%d_%H%M%S")
        latest_date = datetime.strptime(self.memory[-1]['timestamp'], "%Y%m%d_%H%M%S")
        days_active = (latest_date - first_date).days
        
        # Calculate improvement rate
        improvement_rate = {
            metric: value / max(1, days_active) * 30  # Normalized to monthly rate
            for metric, value in self.improvement_metrics.items()
        }
        
        return {
            'days_active': days_active,
            'reflection_count': self.reflection_count,
            'reflections_per_day': self.reflection_count / max(1, days_active),
            'current_metrics': self.improvement_metrics,
            'monthly_improvement_rate': improvement_rate
        }

    def initialize_continuous_improvement(self, interval_hours=24):
        """Start a continuous improvement cycle."""
        import threading
        
        def improvement_cycle():
            while True:
                try:
                    # Wait for the specified interval
                    time.sleep(interval_hours * 3600)
                    
                    # Update self-model
                    self.update_self_model()
                    
                    # Generate improvement suggestions
                    suggestions = self.generate_self_improvement()
                    
                    # Log the suggestions
                    logger.info(f"Generated {len(suggestions.get('suggestions', []))} improvement suggestions")
                    
                    # Here you would implement code to actually apply the suggestions
                    # This would require more complex code generation and modification logic
                    
                except Exception as e:
                    logger.error(f"Error in continuous improvement cycle: {str(e)}")
                    time.sleep(3600)  # Wait an hour before retrying on error
        
        # Start the improvement thread
        improvement_thread = threading.Thread(target=improvement_cycle, daemon=True)
        improvement_thread.start()
        
        logger.info(f"Started continuous improvement cycle with {interval_hours} hour interval")
        return True