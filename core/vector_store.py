from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from core.config import Config

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create collections if they don't exist
        self._ensure_collections()
    
    def _ensure_collections(self):
        """Ensures required collections exist."""
        collections = {
            "azure_resources": "Azure resources and their configurations",
            "security_alerts": "Security alerts and recommendations",
            "audit_logs": "Audit logs and activities",
            "cost_data": "Cost and billing information"
        }
        
        for name, description in collections.items():
            try:
                self.client.get_collection(name)
            except:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(
                        size=384,  # Dimension of all-MiniLM-L6-v2
                        distance=models.Distance.COSINE
                    ),
                    metadata={
                        "description": description
                    }
                )
    
    def store_resource(self, resource: Dict[str, Any]):
        """Stores Azure resource information."""
        embedding = self.encoder.encode(
            f"{resource.get('name', '')} {resource.get('type', '')} {resource.get('location', '')}"
        ).tolist()
        
        self.client.upsert(
            collection_name="azure_resources",
            points=[
                models.PointStruct(
                    id=resource.get('id', '').replace('/', '_'),
                    vector=embedding,
                    payload=resource
                )
            ]
        )
    
    def store_security_alert(self, alert: Dict[str, Any]):
        """Stores security alert information."""
        embedding = self.encoder.encode(
            f"{alert.get('title', '')} {alert.get('description', '')}"
        ).tolist()
        
        self.client.upsert(
            collection_name="security_alerts",
            points=[
                models.PointStruct(
                    id=alert.get('id', '').replace('/', '_'),
                    vector=embedding,
                    payload=alert
                )
            ]
        )
    
    def search_resources(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches for Azure resources based on natural language query."""
        query_vector = self.encoder.encode(query).tolist()
        
        results = self.client.search(
            collection_name="azure_resources",
            query_vector=query_vector,
            limit=limit
        )
        
        return [hit.payload for hit in results]
    
    def search_security_alerts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches for security alerts based on natural language query."""
        query_vector = self.encoder.encode(query).tolist()
        
        results = self.client.search(
            collection_name="security_alerts",
            query_vector=query_vector,
            limit=limit
        )
        
        return [hit.payload for hit in results]
