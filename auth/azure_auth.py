"""
Azure Easy Auth authentication module.

This module handles authentication when the application is deployed on Azure
with Easy Authentication (Easy Auth) enabled.
"""

import os
import streamlit as st
from typing import Optional


def get_azure_easyauth_token() -> Optional[str]:
    """
    Get access token from Azure Easy Auth.
    
    When Easy Auth is enabled on Azure App Service, it automatically handles
    authentication and provides the access token in request headers.
    
    Returns:
        Access token string or None if not available
    """
    # Azure Easy Auth provides the token in a custom header
    # Check for the token in Streamlit's request headers
    if hasattr(st, 'context') and hasattr(st.context, 'headers'):
        # Get token from Easy Auth header
        token = st.context.headers.get("X-MS-TOKEN-AAD-ACCESS-TOKEN")
        if token:
            return token
    
    # Alternative: Get token from environment (some Azure configurations)
    token = os.getenv("MS_TOKEN_AAD_ACCESS_TOKEN")
    if token:
        return token
    
    # If running on Azure but token not found, show error
    if os.getenv("WEBSITE_AUTH_ENABLED") == "True":
        st.error("""
        Easy Auth is enabled but token not found. Please ensure:
        1. Easy Auth is properly configured in Azure App Service
        2. Token Store is enabled
        3. The application has the required API permissions
        """)
    
    return None


def get_user_info_from_easyauth() -> Optional[dict]:
    """
    Get user information from Azure Easy Auth.
    
    Returns:
        Dictionary containing user information or None
    """
    if hasattr(st, 'context') and hasattr(st.context, 'headers'):
        # Get user principal name from Easy Auth header
        user_principal = st.context.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
        user_id = st.context.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
        
        if user_principal or user_id:
            return {
                "username": user_principal,
                "user_id": user_id
            }
    
    return None
