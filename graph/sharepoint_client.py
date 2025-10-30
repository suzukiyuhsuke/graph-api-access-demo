"""
SharePoint Graph API Client.

This module provides a client for interacting with SharePoint sites
using Microsoft Graph API.
"""

import os
import requests
from typing import List, Dict, Optional
from urllib.parse import quote


class SharePointClient:
    """Client for accessing SharePoint sites via Microsoft Graph API."""
    
    def __init__(self, access_token: str):
        """
        Initialize SharePoint client.
        
        Args:
            access_token: OAuth access token for Graph API
        """
        self.access_token = access_token
        self.graph_endpoint = os.getenv(
            "GRAPH_API_ENDPOINT",
            "https://graph.microsoft.com/v1.0"
        )
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, url: str) -> Dict:
        """
        Make a GET request to Graph API.
        
        Args:
            url: Full URL to request
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If the request fails
        """
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Graph API request failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_details = error_data.get("error", {})
                error_msg += f": {error_details.get('message', response.text)}"
            except:
                error_msg += f": {response.text}"
            
            raise Exception(error_msg)
    
    def get_site_id_by_url(self, site_url: str) -> str:
        """
        Get SharePoint site ID from site URL.
        
        Args:
            site_url: SharePoint site URL (e.g., https://tenant.sharepoint.com/sites/sitename)
            
        Returns:
            Site ID string
        """
        # Extract hostname and site path from URL
        # Example: https://tenant.sharepoint.com/sites/sitename
        parts = site_url.replace("https://", "").replace("http://", "").split("/", 1)
        hostname = parts[0]
        site_path = "/" + parts[1] if len(parts) > 1 else ""
        
        # Construct Graph API URL
        url = f"{self.graph_endpoint}/sites/{hostname}:{site_path}"
        
        site_data = self._make_request(url)
        return site_data.get("id")
    
    def list_files(
        self,
        site_url: str,
        folder_path: Optional[str] = None
    ) -> List[Dict]:
        """
        List files and folders from a SharePoint site.
        
        Args:
            site_url: SharePoint site URL
            folder_path: Optional folder path within the site (e.g., "Documents/Subfolder")
            
        Returns:
            List of file/folder dictionaries
        """
        # Get site ID
        site_id = self.get_site_id_by_url(site_url)
        
        # Construct URL for drive items
        if folder_path:
            # List items in specific folder
            encoded_path = quote(folder_path)
            url = f"{self.graph_endpoint}/sites/{site_id}/drive/root:/{encoded_path}:/children"
        else:
            # List items in root
            url = f"{self.graph_endpoint}/sites/{site_id}/drive/root/children"
        
        response_data = self._make_request(url)
        items = response_data.get("value", [])
        
        # Format the response
        files = []
        for item in items:
            file_info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "size": item.get("size", 0),
                "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                "webUrl": item.get("webUrl"),
                "folder": "folder" in item
            }
            files.append(file_info)
        
        return files
    
    def get_file_content(self, site_url: str, file_path: str) -> bytes:
        """
        Download file content from SharePoint.
        
        Args:
            site_url: SharePoint site URL
            file_path: Path to the file within the site
            
        Returns:
            File content as bytes
        """
        site_id = self.get_site_id_by_url(site_url)
        encoded_path = quote(file_path)
        
        url = f"{self.graph_endpoint}/sites/{site_id}/drive/root:/{encoded_path}:/content"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download file: {response.status_code}")
    
    def search_files(self, site_url: str, query: str) -> List[Dict]:
        """
        Search for files in a SharePoint site.
        
        Args:
            site_url: SharePoint site URL
            query: Search query string
            
        Returns:
            List of matching file/folder dictionaries
        """
        site_id = self.get_site_id_by_url(site_url)
        encoded_query = quote(query)
        
        url = f"{self.graph_endpoint}/sites/{site_id}/drive/root/search(q='{encoded_query}')"
        
        response_data = self._make_request(url)
        items = response_data.get("value", [])
        
        # Format the response
        files = []
        for item in items:
            file_info = {
                "id": item.get("id"),
                "name": item.get("name"),
                "size": item.get("size", 0),
                "lastModifiedDateTime": item.get("lastModifiedDateTime"),
                "webUrl": item.get("webUrl"),
                "folder": "folder" in item
            }
            files.append(file_info)
        
        return files
