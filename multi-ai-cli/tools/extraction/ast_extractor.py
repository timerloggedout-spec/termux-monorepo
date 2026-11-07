#!/usr/bin/env python3
"""AST Extractor - Extract information using Abstract Syntax Trees.

This module provides functionality to:
- Parse code into AST
- Extract functions, classes, imports
- Analyze code structure
- Extract documentation
- Find references and dependencies
"""

import os
import sys
import json
import ast
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field


@dataclass
class ASTNode:
    """Represents an AST node with extracted information."""
    node_type: str
    name: str
    start_line: int
    end_line: int
    code: str
    children: List["ASTNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type,
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "code": self.code,
            "children": [c.to_dict() for c in self.children],
            "metadata": self.metadata,
        }


@dataclass
class ExtractedFunction:
    """Represents an extracted function."""
    name: str
    args: List[str]
    defaults: List[Any]
    docstring: Optional[str]
    body: str
    start_line: int
    end_line: int
    is_async: bool = False
    is_generator: bool = False
    decorators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "args": self.args,
            "defaults": self.defaults,
            "docstring": self.docstring,
            "body": self.body,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "is_async": self.is_async,
            "is_generator": self.is_generator,
            "decorators": self.decorators,
            "metadata": self.metadata,
        }


@dataclass
class ExtractedClass:
    """Represents an extracted class."""
    name: str
    bases: List[str]
    docstring: Optional[str]
    methods: List[ExtractedFunction] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    start_line: int
    end_line: int
    decorators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "bases": self.bases,
            "docstring": self.docstring,
            "methods": [m.to_dict() for m in self.methods],
            "attributes": self.attributes,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "decorators": self.decorators,
            "metadata": self.metadata,
        }


@dataclass
class ExtractedImport:
    """Represents an extracted import."""
    module: str
    names: List[str]
    aliases: Dict[str, str] = field(default_factory=dict)
    start_line: int
    is_from: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module,
            "names": self.names,
            "aliases": self.aliases,
            "start_line": self.start_line,
            "is_from": self.is_from,
        }


