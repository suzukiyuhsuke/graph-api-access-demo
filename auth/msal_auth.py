"""
MSAL authentication module for local development.

This module handles authentication using the MSAL (Microsoft Authentication Library)
for local development scenarios.
"""

import os
import msal
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = os.getenv("AUTHORITY", "https://login.microsoftonline.com/") + (TENANT_ID or "")
SCOPES = ["https://graph.microsoft.com/.default"]


def init_msal_app() -> msal.PublicClientApplication:
    """
    Initialize MSAL Public Client Application.
    
    Returns:
        MSAL PublicClientApplication instance
    """
    if not CLIENT_ID or not TENANT_ID:
        raise ValueError(
            "CLIENT_ID and TENANT_ID must be set in environment variables. "
            "Please check your .env file."
        )
    
    return msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY
    )


def get_msal_token() -> Optional[Dict]:
    """
    Get access token using MSAL interactive authentication.
    
    This method opens a browser window for the user to sign in interactively.
    
    Returns:
        Dictionary containing token response or None if authentication fails
    """
    try:
        app = init_msal_app()
        
        # First, try to get token from cache
        accounts = app.get_accounts()
        if accounts:
            # Try silent authentication first
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
            if result and "access_token" in result:
                result["account"] = accounts[0]
                return result
        
        # If silent authentication fails, use interactive authentication
        result = app.acquire_token_interactive(
            scopes=SCOPES,
            prompt="select_account"
        )
        
        if "access_token" in result:
            # Get account information
            accounts = app.get_accounts()
            if accounts:
                result["account"] = accounts[0]
            return result
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            print(f"Authentication failed: {error} - {error_description}")
            return None
    
    except Exception as e:
        print(f"Error during MSAL authentication: {str(e)}")
        return None


def get_msal_token_with_client_secret() -> Optional[str]:
    """
    Get access token using client credentials flow (for service-to-service).
    
    This is an alternative method that uses client secret instead of interactive auth.
    Only works when CLIENT_SECRET is configured.
    
    Returns:
        Access token string or None if authentication fails
    """
    if not CLIENT_SECRET:
        return None
    
    try:
        app = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=AUTHORITY,
            client_credential=CLIENT_SECRET
        )
        
        result = app.acquire_token_for_client(scopes=SCOPES)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            print(f"Authentication failed: {error} - {error_description}")
            return None
    
    except Exception as e:
        print(f"Error during client credentials authentication: {str(e)}")
        return None
