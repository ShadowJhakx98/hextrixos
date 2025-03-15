"""
Autonomous code improvement system with multi-objective optimization
"""
import ast
import inspect
from typing import Dict, List, Tuple
import libcst as cst
from pathlib import Path
from collections import defaultdict
import radon
from radon.complexity import cc_rank
from radon.metrics import mi_rank

class CodeAnalyzer:
    def __init__(self):
        self.metrics = {}
        self.smell_patterns = self._load_smell_patterns()
        
    def _load_smell_patterns(self) -> Dict:
        return {
            'long_method': {'threshold': 15, 'metric': 'cyclomatic'},
            'duplicate_code': {'threshold': 0.3, 'metric': 'similarity'},
            'complex_conditional': {'pattern': 'if.*&&|\|\|'},
            'primitive_obsession': {'types': ['int', 'str', 'bool']}
        }
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Perform deep code analysis with multiple metrics"""
        with open(file_path, 'r') as f:
            code = f.read()
            
        tree = ast.parse(code)
        
        analysis = {
            'complexity': self._calculate_complexity(tree),
            'maintainability': self._calculate_maintainability(code),
            'test_coverage': self._estimate_test_coverage(file_path),
            'security_risks': self._find_security_issues(tree),
            'performance_issues': self._find_performance_anti_patterns(tree)
        }
        
        self.metrics[file_path] = analysis
        return analysis
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict:
        """Calculate cyclomatic complexity metrics"""
        complexities = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                complexity = cc_rank(ast.unparse(node))
                complexities.append({
                    'name': node.name,
                    'complexity': complexity,
                    'grade': cc_rank(complexity)
                })
        return complexities
    
    def _calculate_maintainability(self, code: str) -> float:
        """Compute maintainability index with Radon metrics"""
        mi = radon.metrics.mi_parameters(code)
        return mi['mi']
    
    def _estimate_test_coverage(self, file_path: Path) -> float:
        """Integrate with coverage.py data if available"""
        # Implementation would connect to coverage data
        return 0.85  # Placeholder
    
    def _find_security_issues(self, tree: ast.AST) -> List[str]:
        """Detect common security anti-patterns"""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id in ['eval', 'exec']):
                    issues.append(f"Dangerous function call: {node.func.id}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['pickle', 'marshal']:
                        issues.append(f"Potentially unsafe import: {alias.name}")
        return issues
    
    def _find_performance_anti_patterns(self, tree: ast.AST) -> List[str]:
        """Identify performance-critical code issues"""
        patterns = [
            ('nested_loops', self._detect_nested_loops),
            ('quadratic_complexity', self._detect_quadratic_ops)
        ]
        issues = []
        for pattern_name, detector in patterns:
            if detector(tree):
                issues.append(pattern_name)
        return issues

class CodeRefactorer:
    def __init__(self):
        self.transformations = self._load_refactoring_rules()
        
    def improve_code(self, code: str, analysis: Dict) -> str:
        """Apply optimized transformations based on analysis"""
        wrapper = cst.parse_module(code)
        
        for smell in analysis.get('smells', []):
            transformer = self.transformations.get(smell['type'])
            if transformer:
                wrapper = wrapper.visit(transformer())
                
        return wrapper.code
    
    def _load_refactoring_rules(self) -> Dict:
        return {
            'long_method': SplitMethodTransformer,
            'duplicate_code': DeduplicateCodeTransformer,
            'complex_conditional': SimplifyConditionalTransformer
        }

class AutofixTransformer(cst.CSTTransformer):
    def __init__(self, issue_type):
        self.issue_type = issue_type
        self.changes = []
        
    def leave_FunctionDef(self, original_node, updated_node):
        if self.issue_type == 'long_method':
            return self._split_long_method(updated_node)
        return updated_node
    
    def _split_long_method(self, node):
        # Implementation would analyze and split method
        return node

class CodeImprover:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.refactorer = CodeRefactorer()
        self.optimization_history = defaultdict(list)
        
    def optimize_project(self, project_path: Path):
        """Run full optimization pipeline across project"""
        for py_file in project_path.glob('**/*.py'):
            analysis = self.analyzer.analyze_file(py_file)
            improved_code = self.refactorer.improve_code(
                py_file.read_text(), analysis)
            
            py_file.write_text(improved_code)
            self.optimization_history[py_file].append({
                'original_metrics': analysis,
                'new_metrics': self.analyzer.analyze_file(py_file)
            })
            
    def generate_report(self) -> str:
        """Create optimization summary report"""
        report = ["Code Optimization Report\n"]
        for file, history in self.optimization_history.items():
            original = history[0]['original_metrics']
            new = history[-1]['new_metrics']
            
            report.append(f"File: {file.name}")
            report.append(f"  Maintainability: {original['maintainability']} → {new['maintainability']}")
            report.append(f"  Complexity: {len(original['complexity'])} → {len(new['complexity'])}")
        return "\n".join(report)
