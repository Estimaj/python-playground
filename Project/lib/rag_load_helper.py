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

def filter_notion_content(documents: list) -> list:
    """Filter and clean notion to-do content for meaningful RAG content."""
    filtered_docs = []
    
    for doc in documents:
        content = doc.page_content.strip()
        
        # Skip if too short
        if len(content) < 100:
            continue
            
        # Skip if mostly JIRA tickets/URLs (more than 2 URLs)
        url_count = len(re.findall(r'https?://[^\s]+', content))
        if url_count > 2:
            logger.debug(f"Skipping URL-heavy chunk: {url_count} URLs found")
            continue
            
        # Skip if mostly checkboxes without explanations
        checkbox_count = content.count('[x]') + content.count('[ ]')
        explanation_sentences = len([s for s in content.split('.') if len(s.strip()) > 20])
        
        if checkbox_count > 5 and explanation_sentences < 2:
            logger.debug(f"Skipping checkbox-heavy chunk: {checkbox_count} checkboxes, {explanation_sentences} explanations")
            continue
            
        # Keep chunks with business logic, explanations, or technical content
        valuable_keywords = [
            'swap', 'item', 'customer', 'sync', 'integration', 'api', 'endpoint', 
            'payment', 'checkout', 'session', 'account', 'invoice', 'order',
            'ddms', 'eautomate', 'bmi', 'pricing', 'contract', 'department',
            'how does', 'when', 'then', 'implement', 'deploy', 'test', 'review',
            'meeting notes', 'scope', 'create', 'update', 'fix', 'issue'
        ]
        
        if any(keyword in content.lower() for keyword in valuable_keywords):
            # Clean up the content
            cleaned_content = _clean_notion_content(content)
            if len(cleaned_content.strip()) > 50:
                doc.page_content = cleaned_content
                filtered_docs.append(doc)
                logger.debug(f"Keeping meaningful chunk: {cleaned_content[:100]}...")
        
    return filtered_docs

def _clean_notion_content(text: str) -> str:
    """Clean notion content by removing noise while keeping meaningful parts."""
    
    # Remove standalone dates and numbers
    text = re.sub(r'^\d{1,2}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d{1,2}/\d{1,2}$', '', text, flags=re.MULTILINE)
    
    # Remove excessive checkboxes lines without context
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip lines that are just checkboxes with very short tasks
        if re.match(r'^\[x\]\s*.{1,15}$', line):
            continue
        # Skip standalone URLs
        if re.match(r'^https?://[^\s]+$', line):
            continue
            
        cleaned_lines.append(line)
    
    # Rejoin and clean up spacing
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()