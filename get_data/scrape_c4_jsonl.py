import requests
from bs4 import BeautifulSoup
import re
import json
import datetime
# Configuration
CONFLUENCE_BASE_URL = 'https://confluence.com'
PARENT_PAGE_ID = '1234'  # Replace with the ID of the parent page
PERSONAL_ACCESS_TOKEN = 'TOKEN'
headers = {
   "Accept": "application/json",
   "Authorization": f"Basic {PERSONAL_ACCESS_TOKEN}"
}
def fetch_page_content(page_id):
   url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}?expand=body.view,children.page"
   response = requests.get(url, headers=headers, verify=False)
   print(response)
   if response.status_code == 200:
       return response.json()
   else:
       return None
def get_all_pages(page_id, collected_pages=None):
   if collected_pages is None:
       collected_pages = []
   page_data = fetch_page_content(page_id)
   if page_data:
       collected_pages.append(page_data)
       children = page_data.get('children', {}).get('page', {}).get('results', [])
       for child in children:
           get_all_pages(child['id'], collected_pages)
   return collected_pages
def extract_text_from_html(html):
   soup = BeautifulSoup(html, 'html.parser')
   for script in soup(["script", "style"]):
       script.extract()  # Remove script and style tags
   text = soup.get_text()
   lines = (line.strip() for line in text.splitlines())
   chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
   text = '\n'.join(chunk for chunk in chunks if chunk)
   return text
def clean_text(text):
   text = re.sub(r'\[.*?\]', '', text)  # Remove text in brackets
   text = re.sub(r'http\S+', '', text)  # Remove URLs
   text = re.sub(r'\s+', ' ', text)     # Replace multiple spaces with a single space
   text = text.strip()
   return text
def create_c4_document(page):
   document = {
       "url": f"{CONFLUENCE_BASE_URL}/spaces/{page['space']['key']}/pages/{page['id']}",
       "text": clean_text(extract_text_from_html(page['body']['view']['value'])),
       "timestamp": datetime.datetime.utcnow().isoformat()
   }
   return document
pages = get_all_pages(PARENT_PAGE_ID)
c4_documents = [create_c4_document(page) for page in pages if 'body' in page and 'view' in page['body']]
with open('toy_c4_dataset.jsonl', 'w') as f:
   for doc in c4_documents:
       json.dump(doc, f)
       f.write('\n')
