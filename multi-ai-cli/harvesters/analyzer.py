#!/usr/bin/env python3
"""Code Analyzer for analyzing extracted code."""
import os
import re
import ast
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict
from rich.console import Console

console = Console()

@dataclass
class AnalysisResult:
    """Result of code analysis."""
    functions: List[Dict] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    imports: List[Dict] = field(default_factory=list)
    variables: List[Dict] = field(default_factory=list)
    complexity: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    issues: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert the analysis result to a dictionary.
        
        Returns:
            Dict: A dictionary containing the analysis functions, classes, imports, variables, complexity metrics, dependencies, issues, and metadata.
        """
        return {
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "variables": self.variables,
            "complexity": self.complexity,
            "dependencies": self.dependencies,
            "issues": self.issues,
            "metadata": self.metadata,
        }

class CodeAnalyzer:
    """Analyzes code for structure, complexity, and issues."""
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        """
        Analyze source code and produce a structured analysis result.
        
        Parameters:
            code (str): Source code to analyze.
            language (str): Source language, such as ``"python"``, ``"javascript"``,
                or ``"java"``. Other values use generic analysis.
        
        Returns:
            AnalysisResult: Analysis data containing extracted entities, metadata,
                dependencies, complexity metrics, and any issues encountered.
        """
        result = AnalysisResult()
        result.metadata["language"] = language
        result.metadata["code_length"] = len(code)
        result.metadata["line_count"] = len(code.splitlines())
        
        try:
            if language == "python":
                self._analyze_python(code, result)
            elif language == "javascript":
                self._analyze_javascript(code, result)
            elif language == "java":
                self._analyze_java(code, result)
            else:
                # Generic analysis for any language
                self._analyze_generic(code, result)
        except Exception as e:
            result.issues.append({
                "type": "analysis_error",
                "message": str(e),
                "severity": "error",
            })
        
        return result
    
    def _analyze_python(self, code: str, result: AnalysisResult):
        """
        Analyze Python source code and populate the analysis result with extracted metadata, complexity metrics, imports, dependencies, and issues.
        
        Parameters:
            code (str): Python source code to analyze.
            result (AnalysisResult): Result object to populate with analysis data.
        
        Syntax errors are recorded as issues with error severity.
        """
        try:
            tree = ast.parse(code)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                    }
                    result.functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                        "methods": [],
                    }
                    
                    # Find methods in class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append({
                                "name": item.name,
                                "line": item.lineno,
                            })
                    
                    result.classes.append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result.imports.append({
                            "name": alias.name,
                            "asname": alias.asname,
                            "type": "import",
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        result.imports.append({
                            "name": alias.name,
                            "module": node.module,
                            "asname": alias.asname,
                            "type": "from_import",
                        })
            
            # Calculate complexity
            result.complexity = self._calculate_python_complexity(tree)
            
            # Extract dependencies
            result.dependencies = list(set([
                imp.get("name") or imp.get("module", "") 
                for imp in result.imports 
                if imp.get("name") or imp.get("module")
            ]))
            
        except SyntaxError as e:
            result.issues.append({
                "type": "syntax_error",
                "message": str(e),
                "severity": "error",
            })
    
    def _analyze_javascript(self, code: str, result: AnalysisResult):
        """Analyze JavaScript code and populate the result with detected functions, classes, imports, dependencies, and complexity metrics."""
        # Use regex-based analysis for JavaScript
        
        # Extract functions
        func_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
            
            result.functions.append({
                "name": func_name,
                "args": args,
                "type": "function",
            })
        
        # Extract arrow functions
        arrow_pattern = r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>'
        for match in re.finditer(arrow_pattern, code):
            func_name = match.group(1)
            args = [arg.strip() for arg in match.group(2).split(',') if arg.strip()]
            
            result.functions.append({
                "name": func_name,
                "args": args,
                "type": "arrow_function",
            })
        
        # Extract classes
        class_pattern = r'class\s+(\w+)\s*\{'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            result.classes.append({
                "name": class_name,
                "type": "class",
            })
        
        # Extract imports
        import_pattern = r'(?:import|require)\s*\(?["\']([^"\']+)["\']\)?'
        for match in re.finditer(import_pattern, code):
            module = match.group(1)
            if module not in result.dependencies:
                result.dependencies.append(module)
                result.imports.append({
                    "name": module,
                    "type": "import",
                })
        
        # Calculate complexity (simplified)
        result.complexity = {
            "functions": len(result.functions),
            "classes": len(result.classes),
            "imports": len(result.imports),
        }
    
    def _analyze_java(self, code: str, result: AnalysisResult):
        """
        Analyze Java source code and populate the analysis result with detected classes, methods, imports, dependencies, and complexity metrics.
        
        Parameters:
            code (str): Java source code to analyze.
            result (AnalysisResult): Object to populate with the analysis findings.
        """
        # Extract classes
        class_pattern = r'class\s+(\w+)\s*\{'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            result.classes.append({
                "name": class_name,
                "type": "class",
            })
        
        # Extract methods
        method_pattern = r'(?:public|private|protected|static|final|\s)+[\w<>\s]+(\w+)\s*\(([^)]*)\)\s*\{'
        for match in re.finditer(method_pattern, code):
            method_name = match.group(1)
            args = [arg.strip().split()[-1] for arg in match.group(2).split(',') if arg.strip()]
            
            result.functions.append({
                "name": method_name,
                "args": args,
                "type": "method",
            })
        
        # Extract imports
        import_pattern = r'import\s+([\w.]+);'
        for match in re.finditer(import_pattern, code):
            module = match.group(1)
            if module not in result.dependencies:
                result.dependencies.append(module)
                result.imports.append({
                    "name": module,
                    "type": "import",
                })
        
        # Calculate complexity
        result.complexity = {
            "classes": len(result.classes),
            "methods": len(result.functions),
            "imports": len(result.imports),
        }
    
    def _analyze_generic(self, code: str, result: AnalysisResult):
        """Collect basic size, word, comment, and complexity metrics for source code."""
        # Count lines and characters
        lines = code.splitlines()
        result.metadata["line_count"] = len(lines)
        result.metadata["char_count"] = len(code)
        
        # Count words
        words = re.findall(r'\w+', code)
        result.metadata["word_count"] = len(words)
        
        # Count comments
        comment_pattern = r'//.*|/\*.*?\*/|#.*|--.*'
        comments = re.findall(comment_pattern, code, re.DOTALL)
        result.metadata["comment_count"] = len(comments)
        
        # Simple complexity metric
        result.complexity = {
            "lines": len(lines),
            "words": len(words),
            "comments": len(comments),
        }
    
    def _calculate_python_complexity(self, tree: ast.AST) -> Dict:
        """
        Calculate structural and cyclomatic complexity metrics for a Python syntax tree.
        
        Parameters:
        	tree (ast.AST): Parsed Python syntax tree to analyze.
        
        Returns:
        	Dict: Metrics containing counts of functions, classes, and imports, along with nesting and cyclomatic complexity values.
        """
        metrics = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "nested_levels": 0,
            "max_nesting": 0,
            "cyclomatic": 1,  # Base complexity
        }
        
        # Count nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
                # Count decision points for cyclomatic complexity
                for item in ast.walk(node):
                    if isinstance(item, (ast.If, ast.For, ast.While, ast.And, ast.Or)):
                        metrics["cyclomatic"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["imports"] += 1
        
        return metrics
    
    def analyze_multiple(self, codes: List[Tuple[str, str]]) -> List[AnalysisResult]:
        """
        Analyze multiple code snippets using their specified languages.
        
        Parameters:
        	codes (List[Tuple[str, str]]): Code and language pairs to analyze.
        
        Returns:
        	List[AnalysisResult]: Analysis results in the same order as the input pairs.
        """
        results = []
        for code, language in codes:
            result = self.analyze(code, language)
            results.append(result)
        return results
    
    def compare_analyses(self, results: List[AnalysisResult]) -> Dict:
        """
        Summarize function, class, import, dependency, issue, and language counts across analysis results.
        
        Parameters:
            results (List[AnalysisResult]): Analysis results to compare.
        
        Returns:
            Dict: Aggregate counts and the languages represented in the results.
        """
        comparison = {
            "total_functions": sum(len(r.functions) for r in results),
            "total_classes": sum(len(r.classes) for r in results),
            "total_imports": sum(len(r.imports) for r in results),
            "total_dependencies": len(set(
                dep for r in results for dep in r.dependencies
            )),
            "total_issues": sum(len(r.issues) for r in results),
            "languages": [r.metadata.get("language", "unknown") for r in results],
        }
        return comparison

if __name__ == "__main__":
    # Example usage
    analyzer = CodeAnalyzer()
    
    # Test Python analysis
    python_code = """
def hello(name):
    '''Say hello'''
    print(f"Hello, {name}!")

def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
    """
    
    result = analyzer.analyze(python_code, "python")
    print("Analysis Result:")
    print(f"  Functions: {len(result.functions)}")
    print(f"  Classes: {len(result.classes)}")
    print(f"  Complexity: {result.complexity}")
    print(f"  Dependencies: {result.dependencies}")
