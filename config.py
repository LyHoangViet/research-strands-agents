import os
from dotenv import load_dotenv

load_dotenv()

# Đường dẫn gốc của dự án
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")

# Lấy model ID từ biến môi trường hoặc sử dụng giá trị mặc định
CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# AWS Configure
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Bedrock Configuration
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
BEDROCK_TEMPERATURE = float(os.getenv("BEDROCK_TEMPERATURE", "0.1"))

# Opensearch
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_COLLECTION_ID = os.getenv("OPENSEARCH_COLLECTION_ID")
OPENSEARCH_INDEX_NAME = os.getenv("OPENSEARCH_INDEX_NAME")