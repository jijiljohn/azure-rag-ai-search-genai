import requests
from bs4 import BeautifulSoup

def extract_website_text(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    clean_text = "\n".join(
        line.strip() for line in text.splitlines() if line.strip()
    )

    return clean_text
