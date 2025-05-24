"""
Helper functions for RAG document loading and processing.
"""
import logging
import re

logger = logging.getLogger(__name__)

def _clean_website_content(text: str) -> str:
    """Clean up website content by removing noise and formatting."""
    
    # Remove excessive whitespace and newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
    
    # Remove common web elements
    patterns_to_remove = [
        r'© \d{4}.*?rights reserved.*?(?:\n|$)',
        r'Terms of Service.*?Privacy Policy.*?(?:\n|$)',
        r'We use cookies.*?Privacy Policy.*?(?:\n|$)',
        r'Accept\s*$',
        r'Submit\s*$',
        r'click for next image.*?(?:\n|$)',
        r'Next\s*Cancel\s*(?:\n|$)',
        r'Download count:.*?(?:\n|$)',
        r'\(Click on any tool to see more information\)',
        r'briefcase Created with Sketch.*?(?:\n|$)',
        r'github \[#\d+\] Created with Sketch.*?(?:\n|$)',
        r'Contact Form\s*(?:\n|$)',
        r'Terms of Service\s*(?:\n|$)',
        r'Privacy Policy\s*(?:\n|$)',
        r'We use cookies.*?Privacy Policy\.',
        r'Contact:\s*\[email.*?protected\]\s*(?:\n|$)',
        r'Download CV\s*(?:\n|$)',
        r'CV\s*(?:\n|$)',
        r'Based In\s*(?:\n|$)',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove form fields pattern
    text = re.sub(r'(First name|Last name|Email address|Phone Number|Message)\s*(?:\n|$)', '', text)
    
    # Clean up tool/year patterns (like "4+ Years", "2021 - 2024")
    text = re.sub(r'^\d+\+?\s*Years?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d{4}\s*-\s*\d{4}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove standalone symbols and short fragments
    text = re.sub(r'^\s*[•\-\+]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[^\w\s]\s*$', '', text, flags=re.MULTILINE)
    
    # Final cleanup
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines again
    text = text.strip()
    
    return text
    
def filter_meaningful_content(documents: list) -> list:
    """Filter out documents with minimal meaningful content."""
    filtered_docs = []
    
    for doc in documents:
        # Clean the content
        cleaned_content = _clean_website_content(doc.page_content)
        
        # Skip if too short or mostly whitespace after cleaning
        if len(cleaned_content.strip()) < 50:
            logger.debug(f"Skipping short document: {cleaned_content[:50]}...")
            continue
        
        # Skip if mostly navigation/form content
        nav_keywords = ['click', 'submit', 'accept', 'cancel', 'download', 'next', 'previous']
        if sum(keyword in cleaned_content.lower() for keyword in nav_keywords) > 3:
            logger.debug(f"Skipping navigation document: {cleaned_content[:50]}...")
            continue
        
        # Update the document with cleaned content
        doc.page_content = cleaned_content
        filtered_docs.append(doc)
    
    return filtered_docs