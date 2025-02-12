import unicodedata

# Function to normalize text (remove accents, spaces, and convert to lowercase)
def normalize_text(text):
    if not text:
        return ""
    text = text.strip().lower()
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    text = text.replace(" ", "").replace("'", "").replace("’", "")  # Remove spaces and apostrophes
    return text