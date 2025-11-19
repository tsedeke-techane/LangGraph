# test.py
from dotenv import load_dotenv
import os

load_dotenv()
print("GOOGLE_API_KEY exists:", bool(os.getenv("GOOGLE_API_KEY")))
print("Key length:", len(os.getenv("GOOGLE_API_KEY", "")))