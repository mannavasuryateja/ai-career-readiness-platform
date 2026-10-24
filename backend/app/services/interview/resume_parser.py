"""Resume parsing service for extracting text and generating summaries"""
import re
from typing import Optional


class ResumeParser:
    """Parses resume files and extracts text"""

    @staticmethod
    def parse_pdf(file_path: str) -> Optional[str]:
        """Parse PDF file and extract text using pdfplumber"""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip() if text.strip() else None
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

    @staticmethod
    def parse_docx(file_path: str) -> Optional[str]:
        """Parse DOCX file and extract text using python-docx"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text.strip() if text.strip() else None
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")

    @staticmethod
    def parse_txt(file_path: str) -> Optional[str]:
        """Parse TXT file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            return text if text else None
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")

    @staticmethod
    def extract_text(file_path: str, filename: str) -> Optional[str]:
        """
        Extract text from any supported file format based on extension
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename to determine file type
            
        Returns:
            Extracted text or None
        """
        extension = filename.lower().split(".")[-1]

        if extension == "pdf":
            return ResumeParser.parse_pdf(file_path)
        elif extension in ("docx", "doc"):
            return ResumeParser.parse_docx(file_path)
        elif extension == "txt":
            return ResumeParser.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    @staticmethod
    def generate_summary(extracted_text: str, max_length: int = 300) -> str:
        """
        Generate a concise summary from extracted text using simple heuristics
        
        Args:
            extracted_text: Raw text extracted from resume
            max_length: Maximum length of summary in characters
            
        Returns:
            Generated summary (ensures non-empty result)
        """
        if not extracted_text or len(extracted_text.strip()) < 10:
            return "Resume content available"

        text = extracted_text.strip()
        
        # Split into lines and filter empty ones
        lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 8]
        
        if not lines:
            return text[:max_length].strip() if len(text) > 0 else "Resume content available"

        # Collect first meaningful lines to form a summary
        summary_parts = []
        char_count = 0

        for line in lines:
            # Stop if we've reached max length
            if char_count + len(line) + 1 > max_length:
                break
            
            summary_parts.append(line)
            char_count += len(line) + 1  # +1 for space/separator

        # Join and create final summary
        summary = " ".join(summary_parts)
        
        # Ensure summary is never empty
        if not summary or len(summary.strip()) < 10:
            # Fallback: take raw text
            summary = text[:max_length].strip()
        
        # Final fallback if still empty
        if not summary or len(summary.strip()) < 5:
            summary = "Resume content available"
        
        return summary

    @staticmethod
    def extract_key_technologies(extracted_text: str) -> list:
        """Extract common programming languages and technologies from resume text"""
        technologies = [
            "python",
            "javascript",
            "java",
            "csharp",
            "golang",
            "rust",
            "typescript",
            "react",
            "vue",
            "angular",
            "django",
            "fastapi",
            "node",
            "express",
            "sql",
            "mongodb",
            "postgresql",
            "aws",
            "gcp",
            "azure",
            "docker",
            "kubernetes",
            "git",
        ]

        found_tech = []
        text_lower = extracted_text.lower()

        for tech in technologies:
            if tech in text_lower:
                found_tech.append(tech)

        return list(set(found_tech))[:10]  # Return up to 10 unique technologies