class ASTExtractor:
    """Extract information from code using AST.
    
    This extractor parses code into an Abstract Syntax Tree and extracts
    structured information about the code.
    """
    
    def __init__(
        self,
        language: str = "python",
        include_docstrings: bool = True,
        include_comments: bool = False,
        **kwargs
    ):
        """Initialize AST extractor.
        
        Args:
            language: Programming language (currently only Python supported)
            include_docstrings: Whether to extract docstrings
            include_comments: Whether to include comments in extracted code
        """
        self.language = language
        self.include_docstrings = include_docstrings
        self.include_comments = include_comments
    
    def extract(
        self,
        code: str,
        source: str = "",
    ) -> ASTNode:
        """Parse code and extract AST.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            Root ASTNode
        """
        if self.language != "python":
            raise NotImplementedError(f"Language {self.language} not yet supported")
        
        try:
            tree = ast.parse(code, filename=source)
            return self._build_ast_node(tree, source)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def _build_ast_node(self, node: ast.AST, source: str) -> ASTNode:
        """Build ASTNode from ast.AST node.
        
        Args:
            node: AST node
            source: Source identifier
            
        Returns:
            ASTNode
        """
        node_type = type(node).__name__
        name = ""
        
        # Get node name
        if hasattr(node, "name"):
            name = node.name
        elif hasattr(node, "id"):
            name = node.id
        elif hasattr(node, "attr"):
            name = node.attr
        
        # Get code
        try:
            code = ast.get_source_segment(source, node)
        except (TypeError, ValueError):
            code = ""
        
        # Build children
        children = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        children.append(self._build_ast_node(item, source))
            elif isinstance(value, ast.AST):
                children.append(self._build_ast_node(value, source))
        
        return ASTNode(
            node_type=node_type,
            name=name or node_type,
            start_line=node.lineno if hasattr(node, "lineno") else 0,
            end_line=node.end_lineno if hasattr(node, "end_lineno") else 0,
            code=code,
            children=children,
            metadata={
                "fields": {f: getattr(node, f) for f in node._fields},
            }
        )
    
    def extract_functions(
        self,
        code: str,
        source: str = "",
    ) -> List[ExtractedFunction]:
        """Extract all functions from code.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            List of ExtractedFunction objects
        """
        if self.language != "python":
            raise NotImplementedError(f"Language {self.language} not yet supported")
        
        try:
            tree = ast.parse(code, filename=source)
            return self._extract_functions_from_tree(tree, code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def _extract_functions_from_tree(
        self,
        tree: ast.AST,
        code: str,
    ) -> List[ExtractedFunction]:
        """Extract functions from AST tree.
        
        Args:
            tree: AST tree
            code: Original code
            
        Returns:
            List of ExtractedFunction objects
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = self._extract_function(node, code)
                functions.append(func)
            elif isinstance(node, ast.AsyncFunctionDef):
                func = self._extract_function(node, code)
                func.is_async = True
                functions.append(func)
        
        return functions
    
    def _extract_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        code: str,
    ) -> ExtractedFunction:
        """Extract function information from AST node.
        
        Args:
            node: Function AST node
            code: Original code
            
        Returns:
            ExtractedFunction
        """
        # Extract arguments
        args = []
        defaults = []
        
        for arg in node.args.args:
            args.append(arg.arg)
        
        for default in node.args.defaults:
            try:
                defaults.append(ast.literal_eval(default))
            except Exception:
                defaults.append(None)
        
        # Extract docstring
        docstring = None
        if self.include_docstrings and ast.get_docstring(node):
            docstring = ast.get_docstring(node)
        
        # Extract body
        try:
            body_start = node.body[0].lineno if node.body else node.lineno
            body_end = node.end_lineno
            body_lines = code.splitlines()[body_start - 1:body_end]
            body = "\n".join(body_lines)
        except Exception:
            body = ""
        
        # Check if generator
        is_generator = any(
            isinstance(n, ast.Yield) or isinstance(n, ast.YieldFrom)
            for n in ast.walk(node)
        )
        
        # Extract decorators
        decorators = [d.id if hasattr(d, "id") else str(d) for d in node.decorator_list]
        
        return ExtractedFunction(
            name=node.name,
            args=args,
            defaults=defaults,
            docstring=docstring,
            body=body,
            start_line=node.lineno,
            end_line=node.end_lineno,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_generator=is_generator,
            decorators=decorators,
            metadata={
                "arg_count": len(args),
                "has_vararg": node.args.vararg is not None,
                "has_kwarg": node.args.kwarg is not None,
            }
        )
    
    def extract_classes(
        self,
        code: str,
        source: str = "",
    ) -> List[ExtractedClass]:
        """Extract all classes from code.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            List of ExtractedClass objects
        """
        if self.language != "python":
            raise NotImplementedError(f"Language {self.language} not yet supported")
        
        try:
            tree = ast.parse(code, filename=source)
            return self._extract_classes_from_tree(tree, code)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def _extract_classes_from_tree(
        self,
        tree: ast.AST,
        code: str,
    ) -> List[ExtractedClass]:
        """Extract classes from AST tree.
        
        Args:
            tree: AST tree
            code: Original code
            
        Returns:
            List of ExtractedClass objects
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls = self._extract_class(node, code)
                classes.append(cls)
        
        return classes
    
    def _extract_class(
        self,
        node: ast.ClassDef,
        code: str,
    ) -> ExtractedClass:
        """Extract class information from AST node.
        
        Args:
            node: Class AST node
            code: Original code
            
        Returns:
            ExtractedClass
        """
        # Extract bases
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{ast.unparse(base)}")
            else:
                bases.append(ast.unparse(base))
        
        # Extract docstring
        docstring = None
        if self.include_docstrings and ast.get_docstring(node):
            docstring = ast.get_docstring(node)
        
        # Extract methods
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function(item, code))
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes.append(item.target.id)
        
        # Extract decorators
        decorators = [d.id if hasattr(d, "id") else str(d) for d in node.decorator_list]
        
        return ExtractedClass(
            name=node.name,
            bases=bases,
            docstring=docstring,
            methods=methods,
            attributes=attributes,
            start_line=node.lineno,
            end_line=node.end_lineno,
            decorators=decorators,
            metadata={
                "method_count": len(methods),
                "attribute_count": len(attributes),
            }
        )
    
    def extract_imports(
        self,
        code: str,
        source: str = "",
    ) -> List[ExtractedImport]:
        """Extract all imports from code.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            List of ExtractedImport objects
        """
        if self.language != "python":
            raise NotImplementedError(f"Language {self.language} not yet supported")
        
        try:
            tree = ast.parse(code, filename=source)
            return self._extract_imports_from_tree(tree)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def _extract_imports_from_tree(
        self,
        tree: ast.AST,
    ) -> List[ExtractedImport]:
        """Extract imports from AST tree.
        
        Args:
            tree: AST tree
            
        Returns:
            List of ExtractedImport objects
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ExtractedImport(
                        module=alias.name,
                        names=[alias.name],
                        aliases={alias.name: alias.asname} if alias.asname else {},
                        start_line=node.lineno,
                        is_from=False,
                    ))
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                aliases = {
                    alias.name: alias.asname
                    for alias in node.names
                    if alias.asname
                }
                imports.append(ExtractedImport(
                    module=node.module,
                    names=names,
                    aliases=aliases,
                    start_line=node.lineno,
                    is_from=True,
                ))
        
        return imports
    
    def extract_dependencies(
        self,
        code: str,
        source: str = "",
    ) -> Dict[str, List[str]]:
        """Extract dependencies from code.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            Dictionary mapping dependency types to lists
        """
        imports = self.extract_imports(code, source)
        
        dependencies = {
            "modules": [],
            "packages": [],
            "builtins": [],
        }
        
        # Python builtins
        builtins = {
            "os", "sys", "json", "re", "time", "datetime", "math", "random",
            "collections", "itertools", "functools", "operator", "copy",
            "pathlib", "argparse", "subprocess", "signal", "threading",
            "asyncio", "concurrent", "multiprocessing", "queue",
            "http", "urllib", "socket", "ssl", "email",
            "logging", "traceback", "warnings", "contextlib",
            "abc", "typing", "dataclasses", "enum",
        }
        
        for imp in imports:
            if imp.is_from:
                if imp.module in builtins:
                    dependencies["builtins"].append(imp.module)
                else:
                    dependencies["packages"].append(imp.module)
            else:
                for name in imp.names:
                    if name in builtins:
                        dependencies["builtins"].append(name)
                    else:
                        dependencies["modules"].append(name)
        
        # Remove duplicates
        for key in dependencies:
            dependencies[key] = list(set(dependencies[key]))
        
        return dependencies
    
    def extract_to_dict(
        self,
        code: str,
        source: str = "",
    ) -> Dict[str, Any]:
        """Extract all information and return as dictionary.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            Dictionary with all extracted information
        """
        return {
            "ast": self.extract(code, source).to_dict(),
            "functions": [f.to_dict() for f in self.extract_functions(code, source)],
            "classes": [c.to_dict() for c in self.extract_classes(code, source)],
            "imports": [i.to_dict() for i in self.extract_imports(code, source)],
            "dependencies": self.extract_dependencies(code, source),
        }
    
    def extract_to_json(
        self,
        code: str,
        source: str = "",
    ) -> str:
        """Extract all information and return as JSON.
        
        Args:
            code: Code to parse
            source: Source identifier
            
        Returns:
            JSON string
        """
        return json.dumps(self.extract_to_dict(code, source), indent=2)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ASTExtractor",
    "ASTNode",
    "ExtractedFunction",
    "ExtractedClass",
    "ExtractedImport",
]
