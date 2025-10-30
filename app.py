"""
Graph API SharePoint File Listing Demo
Streamlit application that accesses SharePoint sites using Microsoft Graph API.

Supports two authentication modes:
1. Azure Easy Auth (for Azure deployment)
2. MSAL (for local development)
"""

import os
import streamlit as st
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Import authentication modules
from auth.azure_auth import get_azure_easyauth_token
from auth.msal_auth import get_msal_token, init_msal_app
from graph.sharepoint_client import SharePointClient

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SharePoint File Listing Demo",
    page_icon="📁",
    layout="wide"
)


def is_running_on_azure() -> bool:
    """Check if the application is running on Azure with Easy Auth enabled."""
    # Azure Easy Auth sets specific headers when enabled
    return os.getenv("WEBSITE_AUTH_ENABLED") == "True" or \
           "X-MS-TOKEN-AAD-ACCESS-TOKEN" in st.context.headers


def get_access_token() -> Optional[str]:
    """
    Get access token based on the environment.
    
    Returns:
        Access token string or None if authentication fails
    """
    if is_running_on_azure():
        # Running on Azure with Easy Auth
        st.sidebar.info("🔐 Authentication: Azure Easy Auth")
        return get_azure_easyauth_token()
    else:
        # Running locally - use MSAL
        st.sidebar.info("🔐 Authentication: MSAL (Local)")
        
        # Initialize session state for authentication
        if "msal_token" not in st.session_state:
            st.session_state.msal_token = None
        if "msal_account" not in st.session_state:
            st.session_state.msal_account = None
        
        # Show sign-in button if not authenticated
        if st.session_state.msal_token is None:
            st.sidebar.warning("Please sign in to continue")
            
            if st.sidebar.button("🔑 Sign In with Microsoft", type="primary"):
                with st.spinner("Opening browser for authentication..."):
                    token_response = get_msal_token()
                    if token_response:
                        st.session_state.msal_token = token_response.get("access_token")
                        st.session_state.msal_account = token_response.get("account")
                        st.rerun()
                    else:
                        st.sidebar.error("Authentication failed. Please try again.")
                        return None
            return None
        else:
            # Already authenticated
            if st.session_state.msal_account:
                username = st.session_state.msal_account.get("username", "User")
                st.sidebar.success(f"Signed in as: {username}")
            
            # Add sign-out button
            if st.sidebar.button("🚪 Sign Out"):
                st.session_state.msal_token = None
                st.session_state.msal_account = None
                st.rerun()
            
            return st.session_state.msal_token


def display_file_list(files: List[Dict]):
    """Display the list of files in a nice format."""
    if not files:
        st.info("No files found in the SharePoint site.")
        return
    
    st.success(f"Found {len(files)} items")
    
    # Create a table view
    for file in files:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                # Display icon based on file type
                if file.get("folder"):
                    st.write(f"📁 **{file['name']}**")
                else:
                    st.write(f"📄 {file['name']}")
            
            with col2:
                size = file.get("size", 0)
                if size > 0:
                    # Convert bytes to human-readable format
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    elif size < 1024 * 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.2f} MB"
                    else:
                        size_str = f"{size / (1024 * 1024 * 1024):.2f} GB"
                    st.write(f"Size: {size_str}")
            
            with col3:
                modified = file.get("lastModifiedDateTime", "")
                if modified:
                    st.write(f"Modified: {modified[:10]}")
            
            st.divider()


def main():
    """Main application function."""
    st.title("📁 SharePoint File Listing Demo")
    st.markdown("""
    This application demonstrates accessing SharePoint sites using Microsoft Graph API.
    - **Azure deployment**: Uses Easy Auth for authentication
    - **Local development**: Uses MSAL library with interactive sign-in
    """)
    
    # Get access token
    access_token = get_access_token()
    
    if not access_token:
        st.warning("Please authenticate to access SharePoint files.")
        st.info("""
        **Setup Instructions:**
        1. Ensure you have configured the application in Azure AD
        2. Set the required environment variables (see .env.example)
        3. Click the 'Sign In with Microsoft' button in the sidebar
        """)
        return
    
    # Initialize SharePoint client
    sharepoint_client = SharePointClient(access_token)
    
    # Sidebar configuration
    st.sidebar.title("Configuration")
    
    # Option to specify SharePoint site
    site_url = os.getenv("SHAREPOINT_SITE_URL", "")
    site_input = st.sidebar.text_input(
        "SharePoint Site URL",
        value=site_url,
        placeholder="https://yourtenant.sharepoint.com/sites/yoursite"
    )
    
    # Option to specify folder path
    folder_path = st.sidebar.text_input(
        "Folder Path (optional)",
        value="",
        placeholder="Documents/Subfolder"
    )
    
    # Fetch files button
    if st.sidebar.button("🔄 Fetch Files", type="primary"):
        if not site_input:
            st.error("Please enter a SharePoint site URL")
            return
        
        with st.spinner("Fetching files from SharePoint..."):
            try:
                files = sharepoint_client.list_files(site_input, folder_path)
                display_file_list(files)
            except Exception as e:
                st.error(f"Error fetching files: {str(e)}")
                st.exception(e)
    
    # Display help information
    with st.expander("ℹ️ Help"):
        st.markdown("""
        ### How to use this application:
        
        1. **Authenticate**: Sign in using the button in the sidebar
        2. **Configure**: Enter your SharePoint site URL
        3. **Browse**: Optionally specify a folder path to browse
        4. **Fetch**: Click 'Fetch Files' to retrieve the file list
        
        ### Required Permissions:
        - `Sites.Read.All` or `Sites.ReadWrite.All`
        - `Files.Read.All` or `Files.ReadWrite.All`
        
        ### Environment Variables:
        - `CLIENT_ID`: Azure AD application client ID
        - `TENANT_ID`: Azure AD tenant ID
        - `SHAREPOINT_SITE_URL`: Default SharePoint site URL (optional)
        """)


if __name__ == "__main__":
    main()
