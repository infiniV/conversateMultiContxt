"""
Utility script to add documents to the RAG system.
This script helps with importing documents into the appropriate directories
for use by the RAG-enabled voice assistant.
"""

import os
import sys
import shutil
import argparse
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("document-importer")

def clean_filename(filename):
    """Sanitize filenames to avoid special characters issues"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def validate_file_content(file_path: str) -> Dict[str, Any]:
    """
    Validate file content based on extension and return metadata
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Dictionary with validation status and metadata
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    result = {
        "valid": False,
        "reason": "",
        "file_type": ext[1:] if ext else "unknown",
        "size_kb": os.path.getsize(file_path) / 1024
    }
    
    # Check file size (10MB limit)
    if result["size_kb"] > 10240:
        result["reason"] = f"File too large: {result['size_kb']:.1f} KB (max 10MB)"
        return result
        
    try:
        # Text-based validation
        if ext in ['.txt', '.md', '.csv', '.json']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Read first 1KB to check content
                
            if not content.strip():
                result["reason"] = "File appears to be empty"
                return result
            
            # For JSON files, check if it's valid JSON
            if ext == '.json':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    result["reason"] = "Invalid JSON format"
                    return result
        
        # Always mark as valid if no specific validation failed
        result["valid"] = True
        return result
        
    except Exception as e:
        result["reason"] = f"Validation error: {str(e)}"
        return result

def add_documents(source_paths: List[str], business_domain: str, clear_existing: bool = False) -> Dict[str, Any]:
    """
    Add documents to the RAG system for a specific business domain
    
    Args:
        source_paths: List of file or directory paths to add
        business_domain: Business domain to add documents for
        clear_existing: Whether to clear existing documents before adding new ones
        
    Returns:
        Dictionary with operation results
    """
    result = {
        "success": True,
        "files_added": [],
        "files_skipped": [],
        "errors": []
    }
    
    # Base data directory
    data_dir = Path("data")
    domain_dir = data_dir / business_domain
    indexes_dir = data_dir / "indexes" / f"{business_domain}_index"
    
    # Create directories if they don't exist
    data_dir.mkdir(exist_ok=True)
    domain_dir.mkdir(exist_ok=True)
    
    # Clear existing documents if requested
    if clear_existing:
        logger.info(f"Clearing existing documents for domain: {business_domain}")
        files_removed = 0
        
        # Remove existing documents
        for file in domain_dir.glob("*"):
            if file.is_file():
                try:
                    file.unlink()
                    files_removed += 1
                except Exception as e:
                    error_msg = f"Error removing file {file}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
        
        logger.info(f"Removed {files_removed} existing documents")
        
        # Remove existing index if it exists
        if indexes_dir.exists():
            logger.info(f"Removing existing index for domain: {business_domain}")
            try:
                shutil.rmtree(indexes_dir)
                logger.info("Index removed successfully")
            except Exception as e:
                error_msg = f"Error removing index directory: {str(e)}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
    
    # Process each source path
    for source_path in source_paths:
        source = Path(source_path)
        if not source.exists():
            error_msg = f"Source path does not exist: {source_path}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            continue
        
        if source.is_file():
            # Copy a single file
            try:
                dest_file = domain_dir / clean_filename(source.name)
                
                # Validate file
                validation = validate_file_content(source)
                if not validation["valid"]:
                    logger.warning(f"Skipping file {source}: {validation['reason']}")
                    result["files_skipped"].append({
                        "path": str(source),
                        "reason": validation["reason"]
                    })
                    continue
                
                logger.info(f"Copying file: {source} to {dest_file}")
                shutil.copy2(source, dest_file)
                result["files_added"].append(str(dest_file))
                
            except Exception as e:
                error_msg = f"Error copying file {source}: {str(e)}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
        
        elif source.is_dir():
            # Copy all files from the directory
            try:
                files_found = 0
                for file in source.glob("*"):
                    if file.is_file() and file.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.html', '.csv', '.json']:
                        files_found += 1
                        dest_file = domain_dir / clean_filename(file.name)
                        
                        # Validate file
                        validation = validate_file_content(file)
                        if not validation["valid"]:
                            logger.warning(f"Skipping file {file}: {validation['reason']}")
                            result["files_skipped"].append({
                                "path": str(file),
                                "reason": validation["reason"]
                            })
                            continue
                            
                        logger.info(f"Copying file: {file} to {dest_file}")
                        shutil.copy2(file, dest_file)
                        result["files_added"].append(str(dest_file))
                
                if files_found == 0:
                    logger.warning(f"No compatible files found in directory: {source}")
                    
            except Exception as e:
                error_msg = f"Error processing directory {source}: {str(e)}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
    
    if not result["files_added"]:
        if not result["errors"]:
            logger.warning(f"No documents were added for domain: {business_domain}")
            result["warning"] = "No documents were added. Check that your source paths contain valid documents."
    else:
        logger.info(f"Added {len(result['files_added'])} documents to {business_domain} domain")
        # Create a special metadata file with information about the import
        try:
            metadata_file = domain_dir / "_import_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    "last_import": {
                        "timestamp": import_timestamp(),
                        "files_count": len(result["files_added"]),
                        "business_domain": business_domain
                    }
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not create metadata file: {str(e)}")
    
    # Set success status based on errors
    if result["errors"]:
        result["success"] = False
    
    logger.info(f"Document import complete for domain: {business_domain}")
    logger.info(f"The documents will be indexed when the RAG system is next initialized")
    
    return result

