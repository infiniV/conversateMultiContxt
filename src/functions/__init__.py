"""
Functions package initialization.
Contains base classes and utilities for business-specific function contexts.
"""

from livekit.agents import llm
import logging
import asyncio
import os
import glob
from typing import Dict, Any, Annotated, List, Optional
from pathlib import Path

# Add imports for RAG capabilities
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    Document
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from src.utils.config import get_domain_config, get_business_config
from llama_index.llms.groq import Groq
from llama_index.core.settings import Settings

grop=Groq(model="llama-3.1-8b-instant")
Settings.llm=grop
class BaseBusinessFnc(llm.FunctionContext):
    """
    Base function context class that can be extended for any business type.
    Provides common utility functions applicable to most businesses.
    """
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("business-functions")
        self.domain_config = get_domain_config()
        self.business_config = get_business_config()
        self.business_domain = self.business_config.get("domain", "generic")
        self.index = self._initialize_document_index()
        
    def _initialize_document_index(self) -> Optional[VectorStoreIndex]:
        """Initialize the document index for RAG capabilities"""
        try:
            # Get document paths from config
            document_paths = self.domain_config.get("document_paths", [])
            if not document_paths:
                document_paths = [f"data/{self.business_domain}"]
            
            # Set persistence directory
            persist_dir = os.path.join("data", "indexes", f"{self.business_domain}_index")
            
            # Configure embedding model
            embedding_model_name = self.domain_config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
            
            # Configure settings
            Settings.embed_model = embed_model
            Settings.chunk_size = 512
            
            # Create directories if they don't exist
            os.makedirs(persist_dir, exist_ok=True)
            
            # Ensure document directories exist
            for path in document_paths:
                os.makedirs(path, exist_ok=True)
                
            # Check if index already exists
            index_exists = os.path.exists(os.path.join(persist_dir, "docstore.json"))
            should_rebuild_index = False
            
            # Get the modification times of documents and index
            latest_doc_time = 0
            for path in document_paths:
                if os.path.exists(path):
                    for file_path in glob.glob(f"{path}/**/*.*", recursive=True):
                        if os.path.isfile(file_path):
                            mtime = os.path.getmtime(file_path)
                            if mtime > latest_doc_time:
                                latest_doc_time = mtime
            
            # Get index modification time if it exists
            index_time = 0
            if index_exists:
                index_time = os.path.getmtime(os.path.join(persist_dir, "docstore.json"))
            
            # Check if documents are newer than index
            if latest_doc_time > index_time:
                self.logger.info("Documents have been modified since index was created. Rebuilding index.")
                should_rebuild_index = True
            
            # Create or load the index
            if index_exists and not should_rebuild_index:
                # Load existing index
                try:
                    self.logger.info(f"Loading existing index from {persist_dir}")
                    db = chromadb.PersistentClient(path=persist_dir)
                    chroma_collection = db.get_or_create_collection(self.business_domain)
                    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
                    storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=persist_dir)
                    index = load_index_from_storage(storage_context)  # Remove the second parameter
                    
                    # Verify the index is valid by checking for empty nodes
                    query_engine = index.as_query_engine(similarity_top_k=1)
                    try:
                        # Simple test query to validate index
                        response = query_engine.query("test")
                        if response is None or str(response).strip() == "":
                            self.logger.warning("Index validation failed. Rebuilding index.")
                            should_rebuild_index = True
                    except Exception as e:
                        self.logger.warning(f"Index validation failed: {e}. Rebuilding index.")
                        should_rebuild_index = True
                        
                    if not should_rebuild_index:
                        return index
                except Exception as e:
                    self.logger.warning(f"Error loading existing index: {e}. Creating new index.")
                    should_rebuild_index = True
            
            # Create new index
            self.logger.info(f"Creating new index for {self.business_domain} from documents in {document_paths}")
            documents = []
            
            # Try to load documents from each path
            for path in document_paths:
                if os.path.exists(path):
                    try:
                        # Check if the directory has any files
                        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                        if not files:
                            self.logger.warning(f"No files found in {path}. Creating sample document.")
                            
                            # Create a sample document if directory is empty
                            sample_file_path = os.path.join(path, "sample_info.txt")
                            with open(sample_file_path, "w") as f:
                                f.write(f"# {self.business_config['business_name']} Information\n\n")
                                f.write(f"This is a sample document for {self.business_config['business_name']}.\n\n")
                                f.write(f"Business Description: {self.business_config['business_description']}\n\n")
                                f.write("## Services\n\n")
                                for service in self.domain_config.get('services', []):
                                    f.write(f"- {service}\n")
                        
                        # Load documents
                        file_docs = SimpleDirectoryReader(path).load_data()
                        if file_docs:
                            self.logger.info(f"Loaded {len(file_docs)} documents from {path}")
                            documents.extend(file_docs)
                        else:
                            self.logger.warning(f"No documents loaded from {path}")
                    except Exception as e:
                        self.logger.error(f"Error loading documents from {path}: {str(e)}")
                else:
                    self.logger.warning(f"Path {path} does not exist")
            
            if not documents:
                self.logger.warning("No documents found. Creating a minimal document with business information.")
                # Create a minimal document with business information
                text = f"# {self.business_config['business_name']}\n\n"
                text += f"{self.business_config['business_description']}\n\n"
                text += "## Services\n\n"
                for service in self.domain_config.get('services', []):
                    text += f"- {service}\n"
                
                documents = [Document(text=text, metadata={"source": "system_generated"})]
            
            # Create and persist the index
            try:    
                db = chromadb.PersistentClient(path=persist_dir)
                chroma_collection = db.get_or_create_collection(self.business_domain)
                vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
                storage_context = StorageContext.from_defaults(vector_store=vector_store)
                
                index = VectorStoreIndex.from_documents(
                    documents, 
                    storage_context=storage_context
                )
                
                # Persist the index
                index.storage_context.persist(persist_dir=persist_dir)
                
                self.logger.info(f"Successfully created and persisted index with {len(documents)} documents")
                return index
            except Exception as e:
                self.logger.error(f"Error creating index: {str(e)}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error initializing document index: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    @llm.ai_callable()
    async def get_business_info(
        self,
        info_type: Annotated[
            str, 
            llm.TypeInfo(description="Type of business information requested (e.g., hours, location, services, contact)")
        ]
    ) -> Dict[str, Any]:
        """
        Get general business information based on the requested type
        """
        # This function should be overridden with actual business info in subclasses
        return {
            "message": "This is a placeholder function. Please customize with your actual business information.",
            "info_type": info_type,
        }
    
    @llm.ai_callable()
    async def submit_feedback(
        self,
        feedback: Annotated[
            str, 
            llm.TypeInfo(description="Customer feedback or suggestion")
        ],
        rating: Annotated[
            int, 
            llm.TypeInfo(description="Optional customer satisfaction rating (1-5)")
        ] = 0
    ) -> Dict[str, Any]:
        """
        Submit customer feedback or suggestions
        """
        # In a real implementation, this would save to a database
        logging.info(f"Feedback received: {feedback} (Rating: {rating})")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "status": "success",
            "message": "Thank you for your feedback! We appreciate your input and will use it to improve our services."
        }
    
    @llm.ai_callable(description="Get more information about a specific topic from our knowledge base")
    async def query_info(
        self,
        query: Annotated[
            str, 
            llm.TypeInfo(description="The query or topic to search for in the knowledge base")
        ]
    ) -> Dict[str, Any]:
        """
        Query the document index for information on a specific topic
        """
        self.logger.info(f"Querying knowledge base for: {query}")
        
        if not self.index:
            self.logger.warning("Document index not available. Reinitializing...")
            self.index = self._initialize_document_index()
            
            if not self.index:
                return {
                    "status": "error",
                    "message": "Document index is not available. Unable to perform knowledge retrieval."
                }
            
        try:
            # Create query engine and perform query
            query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                use_async=True
            )
            
            # Run the query with timeout
            try:
                response = await asyncio.wait_for(query_engine.aquery(query), timeout=10.0)
            except asyncio.TimeoutError:
                return {
                    "status": "error",
                    "message": "Query timed out. Please try a more specific question."
                }
            
            # Extract sources if available
            sources = []
            if hasattr(response, 'metadata') and response.metadata:
                for metadata in response.metadata.values():
                    if 'file_name' in metadata:
                        sources.append(metadata['file_name'])
            
            answer = str(response).strip()
            if not answer:
                return {
                    "status": "not_found",
                    "message": "I couldn't find specific information about that topic in our knowledge base."
                }
                
            return {
                "status": "success",
                "answer": answer,
                "sources": list(set(sources)) if sources else []
            }
        except Exception as e:
            self.logger.error(f"Error querying document index: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Error retrieving information: {str(e)}"
            }

    @llm.ai_callable(description="Add a document to the knowledge base")
    async def add_document(
        self,
        text: Annotated[
            str,
            llm.TypeInfo(description="The document text to add to the knowledge base")
        ],
        title: Annotated[
            str,
            llm.TypeInfo(description="The title of the document")
        ],
        domain: Annotated[
            str,
            llm.TypeInfo(description="The business domain this document belongs to")
        ] = ""
    ) -> Dict[str, Any]:
        """
        Add a new document to the knowledge base
        """
        if not domain:
            domain = self.business_domain
            
        try:
            # Create directory if it doesn't exist
            doc_dir = os.path.join("data", domain)
            os.makedirs(doc_dir, exist_ok=True)
            
            # Clean title to use as filename
            filename = title.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
            filename = ''.join(c for c in filename if c.isalnum() or c in ['_', '-'])
            filename = f"{filename}.txt"
            
            # Write document to file
            file_path = os.path.join(doc_dir, filename)
            with open(file_path, "w") as f:
                f.write(f"# {title}\n\n")
                f.write(text)
                
            self.logger.info(f"Added document '{title}' to {file_path}")
            
            # Reinitialize index to include new document
            self.index = self._initialize_document_index()
            
            return {
                "status": "success",
                "message": f"Document '{title}' has been added to the knowledge base."
            }
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding document: {str(e)}"
            }

from .agriculture_functions import AgricultureAssistantFnc
from .insurance_functions import InsuranceAssistantFnc

__all__ = [
    "AgricultureAssistantFnc",
    "ConversateAssistantFnc"
]