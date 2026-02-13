
import sys
import requests
from bs4 import BeautifulSoup
import os

# We can reuse the `ask_rin_api` logic? No, that's in server.py.
# However, this script is called by server.py via subprocess.
# So we can just print the raw text, and let the calling RIN instance (the LLM) summarize it?
# Or we can have this script perform the extraction AND the summarization if it has keys.
# Let's start with EXTRACTION.

def fetch_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Kill script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:10000] # Limit to 10k chars for now
    except Exception as e:
        return f"[ERROR]: Could not fetch {url}: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    raw_text = fetch_text(url)
    print(f"--- EXTRACTED CONTENT FROM {url} ---")
    print(raw_text)
