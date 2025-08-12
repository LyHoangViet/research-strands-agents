# Research Strands Agents

Dự án nghiên cứu và triển khai chatbot sử dụng **Strands Agent framework** với **AWS Bedrock** và **Claude AI**.

## 🚀 Tính năng chính

- ✅ **AWS Bedrock Integration**: Kết nối với Claude AI models
- ✅ **Strands-compatible**: Tương thích với Strands Agent framework
- ✅ **Multi-agent Support**: Hỗ trợ nhiều agent với personality khác nhau
- ✅ **Conversation Memory**: Ghi nhớ lịch sử cuộc trò chuyện
- ✅ **Flexible Configuration**: Cấu hình linh hoạt qua file .env
- ✅ **Easy Integration**: API đơn giản, dễ tích hợp

## 📁 Cấu trúc dự án

```
├── bedrock/                    # AWS Bedrock integration
│   ├── session.py             # AWS session management
│   ├── claude.py              # Claude AI client
│   ├── strands_adapter.py     # Strands framework adapter
│   └── __init__.py
├── src/                       # Source code chính
│   ├── agents/               # Agent implementations
│   ├── core/                 # Core framework
│   └── utils/                # Utilities
├── tests/                    # Test cases
├── config.py                 # Configuration management
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── README.md
```

## 🛠️ Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd research-strands-agents
```

### 2. Tạo virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Cài đặt dependencies

**Cài đặt cơ bản** (chỉ cần thiết):
```bash
pip install -r requirements.txt
```

**Cài đặt đầy đủ** (bao gồm API server và dev tools):
```bash
pip install -r requirements-dev.txt
```

### 4. Cấu hình AWS credentials
Sao chép file `.env.example` thành `.env` và điền thông tin AWS:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Agent Models
CHATBOT_AGENT_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

## 🎯 Cách sử dụng

### 1. Sử dụng cơ bản với Claude

```python
from bedrock.claude import ask_claude, chat_with_claude

# Cách đơn giản nhất
response = ask_claude("Xin chào! Bạn có khỏe không?")
print(response)

# Với system prompt
response = chat_with_claude(
    message="Giải thích về machine learning",
    system_prompt="Bạn là chuyên gia AI, trả lời bằng tiếng Việt",
    temperature=0.7
)
print(response)
```

### 2. Sử dụng với Strands-compatible API

```python
from bedrock.strands_adapter import create_agent, create_bedrock_model

# Tạo model (giống Strands BedrockModel)
bedrock_model = create_bedrock_model(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.3,
    max_tokens=2048
)

# Tạo agent (giống Strands Agent)
agent = create_agent(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    name="ChatBot",
    system_prompt="Bạn là trợ lý AI thông minh",
    temperature=0.7
)

# Sử dụng agent
response = agent("Tell me about Amazon Bedrock.")
print(response)
```

### 3. Conversation với memory

```python
from bedrock.strands_adapter import create_agent

agent = create_agent(
    name="Assistant",
    system_prompt="Bạn là trợ lý thông minh, hãy nhớ những gì người dùng nói"
)

# Cuộc trò chuyện có ngữ cảnh
response1 = agent("Tên tôi là John")
print(f"Agent: {response1}")

response2 = agent("Tên tôi là gì?")  # Agent sẽ nhớ tên
print(f"Agent: {response2}")
```

### 4. Multiple agents với personality khác nhau

```python
from bedrock.strands_adapter import create_agent

# Agent thơ ca
poet = create_agent(
    name="Poet",
    system_prompt="Bạn là nhà thơ, trả lời bằng ngôn ngữ thơ mộng",
    temperature=0.9
)

# Agent khoa học
scientist = create_agent(
    name="Scientist", 
    system_prompt="Bạn là nhà khoa học, trả lời chính xác và kỹ thuật",
    temperature=0.3
)

question = "Mô tả đại dương"
poet_response = poet(question)
scientist_response = scientist(question)

print(f"Poet: {poet_response}")
print(f"Scientist: {scientist_response}")
```

## 🧪 Testing

### Chạy test cơ bản
```bash
python tests/test_agents.py
```

### Chạy test Strands integration
```bash
python test_strands_integration.py
```

### Test cấu hình
```bash
python test_config.py
```

## ⚙️ Configuration

### File `.env` - Các biến môi trường:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Agent Models
CHATBOT_AGENT_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
OTHER_AGENT_MODEL=us.amazon.nova-micro-v1:0
POLICY_AGENT_MODEL=us.amazon.nova-micro-v1:0

# Bedrock Configuration  
BEDROCK_MAX_TOKENS=4096
BEDROCK_TEMPERATURE=0.7
```

### Các model có sẵn:
- `anthropic.claude-3-sonnet-20240229-v1:0` (Recommended)
- `anthropic.claude-3-haiku-20240307-v1:0` (Fast)
- `anthropic.claude-3-opus-20240229-v1:0` (Most capable)
- `us.amazon.nova-micro-v1:0` (AWS Nova)

## 📚 API Reference

### ClaudeClient
```python
from bedrock.claude import ClaudeClient

client = ClaudeClient()

# Basic chat
response = client.chat("Hello!")

# With options
response = client.chat(
    message="Explain AI",
    system_prompt="You are an expert",
    temperature=0.7,
    max_tokens=2048
)

# With conversation history
response = client.chat(
    message="Continue our discussion",
    conversation_history=[
        {"role": "user", "content": "Previous message"},
        {"role": "assistant", "content": "Previous response"}
    ]
)
```

### StrandsAgent
```python
from bedrock.strands_adapter import StrandsAgent, StrandsBedrockModel

# Create model
model = StrandsBedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.7
)

# Create agent
agent = StrandsAgent(
    model=model,
    name="MyAgent",
    system_prompt="You are helpful"
)

# Use agent
response = agent("Hello!")

# Reset conversation
agent.reset()
```

## 🔧 Troubleshooting

### Lỗi AWS credentials
```
❌ Error: AWS credentials not found
```
**Giải pháp**: Kiểm tra file `.env` có đúng AWS_ACCESS_KEY_ID và AWS_SECRET_ACCESS_KEY

### Lỗi model không tồn tại
```
❌ Error: Model not found
```
**Giải pháp**: Kiểm tra model_id trong `.env` và đảm bảo model được enable trong AWS Bedrock

### Lỗi region
```
❌ Error: Invalid region
```
**Giải pháp**: Kiểm tra AWS_REGION trong `.env`, sử dụng region hỗ trợ Bedrock như `us-east-1`

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

Dự án này sử dụng MIT License. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 🆘 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra [Troubleshooting](#-troubleshooting)
2. Chạy `python test_config.py` để kiểm tra cấu hình
3. Tạo issue trên GitHub với thông tin chi tiết

## 🔗 Links

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/)
- [Strands Agent Framework](https://strandsagents.com/)

---

**Happy coding! 🚀**