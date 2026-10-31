#!/usr/bin/env python3
"""Colab Notebook - Advanced notebook manipulation and analysis.

This module provides:
- Notebook parsing and manipulation
- Cell analysis
- Code extraction
- Dependency analysis
- Notebook metadata management
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator
from dataclasses import dataclass, field

from .colab_backend import ColabNotebook, ColabCell
from tools.extraction.code_extractor import CodeExtractor
from tools.extraction.ast_extractor import ASTExtractor
from tools.extraction.pattern_extractor import PatternExtractor


@dataclass
class NotebookAnalysis:
    """Analysis of a Colab notebook."""
    notebook_id: str
    name: str
    cell_count: int
    code_cell_count: int
    markdown_cell_count: int
    code_lines: int
    comment_lines: int
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "notebook_id": self.notebook_id,
            "name": self.name,
            "cell_count": self.cell_count,
            "code_cell_count": self.code_cell_count,
            "markdown_cell_count": self.markdown_cell_count,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


class ColabNotebookManager:
    """Advanced notebook manager for Colab.
    
    This manager provides:
    - Notebook analysis
    - Code extraction
    - Dependency analysis
    - Notebook manipulation
    """
    
    def __init__(
        self,
        notebook: Optional[ColabNotebook] = None,
        notebook_id: Optional[str] = None,
        **kwargs
    ):
        """Initialize notebook manager.
        
        Args:
            notebook: ColabNotebook to manage
            notebook_id: Notebook ID to load
        """
        self.notebook = notebook
        self.notebook_id = notebook_id
        self._code_extractor = CodeExtractor()
        self._ast_extractor = ASTExtractor()
        self._pattern_extractor = PatternExtractor()
        self._backend = kwargs.get("backend")
    
    def load(self, notebook_id: Optional[str] = None) -> ColabNotebook:
        """Load a notebook.
        
        Args:
            notebook_id: Notebook ID to load
            
        Returns:
            Loaded ColabNotebook
        """
        notebook_id = notebook_id or self.notebook_id
        
        if self._backend:
            self.notebook = self._backend.get_notebook(notebook_id)
        else:
            raise ValueError("Backend required to load notebook")
        
        return self.notebook
    
    def save(self, notebook: Optional[ColabNotebook] = None) -> bool:
        """Save a notebook.
        
        Args:
            notebook: Notebook to save
            
        Returns:
            True if successful
        """
        notebook = notebook or self.notebook
        
        if self._backend:
            return self._backend.save_notebook(notebook)
        
        raise ValueError("Backend required to save notebook")
    
    def analyze(self, notebook: Optional[ColabNotebook] = None) -> NotebookAnalysis:
        """Analyze a notebook.
        
        Args:
            notebook: Notebook to analyze
            
        Returns:
            NotebookAnalysis object
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        code_cell_count = sum(1 for c in notebook.cells if c.cell_type == "code")
        markdown_cell_count = sum(1 for c in notebook.cells if c.cell_type == "markdown")
        
        code_lines = 0
        comment_lines = 0
        functions = []
        classes = []
        imports = []
        dependencies = {}
        
        for cell in notebook.cells:
            if cell.cell_type == "code":
                source = cell.source if isinstance(cell.source, str) else "\n".join(cell.source)
                
                # Count lines
                lines = source.splitlines()
                code_lines += len(lines)
                
                # Count comments
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                        comment_lines += 1
                
                # Extract code
                code_blocks = self._code_extractor.extract(source)
                for block in code_blocks:
                    if block.language == "python":
                        # Extract functions and classes using AST
                        try:
                            ast_data = self._ast_extractor.extract_to_dict(source)
                            for func in ast_data.get("functions", []):
                                functions.append(func.get("name", ""))
                            for cls in ast_data.get("classes", []):
                                classes.append(cls.get("name", ""))
                            for imp in ast_data.get("imports", []):
                                imports.append(imp.get("module", ""))
                            dependencies.update(ast_data.get("dependencies", {}))
                        except Exception:
                            pass
        
        return NotebookAnalysis(
            notebook_id=notebook.notebook_id,
            name=notebook.name,
            cell_count=len(notebook.cells),
            code_cell_count=code_cell_count,
            markdown_cell_count=markdown_cell_count,
            code_lines=code_lines,
            comment_lines=comment_lines,
            functions=list(set(functions)),
            classes=list(set(classes)),
            imports=list(set(imports)),
            dependencies=dependencies,
            metadata=notebook.metadata,
        )
    
    def extract_code(self, notebook: Optional[ColabNotebook] = None) -> List[Dict[str, Any]]:
        """Extract all code from a notebook.
        
        Args:
            notebook: Notebook to extract from
            
        Returns:
            List of code blocks with metadata
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        code_blocks = []
        
        for i, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                source = cell.source if isinstance(cell.source, str) else "\n".join(cell.source)
                
                # Extract code blocks
                blocks = self._code_extractor.extract(source, source=f"cell_{i}")
                for block in blocks:
                    code_blocks.append({
                        "cell_index": i,
                        "cell_type": cell.cell_type,
                        "code": block.code,
                        "language": block.language,
                        "source": block.source,
                    })
        
        return code_blocks
    
    def search(
        self,
        query: str,
        notebook: Optional[ColabNotebook] = None,
        pattern: bool = False,
        regex: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search in notebook content.
        
        Args:
            query: Search query
            notebook: Notebook to search
            pattern: Whether query is a pattern
            regex: Whether query is a regex
            
        Returns:
            List of search results
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        results = []
        
        for i, cell in enumerate(notebook.cells):
            source = cell.source if isinstance(cell.source, str) else "\n".join(cell.source)
            
            # Search in cell content
            lines = source.splitlines()
            for j, line in enumerate(lines):
                if self._match_line(line, query, pattern, regex):
                    results.append({
                        "cell_index": i,
                        "cell_type": cell.cell_type,
                        "line_number": j + 1,
                        "line": line,
                        "context": lines[max(0, j-2):min(len(lines), j+3)],
                    })
        
        return results
    
    def _match_line(self, line: str, query: str, pattern: bool, regex: bool) -> bool:
        """Check if line matches query."""
        if regex:
            try:
                return bool(re.search(query, line))
            except Exception:
                return False
        
        if pattern:
            import fnmatch
            return fnmatch.fnmatch(line, query)
        
        return query.lower() in line.lower()
    
    def add_cell(
        self,
        cell_type: str = "code",
        source: Union[str, List[str]] = "",
        notebook: Optional[ColabNotebook] = None,
    ) -> ColabCell:
        """Add a cell to a notebook.
        
        Args:
            cell_type: Cell type
            source: Cell source
            notebook: Notebook to add to
            
        Returns:
            Added cell
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        cell = ColabCell(
            cell_type=cell_type,
            source=source,
            metadata={},
        )
        notebook.cells.append(cell)
        
        return cell
    
    def remove_cell(
        self,
        index: int,
        notebook: Optional[ColabNotebook] = None,
    ) -> ColabCell:
        """Remove a cell from a notebook.
        
        Args:
            index: Cell index to remove
            notebook: Notebook to remove from
            
        Returns:
            Removed cell
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        if index < 0 or index >= len(notebook.cells):
            raise IndexError("Cell index out of range")
        
        return notebook.cells.pop(index)
    
    def move_cell(
        self,
        from_index: int,
        to_index: int,
        notebook: Optional[ColabNotebook] = None,
    ) -> bool:
        """Move a cell in a notebook.
        
        Args:
            from_index: Current cell index
            to_index: New cell index
            notebook: Notebook to modify
            
        Returns:
            True if successful
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        if from_index < 0 or from_index >= len(notebook.cells):
            raise IndexError("From index out of range")
        if to_index < 0 or to_index >= len(notebook.cells):
            raise IndexError("To index out of range")
        
        cell = notebook.cells.pop(from_index)
        notebook.cells.insert(to_index, cell)
        
        return True
    
    def get_cell(self, index: int, notebook: Optional[ColabNotebook] = None) -> ColabCell:
        """Get a cell from a notebook.
        
        Args:
            index: Cell index
            notebook: Notebook to get from
            
        Returns:
            Cell at index
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        if index < 0 or index >= len(notebook.cells):
            raise IndexError("Cell index out of range")
        
        return notebook.cells[index]
    
    def set_cell_source(
        self,
        index: int,
        source: Union[str, List[str]],
        notebook: Optional[ColabNotebook] = None,
    ) -> bool:
        """Set cell source.
        
        Args:
            index: Cell index
            source: New source
            notebook: Notebook to modify
            
        Returns:
            True if successful
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        if index < 0 or index >= len(notebook.cells):
            raise IndexError("Cell index out of range")
        
        notebook.cells[index].source = source
        
        return True
    
    def convert_to_python(self, notebook: Optional[ColabNotebook] = None) -> str:
        """Convert notebook to Python script.
        
        Args:
            notebook: Notebook to convert
            
        Returns:
            Python script
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        script = []
        
        for cell in notebook.cells:
            if cell.cell_type == "code":
                source = cell.source if isinstance(cell.source, str) else "\n".join(cell.source)
                script.append(source)
            elif cell.cell_type == "markdown":
                source = cell.source if isinstance(cell.source, str) else "\n".join(cell.source)
                # Convert markdown to comments
                script.append(f'"""{source}"""')
        
        return "\n\n".join(script)
    
    def export_to_file(
        self,
        path: Union[str, Path],
        notebook: Optional[ColabNotebook] = None,
        format: str = "python",
    ) -> bool:
        """Export notebook to file.
        
        Args:
            path: Export path
            notebook: Notebook to export
            format: Export format ("python", "json", "ipynb")
            
        Returns:
            True if successful
        """
        notebook = notebook or self.notebook
        if not notebook:
            raise ValueError("Notebook not loaded")
        
        path = Path(path)
        
        if format == "python":
            content = self.convert_to_python(notebook)
        elif format == "json":
            content = notebook.to_json()
        elif format == "ipynb":
            content = json.dumps(notebook.to_dict(), indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")
        
        path.write_text(content, encoding="utf-8")
        
        return True


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ColabNotebookManager",
    "NotebookAnalysis",
]
