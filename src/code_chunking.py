"""
Advanced AST-based code chunking with semantic preservation
Combining search results [1], [3], and [6] with enhanced merging
"""

import ast
import os
from typing import List, Dict, Tuple
from pathlib import Path
import hashlib
from collections import deque

class CodeChunker:
    def __init__(self, max_size: int = 1000, context_lines: int = 3):
        self.max_size = max_size  # Target chunk size in lines
        self.context_lines = context_lines
        self.node_priorities = {
            ast.FunctionDef: 1,
            ast.ClassDef: 2,
            ast.Import: 3,
            ast.ImportFrom: 3,
            ast.AsyncFunctionDef: 1
        }

    def chunk_code(self, code: str, filepath: str) -> List[Dict]:
        """Semantic code chunking with AST analysis"""
        tree = ast.parse(code)
        chunks = []
        current_chunk = []
        current_size = 0
        context_buffer = deque(maxlen=self.context_lines)
        
        for node in ast.walk(tree):
            node_lines = self._get_node_lines(node, code)
            if not node_lines:
                continue
                
            # Calculate priority based on node type and dependencies
            priority = self.node_priorities.get(type(node), 0)
            chunk_candidate = current_chunk.copy()
            
            # Try adding node to current chunk
            if current_size + len(node_lines) <= self.max_size:
                current_chunk.append((node, node_lines, priority))
                current_size += len(node_lines)
                context_buffer.extend(node_lines)
            else:
                # Finalize current chunk
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, filepath, context_buffer))
                    current_chunk = []
                    current_size = 0
                
                # Start new chunk with current node
                current_chunk.append((node, node_lines, priority))
                current_size += len(node_lines)
                context_buffer = deque(node_lines, maxlen=self.context_lines)

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, filepath, context_buffer))
            
        return chunks

    def _create_chunk(self, nodes: List, filepath: str, context: deque) -> Dict:
        """Package chunk with metadata"""
        code_lines = []
        for node, lines, _ in sorted(nodes, key=lambda x: x[2], reverse=True):
            code_lines.extend(lines)
            
        return {
            'hash': hashlib.sha256('\n'.join(code_lines).encode()).hexdigest(),
            'content': '\n'.join(code_lines),
            'filepath': filepath,
            'context': list(context),
            'ast_types': [type(n[0]).__name__ for n in nodes],
            'size': len(code_lines)
        }

    def _get_node_lines(self, node: ast.AST, code: str) -> List[str]:
        """Extract lines for an AST node with context"""
        lines = code.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        return [line.strip() for line in lines[start_line:end_line]]

    def merge_chunks(self, chunks: List[Dict], original_path: str) -> str:
        """Context-aware chunk recombination"""
        reconstructed = []
        last_line = 0
        
        for chunk in sorted(chunks, key=lambda x: self._get_chunk_position(x, original_path)):
            # Handle gaps between chunks
            current_start = self._get_first_line(chunk['content'])
            if current_start > last_line + 1:
                gap = current_start - last_line - 1
                reconstructed.append(f"# ... {gap} lines omitted ...")
                
            reconstructed.append(chunk['content'])
            last_line = current_start + chunk['size'] - 1
            
        return '\n'.join(reconstructed)

    def _get_chunk_position(self, chunk: Dict, filepath: str) -> int:
        """Get original file position from context"""
        with open(filepath, 'r') as f:
            content = f.read().split('\n')
            for idx, line in enumerate(content):
                if chunk['context'] and line.strip() == chunk['context'][0].strip():
                    return idx
        return 0

    def save_chunks(self, chunks: List[Dict], base_path: str) -> None:
        """Save chunks with metadata as JSON"""
        import json
        output_dir = Path(base_path).parent / 'chunks'
        output_dir.mkdir(exist_ok=True)
        
        for idx, chunk in enumerate(chunks):
            chunk_file = output_dir / f"{Path(base_path).stem}_chunk{idx+1}.json"
            with open(chunk_file, 'w') as f:
                json.dump(chunk, f, indent=2)

    def load_chunks(self, base_path: str) -> List[Dict]:
        """Load chunks from JSON files"""
        import json
        chunks = []
        chunk_dir = Path(base_path).parent / 'chunks'
        
        for chunk_file in chunk_dir.glob(f"{Path(base_path).stem}_chunk*.json"):
            with open(chunk_file, 'r') as f:
                chunks.append(json.load(f))
                
        return sorted(chunks, key=lambda x: x['hash'])

class ASTProcessor:
    """Enhanced from search result [1] with dependency analysis"""
    def __init__(self):
        self.dependencies = {}
        self.import_map = {}

    def analyze_dependencies(self, chunk: Dict) -> List[str]:
        """Extract imports and cross-chunk references"""
        imports = []
        tree = ast.parse(chunk['content'])
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(self._process_import(node))
            elif isinstance(node, ast.Call):
                self._process_call(node)
                
        return list(set(imports))

    def _process_import(self, node: ast.AST) -> List[str]:
        imports = []
        for alias in node.names:
            fullname = alias.name
            if isinstance(node, ast.ImportFrom) and node.module:
                fullname = f"{node.module}.{alias.name}"
            imports.append(fullname)
            self.import_map[alias.asname or alias.name] = fullname
        return imports

    def _process_call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.import_map:
                self.dependencies.setdefault(func_name, []).append(
                    self.import_map[func_name]
                )
