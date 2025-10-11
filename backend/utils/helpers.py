"""
Utility functions and helpers
Small functions used across the application
"""

def format_docs(docs):
    """Format retrieved documents for display"""
    return "\n\n".join(doc.page_content for doc in docs)

def ensure_list(val):
    """Ensure value is a list, convert if necessary"""
    if isinstance(val, list):
        return val
    if val is None:
        return []
    return [val]

def clean_text(text):
    """Clean and normalize text input"""
    if not text:
        return ""
    return text.strip()

def truncate_text(text, max_length=100):
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_similarity_score(score):
    """Format similarity score as percentage"""
    return f"{score:.1%}"
