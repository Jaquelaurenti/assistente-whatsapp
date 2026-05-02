import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")

print(f"TOKEN: {token[:20] if token else 'NONE'}...")
print(f"DATABASE_ID: {db_id}")