def import_timestamp() -> str:
    """Return a formatted timestamp for the import"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def list_domains() -> Dict[str, Any]:
    """
    List all available business domains with document counts
    
    Returns:
        Dictionary with domain information
    """
    result = {
        "domains": [],
        "total_domains": 0
    }
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        logger.info("Data directory does not exist. No domains available.")
        return result
    
    domains = [d for d in data_dir.iterdir() if d.is_dir() and not d.name == "indexes"]
    
    if not domains:
        logger.info("No business domains found.")
        return result
    
    logger.info("Available business domains:")
    for domain_dir in domains:
        files = [f for f in domain_dir.glob("*") if f.is_file() and not f.name.startswith("_")]
        file_count = len(files)
        
        # Get the file types
        file_types = {}
        for file in files:
            ext = file.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
        domain_info = {
            "name": domain_dir.name,
            "document_count": file_count,
            "file_types": file_types
        }
        
        # Check if index exists
        index_dir = data_dir / "indexes" / f"{domain_dir.name}_index"
        domain_info["has_index"] = index_dir.exists()
        
        result["domains"].append(domain_info)
        logger.info(f"- {domain_dir.name}: {file_count} documents")
    
    result["total_domains"] = len(domains)
    return result

def print_domain_info(domain: str) -> Dict[str, Any]:
    """
    Print detailed information about a specific domain
    
    Args:
        domain: Domain name to get information for
        
    Returns:
        Dictionary with domain information
    """
    domain_dir = Path("data") / domain
    
    if not domain_dir.exists() or not domain_dir.is_dir():
        logger.error(f"Domain directory does not exist: {domain}")
        return {
            "error": f"Domain '{domain}' not found",
            "available_domains": [d.name for d in Path("data").glob("*") if d.is_dir() and not d.name == "indexes"]
        }
    
    result = {
        "domain": domain,
        "document_count": 0,
        "files": [],
        "index_status": "not_found"
    }
    
    # List all files
    files = [f for f in domain_dir.glob("*") if f.is_file() and not f.name.startswith("_")]
    result["document_count"] = len(files)
    
    # Get file details
    for file in files:
        try:
            file_size = os.path.getsize(file)
            file_info = {
                "name": file.name,
                "size_bytes": file_size,
                "size_kb": round(file_size / 1024, 1),
                "type": file.suffix[1:] if file.suffix else "unknown"
            }
            result["files"].append(file_info)
        except Exception as e:
            logger.warning(f"Error getting file info for {file}: {str(e)}")
    
    # Check index status
    index_dir = Path("data") / "indexes" / f"{domain}_index"
    if index_dir.exists():
        result["index_status"] = "exists"
        
        # Check if docstore.json exists (indicates a valid index)
        if (index_dir / "docstore.json").exists():
            result["index_status"] = "valid"
            
            # Try to get document count from docstore
            try:
                with open(index_dir / "docstore.json", 'r') as f:
                    docstore_data = json.load(f)
                    doc_count = len(docstore_data.get("docstore/metadata", {}))
                    result["indexed_document_count"] = doc_count
            except Exception as e:
                logger.warning(f"Could not read docstore.json: {str(e)}")
    
    # Print information
    logger.info(f"Domain: {domain}")
    logger.info(f"Document count: {result['document_count']}")
    logger.info(f"Index status: {result['index_status']}")
    
    return result

def create_sample_document(domain: str, document_type: str = "general") -> Dict[str, Any]:
    """
    Create a sample document for the specified domain
    
    Args:
        domain: Business domain to create sample document for
        document_type: Type of sample document to create (general, faq, etc.)
        
    Returns:
        Dictionary with operation result
    """
    domain_dir = Path("data") / domain
    
    if not domain_dir.exists():
        logger.info(f"Creating domain directory: {domain}")
        domain_dir.mkdir(parents=True, exist_ok=True)
    
    result = {
        "success": False,
        "file_path": "",
        "error": ""
    }
    
    try:
        # Determine filename based on document type
        if document_type == "faq":
            filename = "sample_faq.md"
            content = f"""# Frequently Asked Questions about {domain.capitalize()}

