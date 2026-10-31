"""
Audit Agent
Technical audit agent for Antigravity.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any


class AuditAgent:
    """
    Technical audit agent for Antigravity.
    
    This agent performs:
    - Codebase analysis
    - Security audits
    - Performance analysis
    - Dependency checking
    - Vulnerability scanning
    """
    
    def __init__(self, session_manager = None):
        """
        Initialize audit agent.
        
        Args:
            session_manager: Session manager for Antigravity
        """
        self.session_manager = session_manager
        self._backend = None
        
    def _get_backend(self):
        """Get Antigravity backend."""
        if self._backend is None:
            from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
            self._backend = AntigravitySDKBackend(self.session_manager)
        return self._backend
    
    def audit_codebase(self, path: str = ".") -> Dict[str, Any]:
        """
        Audit a codebase.
        
        Args:
            path: Path to the codebase
            
        Returns:
            Audit report
        """
        try:
            # Build audit prompt
            prompt = f"""
Analyze the codebase at {path} and provide a comprehensive audit report.

Include the following sections:
1. **Code Quality**:
   - Code style and formatting
   - Naming conventions
   - Documentation quality
   - Code duplication

2. **Security**:
   - Potential vulnerabilities
   - Hardcoded secrets
   - Input validation
   - Authentication/authorization

3. **Performance**:
   - Algorithm efficiency
   - Resource usage
   - Bottlenecks
   - Scalability concerns

4. **Dependencies**:
   - Outdated packages
   - Vulnerable dependencies
   - Unused dependencies
   - License compatibility

5. **Architecture**:
   - Design patterns
   - Modularity
   - Separation of concerns
   - Maintainability

6. **Testing**:
   - Test coverage
   - Test quality
   - Edge cases
   - Integration tests

Provide specific, actionable recommendations for each issue found.
"""
            
            # Use Antigravity to analyze
            backend = self._get_backend()
            response = backend.send_message(prompt)
            
            # Parse response
            return {
                "status": "success",
                "path": path,
                "report": response,
                "type": "codebase_audit"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": path
            }
    
    def security_scan(self, path: str = ".") -> Dict[str, Any]:
        """
        Perform a security scan.
        
        Args:
            path: Path to scan
            
        Returns:
            Security scan report
        """
        try:
            prompt = f"""
Perform a comprehensive security scan of the codebase at {path}.

Focus on:
1. **Secrets Detection**:
   - API keys
   - Passwords
   - Tokens
   - Private keys
   - Sensitive data

2. **Vulnerability Analysis**:
   - SQL injection
   - XSS vulnerabilities
   - CSRF vulnerabilities
   - Authentication bypass
   - Privilege escalation

3. **Configuration Issues**:
   - Insecure defaults
   - Misconfigurations
   - Exposed debug endpoints
   - Verbose error messages

4. **Dependency Vulnerabilities**:
   - Known CVEs
   - Outdated packages
   - Vulnerable versions

5. **Code Patterns**:
   - eval() usage
   - exec() usage
   - pickle usage
   - shell=True in subprocess
   - Hardcoded credentials

Provide severity levels (Critical, High, Medium, Low) for each finding.
"""
            
            backend = self._get_backend()
            response = backend.send_message(prompt)
            
            return {
                "status": "success",
                "path": path,
                "report": response,
                "type": "security_scan"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": path
            }
    
    def performance_analysis(self, path: str = ".") -> Dict[str, Any]:
        """
        Perform a performance analysis.
        
        Args:
            path: Path to analyze
            
        Returns:
            Performance analysis report
        """
        try:
            prompt = f"""
Analyze the performance characteristics of the codebase at {path}.

Focus on:
1. **Time Complexity**:
   - Identify algorithms with high time complexity
   - Suggest optimizations
   - Big-O analysis

2. **Space Complexity**:
   - Memory usage patterns
   - Data structure efficiency
   - Caching opportunities

3. **I/O Operations**:
   - File I/O patterns
   - Network requests
   - Database queries
   - Blocking operations

4. **Resource Usage**:
   - CPU-intensive operations
   - Memory leaks
   - Resource contention
   - Parallelization opportunities

5. **Bottlenecks**:
   - Slowest operations
   - Frequent operations
   - N+1 query problems
   - Inefficient loops

Provide specific code examples and optimization suggestions.
"""
            
            backend = self._get_backend()
            response = backend.send_message(prompt)
            
            return {
                "status": "success",
                "path": path,
                "report": response,
                "type": "performance_analysis"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": path
            }
    
    def dependency_audit(self, requirements_path: str = "requirements.txt") -> Dict[str, Any]:
        """
        Audit dependencies.
        
        Args:
            requirements_path: Path to requirements file
            
        Returns:
            Dependency audit report
        """
        try:
            # Read requirements file
            req_path = Path(requirements_path)
            if not req_path.exists():
                return {
                    "status": "error",
                    "error": f"Requirements file not found: {requirements_path}",
                    "path": requirements_path
                }
            
            requirements = req_path.read_text()
            
            prompt = f"""
Analyze the following Python dependencies and provide a comprehensive audit:

{requirements}

Focus on:
1. **Version Analysis**:
   - Pinned vs. unpinned versions
   - Version ranges
   - Compatibility issues

2. **Security**:
   - Known vulnerabilities (CVE database)
   - Outdated packages
   - Security advisories

3. **License Compatibility**:
   - License types
   - Compatibility with project license
   - Restrictive licenses

4. **Maintenance**:
   - Abandoned packages
   - Last update dates
   - Maintenance status

5. **Optimizations**:
   - Redundant packages
   - Conflicting versions
   - Unused dependencies
   - Alternative packages

Provide specific recommendations for each dependency.
"""
            
            backend = self._get_backend()
            response = backend.send_message(prompt)
            
            return {
                "status": "success",
                "path": requirements_path,
                "report": response,
                "type": "dependency_audit",
                "dependencies": requirements
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "path": requirements_path
            }
    
    def patch_imports(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze and suggest patches for broken imports.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Patch suggestions
        """
        try:
            prompt = f"""
Analyze the following {language} code and identify broken imports.

For each broken import, provide:
1. The broken import statement
2. The reason it's broken (module not found, wrong version, etc.)
3. Suggested fix (correct import statement or installation command)

Code:
{code}

Provide a list of patches in JSON format:
{{
    "patches": [
        {{
            "line": <line_number>,
            "broken_import": "<broken_import_statement>",
            "reason": "<reason>",
            "fix": "<suggested_fix>"
        }}
    ]
}}
"""
            
            backend = self._get_backend()
            response = backend.send_message(prompt)
            
            # Try to parse JSON from response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "patches": response,
                    "raw_response": response
                }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
