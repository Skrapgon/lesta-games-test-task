import re

def get_text_length(text: str):
    text_words = re.findall(r'\b\w+\b', text, re.UNICODE)
    return len(text_words)

def split_text(text: str):
    text_words = re.findall(r'\b\w+\b', text.lower(), re.UNICODE)
    return text_words