#!/usr/bin/env python3
"""Network utilities for HTTP requests and web operations."""
import os
import json
import time
from typing import List, Dict, Optional, Tuple, Any
from rich.console import Console
from curl_cffi import requests as curl_requests

console = Console()

class NetworkUtils:
    """Utilities for network operations."""
    
    def __init__(self):
        """Initialize network utilities."""
        self.session = curl_requests.Session()
        self._configure_session()
    
    def _configure_session(self):
        """Configure default session headers."""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
        })
    
    def get(self, url: str, headers: Dict = None, params: Dict = None, timeout: int = 30) -> Optional[Dict]:
        """
        Send a GET request and parse a successful response as JSON.
        
        Parameters:
        	url (str): The request URL.
        	headers (Dict): Optional headers to add to the session.
        	params (Dict): Optional query parameters.
        	timeout (int): Maximum time to wait for the request, in seconds.
        
        Returns:
        	Dict: The parsed JSON response, or a dictionary containing the raw response under `"content"`.
        	None: If the request fails or the response status code is not 200.
        """
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.get(url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except Exception:
                    return {"content": response.text}
            else:
                console.print(f"[red]GET {url} failed with status {response.status_code}: {response.text[:200]}[/]")
                return None
        except Exception as e:
            console.print(f"[red]GET {url} error: {e}[/]")
            return None
    
    def post(self, url: str, data: Dict = None, json_data: Dict = None, headers: Dict = None, timeout: int = 30) -> Optional[Dict]:
        """
        Send form-encoded or JSON data to a URL using a POST request.
        
        Parameters:
            url (str): The destination URL.
            data (Dict, optional): Form-encoded request data.
            json_data (Dict, optional): JSON request data.
            headers (Dict, optional): Additional request headers.
            timeout (int): Maximum time to wait for the request, in seconds.
        
        Returns:
            Optional[Dict]: The parsed response data, a dictionary containing raw response content when JSON parsing fails, or `None` when the request fails.
        """
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.post(url, data=data, json=json_data, timeout=timeout)
            
            if response.status_code in [200, 201]:
                try:
                    return response.json()
                except Exception:
                    return {"content": response.text}
            else:
                console.print(f"[red]POST {url} failed with status {response.status_code}: {response.text[:200]}[/]")
                return None
        except Exception as e:
            console.print(f"[red]POST {url} error: {e}[/]")
            return None
    
    def put(self, url: str, data: Dict = None, json_data: Dict = None, headers: Dict = None, timeout: int = 30) -> Optional[Dict]:
        """
        Send a PUT request and parse the successful response.
        
        Parameters:
            data (Dict): Form data to include in the request.
            json_data (Dict): JSON data to include in the request.
        
        Returns:
            Optional[Dict]: The parsed response data, or a dictionary containing the raw response text under ``"content"``; ``None`` if the request fails or returns an unsuccessful status.
        """
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.put(url, data=data, json=json_data, timeout=timeout)
            
            if response.status_code in [200, 201, 204]:
                try:
                    return response.json()
                except Exception:
                    return {"content": response.text}
            else:
                console.print(f"[red]PUT {url} failed with status {response.status_code}: {response.text[:200]}[/]")
                return None
        except Exception as e:
            console.print(f"[red]PUT {url} error: {e}[/]")
            return None
    
    def delete(self, url: str, headers: Dict = None, timeout: int = 30) -> bool:
        """
        Send a DELETE request to a URL.
        
        Parameters:
            headers (Dict): Optional headers to include with the request.
            timeout (int): Maximum time to wait for the request, in seconds.
        
        Returns:
            bool: `True` if the response status is 200, 201, or 204, `False` otherwise.
        """
        try:
            if headers:
                self.session.headers.update(headers)
            
            response = self.session.delete(url, timeout=timeout)
            
            if response.status_code in [200, 201, 204]:
                return True
            else:
                console.print(f"[red]DELETE {url} failed with status {response.status_code}: {response.text[:200]}[/]")
                return False
        except Exception as e:
            console.print(f"[red]DELETE {url} error: {e}[/]")
            return False
    
    def download_file(self, url: str, save_path: str, timeout: int = 60) -> bool:
        """
        Download a file from a URL and save it to the specified path.
        
        Parameters:
        	save_path (str): Destination path for the downloaded file.
        	timeout (int): Maximum time in seconds to wait for the request.
        
        Returns:
        	bool: `True` if the file was downloaded successfully, `False` otherwise.
        """
        try:
            response = self.session.get(url, timeout=timeout)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                console.print(f"[green]Downloaded {url} to {save_path}[/]")
                return True
            else:
                console.print(f"[red]Download failed with status {response.status_code}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Download error: {e}[/]")
            return False
    
    def check_url(self, url: str, timeout: int = 10) -> bool:
        """
        Check whether a URL is accessible.
        
        Parameters:
        	url (str): The URL to check.
        	timeout (int): Maximum time to wait for the response, in seconds.
        
        Returns:
        	bool: `True` if the response status code is below 400, `False` otherwise.
        """
        try:
            response = self.session.head(url, timeout=timeout)
            return response.status_code < 400
        except Exception:
            return False
    
    def get_with_retry(self, url: str, max_retries: int = 3, delay: float = 1.0, **kwargs) -> Optional[Dict]:
        """
        Attempt a GET request multiple times until it succeeds or the retry limit is reached.
        
        Parameters:
        	url (str): The URL to request.
        	max_retries (int): Maximum number of request attempts.
        	delay (float): Base delay in seconds between attempts.
        	**kwargs: Additional arguments passed to the GET request.
        
        Returns:
        	Dict or None: The first successful response data, or None if all attempts fail.
        """
        for attempt in range(max_retries):
            result = self.get(url, **kwargs)
            if result is not None:
                return result
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
        return None
    
    def post_with_retry(self, url: str, max_retries: int = 3, delay: float = 1.0, **kwargs) -> Optional[Dict]:
        """
        Send a POST request, retrying failed attempts with increasing delays.
        
        Parameters:
            max_retries (int): Maximum number of request attempts.
            delay (float): Base delay in seconds between retry attempts.
        
        Returns:
            Optional[Dict]: The first successful response, or None if all attempts fail.
        """
        for attempt in range(max_retries):
            result = self.post(url, **kwargs)
            if result is not None:
                return result
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
        return None
    
    def set_cookie(self, name: str, value: str, domain: str = None):
        """Set a cookie in the session."""
        self.session.cookies.set(name, value, domain=domain)
    
    def set_header(self, name: str, value: str):
        """Set a header in the session."""
        self.session.headers[name] = value
    
    def clear_cookies(self):
        """Clear all cookies."""
        self.session.cookies.clear()
    
    def clear_headers(self):
        """Clear all custom headers."""
        self._configure_session()

if __name__ == "__main__":
    # Example usage
    net = NetworkUtils()
    
    # Test GET request
    result = net.get("https://api.github.com")
    if result:
        print("GitHub API is accessible")
    
    # Test URL check
    if net.check_url("https://www.google.com"):
        print("Google is accessible")