## General Questions

### What is {domain.capitalize()}?
This is a sample FAQ document. Replace with actual {domain} information.

### How does {domain.capitalize()} work?
This is where you would explain how your {domain} service or product works.

## Pricing and Plans

### What pricing plans are available?
Describe your pricing structure here.

### Is there a free trial?
Explain your trial options here.

## Support

### How can I get help?
Provide contact information and support hours.

### Do you offer training?
Describe available training resources.
"""
        elif document_type == "guide":
            filename = "sample_guide.md"
            content = f"""# {domain.capitalize()} User Guide

## Introduction
This is a sample user guide for {domain}. Replace with actual information.

## Getting Started
1. Step one explanation
2. Step two explanation
3. Step three explanation

## Features
- Feature one description
- Feature two description
- Feature three description

## Advanced Usage
Explain advanced usage scenarios here.

## Troubleshooting
Common issues and their solutions.
"""
        else:  # general
            filename = "sample_info.md"
            content = f"""# About {domain.capitalize()}

## Overview
This is a sample document for the {domain} domain. Replace this content with actual information.

## Key Points
- Important point one
- Important point two
- Important point three

## Additional Information
Add any other relevant details here.
"""
        
        # Save the file
        file_path = domain_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
            
        logger.info(f"Created sample {document_type} document: {file_path}")
        
        result["success"] = True
        result["file_path"] = str(file_path)
        
    except Exception as e:
        error_msg = f"Error creating sample document: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Add documents to RAG system")
    parser.add_argument("--domain", type=str, help="Business domain to add documents for")
    parser.add_argument("--sources", nargs="+", help="Source file or directory paths")
    parser.add_argument("--clear", action="store_true", help="Clear existing documents before adding new ones")
    parser.add_argument("--list", action="store_true", help="List available business domains")
    parser.add_argument("--info", type=str, help="Get detailed information about a domain")
    parser.add_argument("--create-sample", type=str, help="Create a sample document for the specified domain")
    parser.add_argument("--sample-type", type=str, default="general", choices=["general", "faq", "guide"], 
                        help="Type of sample document to create")
    
    args = parser.parse_args()
    
    if args.list:
        list_domains()
        return
    
    if args.info:
        print_domain_info(args.info)
        return
    
    if args.create_sample:
        result = create_sample_document(args.create_sample, args.sample_type)
        if result["success"]:
            logger.info(f"Sample document created successfully: {result['file_path']}")
        else:
            logger.error(f"Failed to create sample document: {result['error']}")
        return
    
    if not args.domain:
        logger.error("Domain is required. Use --domain to specify business domain.")
        return
    
    if not args.sources:
        logger.error("No source paths provided. Use --sources to specify file or directory paths.")
        return
    
    add_documents(args.sources, args.domain, args.clear)

if __name__ == "__main__":
    main()
