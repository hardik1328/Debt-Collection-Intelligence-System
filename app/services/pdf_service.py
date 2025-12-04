import pypdf
import pdfplumber
import os
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDF text extraction"""
    
    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, int]:
        """Extract text from PDF"""
        try:
            text_content = []
            page_count = 0
            
            # Use pdfplumber for better text extraction
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {page_count} pages from {file_path}")
            return full_text, page_count
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise


class PDFMetadata:
    """Extract PDF metadata"""
    
    @staticmethod
    def get_metadata(file_path: str) -> dict:
        """Get PDF metadata"""
        try:
            with pypdf.PdfReader(file_path) as pdf:
                metadata = pdf.metadata or {}
                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                }
        except Exception as e:
            logger.error(f"Failed to get metadata from {file_path}: {str(e)}")
            return {}
