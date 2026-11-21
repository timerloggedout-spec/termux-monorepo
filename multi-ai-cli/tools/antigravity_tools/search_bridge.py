"""
Search Bridge
Reverse-engineered search bridges for Antigravity.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any


class SearchBridge:
    """
    Search Bridge - Reverse-engineered search bridges for Antigravity.
    
    This module provides local execution overrides and search capabilities
    for Antigravity, including:
    - Web search
    - Code search
    - Documentation search
    - Custom search providers
    """
    
    def __init__(self, 
                 api_key: str = None,
                 session_manager = None,
                 search_provider: str = "google"):
        """
        Initialize search bridge.
        
        Args:
            api_key: API key for search provider
            session_manager: Session manager for Antigravity
            search_provider: Search provider to use ("google", "duckduckgo", "bing")
        """
        self.api_key = api_key or os.environ.get("SEARCH_API_KEY")
        self.session_manager = session_manager
        self.search_provider = search_provider
        self._backend = None
        
    def _get_backend(self):
        """Get Antigravity backend."""
        if self._backend is None:
            from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
            self._backend = AntigravitySDKBackend(self.session_manager)
        return self._backend
    
    def web_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            if self.search_provider == "google":
                return self._google_search(query, limit)
            elif self.search_provider == "duckduckgo":
                return self._duckduckgo_search(query, limit)
            elif self.search_provider == "bing":
                return self._bing_search(query, limit)
            else:
                # Use Antigravity's built-in search
                return self._antigravity_search(query, limit)
        except Exception as e:
            return [{"error": str(e), "query": query}]
    
    def _google_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Google search implementation."""
        try:
            if not self.api_key:
                # Use free API
                url = f"https://www.googleapis.com/customsearch/v1"
                params = {
                    "q": query,
                    "key": self.api_key,
                    "cx": os.environ.get("GOOGLE_CX", ""),
                    "num": limit
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", [])[:limit]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google"
                    })
                return results
            else:
                # Fallback to Antigravity
                return self._antigravity_search(query, limit)
        except Exception as e:
            return [{"error": str(e), "query": query, "source": "google"}]
    
    def _duckduckgo_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """DuckDuckGo search implementation."""
        try:
            import duckduckgo_search
            
            results = duckduckgo_search.search(query, max_results=limit)
            
            output = []
            for result in results:
                output.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })
            return output
        except ImportError:
            # Fallback to web scraping
            try:
                url = f"https://html.duckduckgo.com/html/"
                params = {"q": query}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                response = requests.post(url, data=params, headers=headers, timeout=10)
                
                # Parse HTML response
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = []
                for result in soup.select("div.result")[:limit]:
                    title_elem = result.select_one("a.result__url")
                    snippet_elem = result.select_one("a.result__snippet")
                    
                    if title_elem and snippet_elem:
                        results.append({
                            "title": title_elem.get_text(),
                            "url": title_elem.get("href", ""),
                            "snippet": snippet_elem.get_text(),
                            "source": "duckduckgo"
                        })
                return results
            except Exception:
                return self._antigravity_search(query, limit)
    
    def _bing_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Bing search implementation."""
        try:
            if self.api_key:
                url = f"https://api.bing.microsoft.com/v7.0/search"
                headers = {"Ocp-Apim-Subscription-Key": self.api_key}
                params = {"q": query, "count": limit}
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("webPages", {}).get("value", [])[:limit]:
                    results.append({
                        "title": item.get("name", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "bing"
                    })
                return results
            else:
                return self._antigravity_search(query, limit)
        except Exception as e:
            return [{"error": str(e), "query": query, "source": "bing"}]
    
    def _antigravity_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Use Antigravity's built-in search."""
        try:
            backend = self._get_backend()
            
            # Use Antigravity to perform search
            prompt = f"""
Perform a web search for: {query}

Return results in JSON format:
{{
    "results": [
        {{
            "title": "<title>",
            "url": "<url>",
            "snippet": "<snippet>",
            "source": "antigravity"
        }}
    ]
}}

Limit to {limit} results.
"""
            
            response = backend.send_message(prompt)
            
            # Try to parse JSON
            try:
                data = json.loads(response)
                return data.get("results", [])
            except json.JSONDecodeError:
                # Return as single result
                return [{
                    "title": "Antigravity Search",
                    "url": "",
                    "snippet": response,
                    "source": "antigravity"
                }]
        except Exception as e:
            return [{"error": str(e), "query": query, "source": "antigravity"}]
    
    def code_search(self, query: str, language: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a code search.
        
        Args:
            query: Search query
            language: Optional language filter
            limit: Maximum number of results
            
        Returns:
            List of code search results
        """
        try:
            backend = self._get_backend()
            
            language_str = f"Language: {language}" if language else ""
            prompt = f"""
Search for code examples matching: {query}

{language_str}

Return results in JSON format:
{{
    "results": [
        {{
            "title": "<description>",
            "code": "<code_snippet>",
            "language": "<language>",
            "source": "<source>",
            "url": "<url>"
        }}
    ]
}}

Limit to {limit} results.
"""
            
            response = backend.send_message(prompt)
            
            try:
                data = json.loads(response)
                return data.get("results", [])
            except json.JSONDecodeError:
                return [{
                    "title": "Code Search",
                    "code": response,
                    "language": language or "unknown",
                    "source": "antigravity",
                    "url": ""
                }]
        except Exception as e:
            return [{"error": str(e), "query": query}]
    
    def documentation_search(self, query: str, project: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search documentation.
        
        Args:
            query: Search query
            project: Optional project name
            limit: Maximum number of results
            
        Returns:
            List of documentation search results
        """
        try:
            backend = self._get_backend()
            
            project_str = f"Project: {project}" if project else ""
            prompt = f"""
Search documentation for: {query}

{project_str}

Return results in JSON format:
{{
    "results": [
        {{
            "title": "<documentation_title>",
            "content": "<documentation_content>",
            "url": "<url>",
            "source": "<source>"
        }}
    ]
}}

Limit to {limit} results.
"""
            
            response = backend.send_message(prompt)
            
            try:
                data = json.loads(response)
                return data.get("results", [])
            except json.JSONDecodeError:
                return [{
                    "title": "Documentation Search",
                    "content": response,
                    "url": "",
                    "source": "antigravity"
                }]
        except Exception as e:
            return [{"error": str(e), "query": query}]
    
    def local_search(self, query: str, path: str = ".", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a local file search.
        
        Args:
            query: Search query
            path: Path to search in
            limit: Maximum number of results
            
        Returns:
            List of local search results
        """
        try:
            from pathlib import Path
            
            search_path = Path(path)
            if not search_path.exists():
                return [{"error": f"Path not found: {path}", "query": query}]
            
            results = []
            
            # Recursively search files
            for file_path in search_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in [".py", ".js", ".ts", ".md", ".txt"]:
                    try:
                        content = file_path.read_text()
                        if query.lower() in content.lower():
                            # Find context around the match
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if query.lower() in line.lower():
                                    start = max(0, i - 2)
                                    end = min(len(lines), i + 3)
                                    context = '\n'.join(lines[start:end])
                                    
                                    results.append({
                                        "file": str(file_path),
                                        "line": i + 1,
                                        "context": context,
                                        "source": "local"
                                    })
                                    
                                    if len(results) >= limit:
                                        break
                    except Exception:
                        continue
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            return [{"error": str(e), "query": query, "path": path}]
