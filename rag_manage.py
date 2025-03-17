"""
RAG System Management Utilities

This script provides tools to manage, monitor, and troubleshoot the RAG (Retrieval Augmented Generation)
components of the Farmovation assistant.

Usage:
  python rag_manage.py --check-all           # Check status of all RAG indexes
  python rag_manage.py --rebuild agriculture  # Rebuild index for agriculture domain
  python rag_manage.py --validate agriculture # Validate documents and index for agriculture
  python rag_manage.py --clean agriculture    # Clean up problematic files in domain
"""

import os
import sys
import json
import logging
import argparse
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import glob

# Add RAG-related imports
try:
    from llama_index.core import (
        SimpleDirectoryReader,
        VectorStoreIndex,
        StorageContext,
        load_index_from_storage,
        Settings,
        Document
    )
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb
except ImportError:
    print("Error: Required libraries not found. Install with 'pip install llama-index'")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag-manager")

class RAGManager:
    """
    Manager class for RAG components, providing utilities to:
    - Check index health
    - Rebuild indexes
    - Validate documents
    - Clean up problematic files
    """
    
    def __init__(self):
        """Initialize the RAG Manager"""
        self.base_dir = Path("data")
        self.indexes_dir = self.base_dir / "indexes"
        
        # Ensure directories exist
        self.base_dir.mkdir(exist_ok=True)
        self.indexes_dir.mkdir(exist_ok=True)
        
        # Default embedding model
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
    def get_domains(self) -> List[str]:
        """Get list of available domains"""
        return [d.name for d in self.base_dir.iterdir() 
                if d.is_dir() and not d.name == "indexes"]
    
    def check_all_indexes(self) -> Dict[str, Dict[str, Any]]:
        """Check the health of all domain indexes"""
        domains = self.get_domains()
        results = {}
        
        logger.info(f"Checking {len(domains)} domain indexes...")
        for domain in domains:
            results[domain] = self.check_index_health(domain)
        
        # Print summary
        logger.info("\n--- Index Health Summary ---")
        for domain, health in results.items():
            status = health.get("status", "unknown")
            doc_count = health.get("document_count", 0)
            index_count = health.get("index_document_count", 0)
            
            color_code = "\033[32m"  # Green for healthy
            if status == "warning":
                color_code = "\033[33m"  # Yellow for warning
            elif status == "error":
                color_code = "\033[31m"  # Red for error
            reset_code = "\033[0m"
            
            logger.info(f"{domain}: {color_code}{status}{reset_code} - {doc_count} docs, {index_count} indexed")
            if "issues" in health and health["issues"]:
                for issue in health["issues"]:
                    logger.info(f"  - {issue}")
                    
        return results
    
    def check_index_health(self, domain: str) -> Dict[str, Any]:
        """
        Check the health of a specific domain's RAG index
        
        Args:
            domain: The domain name to check
            
        Returns:
            Dictionary with health information
        """
        result = {
            "domain": domain,
            "status": "healthy",
            "issues": [],
            "document_count": 0,
            "index_document_count": 0
        }
        
        # Check if domain directory exists
        domain_dir = self.base_dir / domain
        if not domain_dir.exists():
            result["status"] = "error"
            result["issues"].append(f"Domain directory {domain_dir} does not exist")
            return result
        
        # Count domain documents
        documents = [f for f in domain_dir.glob("*") 
                     if f.is_file() and not f.name.startswith("_")]
        result["document_count"] = len(documents)
        
        if len(documents) == 0:
            result["status"] = "warning"
            result["issues"].append("No documents found in domain directory")
        
        # Check if index exists
        index_dir = self.indexes_dir / f"{domain}_index"
        if not index_dir.exists():
            result["status"] = "warning"
            result["issues"].append("Index directory does not exist")
            return result
        
        # Check for expected index files
        required_files = ["chroma.sqlite3", "docstore.json"]
        for file in required_files:
            if not (index_dir / file).exists():
                result["status"] = "error"
                result["issues"].append(f"Missing required index file: {file}")
        
        # Try to get document count from index
        try:
            with open(index_dir / "docstore.json", 'r') as f:
                docstore_data = json.load(f)
                doc_count = len(docstore_data.get("docstore/metadata", {}))
                result["index_document_count"] = doc_count
                
                # Check if index document count matches actual documents
                if doc_count != len(documents) and len(documents) > 0:
                    result["status"] = "warning" 
                    result["issues"].append(
                        f"Document count mismatch: {len(documents)} docs but {doc_count} in index"
                    )
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error reading docstore.json: {str(e)}")
        
        # Try loading the index to verify it works
        try:
            # Test loading index
            db = chromadb.PersistentClient(path=str(index_dir))
            collection_exists = False
            
            try:
                chroma_collection = db.get_collection(domain)
                collection_exists = True
            except Exception:
                result["status"] = "error"
                result["issues"].append("Chroma collection does not exist")
            
            if collection_exists:
                # Check collection count
                try:
                    count = chroma_collection.count()
                    if count == 0:
                        result["status"] = "warning"
                        result["issues"].append("Chroma collection is empty")
                    result["embedding_count"] = count
                except Exception as e:
                    result["status"] = "error"
                    result["issues"].append(f"Error checking collection count: {str(e)}")
                
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(f"Error loading index: {str(e)}")
        
        # Return final health assessment
        return result
    
    def rebuild_index(self, domain: str, force: bool = False) -> Dict[str, Any]:
        """
        Rebuild the index for a domain
        
        Args:
            domain: The domain to rebuild the index for
            force: Whether to force rebuild even if index appears healthy
            
        Returns:
            Dictionary with operation results
        """
        result = {
            "domain": domain,
            "success": False,
            "message": ""
        }
        
        logger.info(f"Rebuilding index for {domain}...")
        
        # Check if domain exists
        domain_dir = self.base_dir / domain
        if not domain_dir.exists():
            result["message"] = f"Domain directory {domain} does not exist"
            logger.error(result["message"])
            return result
        
        # Check if there are documents to index
        documents = list(domain_dir.glob("*"))
        if not documents:
            result["message"] = f"No documents found in {domain} directory"
            logger.warning(result["message"])
            return result
        
        # Check index health if not forcing rebuild
        if not force:
            health = self.check_index_health(domain)
            if health["status"] == "healthy":
                should_rebuild = input("Index appears healthy. Rebuild anyway? (y/n): ").lower() == 'y'
                if not should_rebuild:
                    result["message"] = "Index rebuild cancelled by user"
                    logger.info(result["message"])
                    return result
        
        # Delete existing index if it exists
        index_dir = self.indexes_dir / f"{domain}_index"
        if index_dir.exists():
            try:
                logger.info(f"Removing existing index directory: {index_dir}")
                shutil.rmtree(index_dir)
            except Exception as e:
                result["message"] = f"Error removing existing index: {str(e)}"
                logger.error(result["message"])
                return result
        
        # Create new index directory
        index_dir.mkdir(exist_ok=True)
        
        try:
            # Configure embedding model
            embed_model = HuggingFaceEmbedding(model_name=self.embedding_model_name)
            Settings.embed_model = embed_model
            Settings.chunk_size = 512
            
            # Load documents
            logger.info(f"Loading documents from {domain_dir}")
            try:
                documents = SimpleDirectoryReader(str(domain_dir)).load_data()
                logger.info(f"Loaded {len(documents)} documents")
            except Exception as e:
                result["message"] = f"Error loading documents: {str(e)}"
                logger.error(result["message"])
                return result
            
            if not documents:
                result["message"] = "No documents were loaded"
                logger.warning(result["message"])
                return result
            
            # Create index
            logger.info("Creating new index...")
            start_time = time.time()
            
            # Initialize ChromaDB
            db = chromadb.PersistentClient(path=str(index_dir))
            chroma_collection = db.get_or_create_collection(domain)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context
            )
            
            # Persist index
            index.storage_context.persist(persist_dir=str(index_dir))
            
            duration = time.time() - start_time
            logger.info(f"Index created and persisted in {duration:.2f} seconds")
            
            # Verify index
            health = self.check_index_health(domain)
            if health["status"] == "error":
                result["message"] = f"Index rebuilt but has errors: {', '.join(health['issues'])}"
                logger.warning(result["message"])
                return result
            
            result["success"] = True
            result["message"] = f"Successfully rebuilt index with {len(documents)} documents"
            logger.info(result["message"])
            
            return result
            
        except Exception as e:
            import traceback
            result["message"] = f"Error rebuilding index: {str(e)}"
            logger.error(result["message"])
            logger.debug(traceback.format_exc())
            return result
    
    def validate_documents(self, domain: str) -> Dict[str, Any]:
        """
        Validate all documents in a domain for indexability
        
        Args:
            domain: The domain to validate documents for
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "domain": domain,
            "total_documents": 0,
            "valid_documents": 0,
            "problematic_documents": []
        }
        
        domain_dir = self.base_dir / domain
        if not domain_dir.exists():
            logger.error(f"Domain directory {domain} does not exist")
            return result
        
        logger.info(f"Validating documents in {domain}...")
        
        # Get list of all files
        files = [f for f in domain_dir.glob("*") if f.is_file() and not f.name.startswith("_")]
        result["total_documents"] = len(files)
        
        if not files:
            logger.warning(f"No documents found in {domain}")
            return result
        
        # Validate each document
        for file in files:
            try:
                # Check file size
                file_size = os.path.getsize(file)
                if file_size == 0:
                    result["problematic_documents"].append({
                        "file": str(file),
                        "issue": "Empty file"
                    })
                    continue
                    
                if file_size > 10 * 1024 * 1024:  # 10MB
                    result["problematic_documents"].append({
                        "file": str(file),
                        "issue": f"File too large: {file_size / (1024*1024):.2f}MB"
                    })
                    continue
                
                # Check encoding for text files
                if file.suffix.lower() in ['.txt', '.md', '.csv', '.json']:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read(1024)  # Read just the beginning
                            if not content.strip():
                                result["problematic_documents"].append({
                                    "file": str(file),
                                    "issue": "File appears to be empty"
                                })
                                continue
                    except UnicodeDecodeError:
                        result["problematic_documents"].append({
                            "file": str(file),
                            "issue": "File has encoding issues"
                        })
                        continue
                
                # Try to load the document with SimpleDirectoryReader
                try:
                    docs = SimpleDirectoryReader(input_files=[str(file)]).load_data()
                    if not docs:
                        result["problematic_documents"].append({
                            "file": str(file),
                            "issue": "Failed to load with SimpleDirectoryReader"
                        })
                        continue
                except Exception as e:
                    result["problematic_documents"].append({
                        "file": str(file),
                        "issue": f"Error during document loading: {str(e)}"
                    })
                    continue
                
                # Document passed all checks
                result["valid_documents"] += 1
                
            except Exception as e:
                result["problematic_documents"].append({
                    "file": str(file),
                    "issue": f"Unexpected error: {str(e)}"
                })
        
        # Print validation results
        logger.info(f"Validation complete: {result['valid_documents']} of {result['total_documents']} documents are valid")
        if result["problematic_documents"]:
            logger.warning(f"Found {len(result['problematic_documents'])} problematic documents:")
            for doc in result["problematic_documents"]:
                logger.warning(f"  - {os.path.basename(doc['file'])}: {doc['issue']}")
                
        return result
    
    def clean_domain(self, domain: str, fix_issues: bool = False) -> Dict[str, Any]:
        """
        Clean up problematic files in a domain
        
        Args:
            domain: The domain to clean
            fix_issues: Whether to automatically fix issues when possible
            
        Returns:
            Dictionary with cleaning results
        """
        result = {
            "domain": domain,
            "files_checked": 0,
            "files_fixed": 0,
            "files_removed": 0,
            "issues_found": 0
        }
        
        domain_dir = self.base_dir / domain
        if not domain_dir.exists():
            logger.error(f"Domain directory {domain} does not exist")
            return result
        
        logger.info(f"Cleaning domain: {domain}")
        
        # First validate to find problematic documents
        validation = self.validate_documents(domain)
        result["files_checked"] = validation["total_documents"]
        result["issues_found"] = len(validation["problematic_documents"])
        
        if not validation["problematic_documents"]:
            logger.info(f"No issues found in {domain}")
            return result
        
        # Process problematic documents
        for doc in validation["problematic_documents"]:
            file_path = Path(doc["file"])
            issue = doc["issue"]
            
            if "Empty file" in issue or "encoding issues" in issue:
                if fix_issues:
                    try:
                        backup_file = file_path.parent / f"_backup_{file_path.name}"
                        shutil.copy2(file_path, backup_file)
                        os.remove(file_path)
                        result["files_removed"] += 1
                        logger.info(f"Removed problematic file: {file_path} (backup created)")
                    except Exception as e:
                        logger.error(f"Error removing file {file_path}: {str(e)}")
                else:
                    logger.info(f"Recommend removing file: {file_path} - {issue}")
            
            elif "File too large" in issue:
                if fix_issues:
                    try:
                        logger.info(f"Large file {file_path} will be ignored during indexing")
                        # Optionally create a marker file to indicate it should be skipped
                        with open(file_path.parent / f"_skip_{file_path.name}.marker", "w") as f:
                            f.write(f"File too large: {issue}")
                    except Exception as e:
                        logger.error(f"Error creating marker file for {file_path}: {str(e)}")
                else:
                    logger.info(f"Recommend ignoring or splitting file: {file_path} - {issue}")
        
        # Ask about rebuilding index if issues were found and fixed
        if fix_issues and (result["files_removed"] > 0 or result["files_fixed"] > 0):
            should_rebuild = input(f"Issues fixed in {domain}. Rebuild index now? (y/n): ").lower() == 'y'
            if should_rebuild:
                self.rebuild_index(domain, force=True)
                
        return result

def main():
    parser = argparse.ArgumentParser(description="RAG System Management Utilities")
    parser.add_argument("--check-all", action="store_true", help="Check all RAG indexes")
    parser.add_argument("--check", type=str, help="Check health of a specific domain index")
    parser.add_argument("--rebuild", type=str, help="Rebuild index for a domain")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if index is healthy")
    parser.add_argument("--validate", type=str, help="Validate documents in a domain")
    parser.add_argument("--clean", type=str, help="Clean problematic files in a domain")
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues when cleaning")
    parser.add_argument("--list", action="store_true", help="List available domains")
    
    args = parser.parse_args()
    
    # Create RAG manager
    manager = RAGManager()
    
    if args.list:
        domains = manager.get_domains()
        logger.info("Available domains:")
        for domain in domains:
            logger.info(f"- {domain}")
        return
    
    if args.check_all:
        manager.check_all_indexes()
        return
        
    if args.check:
        health = manager.check_index_health(args.check)
        logger.info(f"Index health for {args.check}: {health['status']}")
        if "issues" in health and health["issues"]:
            for issue in health["issues"]:
                logger.info(f"- {issue}")
        return
        
    if args.rebuild:
        manager.rebuild_index(args.rebuild, args.force)
        return
        
    if args.validate:
        manager.validate_documents(args.validate)
        return
        
    if args.clean:
        manager.clean_domain(args.clean, args.fix)
        return
        
    # If no action specified, show help
    parser.print_help()

if __name__ == "__main__":
    main()