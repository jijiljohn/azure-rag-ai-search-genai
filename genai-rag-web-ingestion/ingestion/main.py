import os
import hashlib
from dotenv import load_dotenv
from web_scrapper import extract_website_text
from upload_blob import upload_text_to_blob

load_dotenv()

URL = os.getenv("TARGET_WEBSITE_URL")

def main():
    if not URL:
        raise ValueError("TARGET_WEBSITE_URL not set")

    text = extract_website_text(URL)
    file_id = hashlib.md5(URL.encode()).hexdigest()
    filename = f"{file_id}.txt"
    upload_text_to_blob(filename, text)

if __name__ == "__main__":
    main()
