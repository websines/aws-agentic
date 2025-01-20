from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from core.config import Config

def get_graph_client():
    """Create an authenticated Microsoft Graph client."""
    credentials = ClientSecretCredential(
        tenant_id=Config.AZURE_TENANT_ID,
        client_id=Config.AZURE_CLIENT_ID,
        client_secret=Config.AZURE_CLIENT_SECRET
    )
    
    return GraphClient(credential=credentials)
