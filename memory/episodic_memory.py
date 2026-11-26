
import chromadb
from sentence_transformers import SentenceTransformer
import uuid

class EpisodicMemory:
    def __init__(self, presist_dir="./chroma_db", collection_name="episodic_memory"):
        self.client=chromadb.PersistentClient(path=presist_dir)
        self.encoder=SentenceTransformer("all-MiniLM-L6-v2")
        self.collection=self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def store(self, text:str, metadeta: dict=None):
        """
        Save a conversation Snipped. Return the ID.
        """
        if metadeta is None:
            metadeta={"type": "conversion"}

        vector=self.encoder.encode(text).tolist()

        item_id=str(uuid.uuid4())

        self.collection.add(
            embeddings=[vector],
            documents=[text],
            metadatas=[metadeta],
            ids=[item_id]
        )

        return item_id

    def retrieve(self, query:str, top_k=3):
        """
        Retrives top_k chunks against query.
        """

        if self.collection.count()==0:
            return []
        
        query_vector=self.encoder.encode(query).tolist()

        results=self.collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, self.collection.count())
        )

        documents=results['documents'][0]

        return documents

    def count(self):
        """
        How many total items saved.
        """
        return self.collection.count()
