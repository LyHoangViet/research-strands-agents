# Research Strands Agents

Dự án nghiên cứu và triển khai hệ thống multi-agent sử dụng **Strands Agent framework** với **AWS Bedrock** và **Claude AI**. Hỗ trợ nhiều kiểu agent pattern: Orchestrator, Graph, Swarm, và Workflow.

## 🚀 Tính năng chính

- ✅ **Multi-Agent Patterns**: Orchestrator, Graph, Swarm, Workflow
- ✅ **AWS Bedrock Integration**: Kết nối với Claude AI và Nova models
- ✅ **Document Processing**: Textract integration cho xử lý tài liệu
- ✅ **Streaming Support**: Real-time response streaming
- ✅ **FastAPI Backend**: RESTful API cho tích hợp
- ✅ **Comprehensive Tools**: AWS resource management, pricing, documentation
- ✅ **Docker Support**: Containerized deployment
- ✅ **Flexible Configuration**: Environment-based configuration

## 📁 Cấu trúc dự án

```
├── agent_chatbot_orchestrator/     # Agent orchestrator pattern
│   ├── agents/                    # Specialized agents (account, architect, docs)
│   ├── tools/                     # Agent tools
│   └── orchestrator_agent.py      # Main orchestrator
├── agent_textract_graph/          # Document processing graph
│   ├── tools/                     # Textract, classify, format tools
│   ├── textract_agent.py          # Graph-based document processing
│   └── ui_textract.py             # Streamlit UI
├── agent_plan_swarm/              # Swarm agent pattern
│   └── swarm_agent.py             # Multi-agent collaboration
├── agent_infra_workflow/          # Workflow management
│   └── flow_agent.py              # Sequential workflow processing
├── bedrock/                       # AWS Bedrock integration
│   ├── session.py                 # AWS session management
│   └── claude.py                  # Claude AI client
├── src/                           # Core framework
│   ├── agents/                    # Base agents (docs, pricing, resource)
│   ├── tools/                     # AWS tools (cost, pricing, resources)
│   └── utils/                     # Configuration and logging
├── api/                           # FastAPI application
├── tests/                         # Comprehensive test suite
├── docker/                        # Docker configuration
├── scripts/                       # Utility scripts
└── config/                        # Configuration files
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
```bash
pip install -r requirements.txt
```

### 4. Cấu hình AWS credentials
Sao chép file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token  # Optional for temporary credentials
AWS_REGION=us-east-1

# Agent Models
CHATBOT_AGENT_MODEL=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# Bedrock Configuration
BEDROCK_MAX_TOKENS=10000
BEDROCK_TEMPERATURE=0.1

# OpenSearch (Optional)
OPENSEARCH_HOST=
OPENSEARCH_COLLECTION_ID=
OPENSEARCH_INDEX_NAME=
```

## 🎯 Cách sử dụng

### 1. Agent Orchestrator Pattern
```bash
python agent_chatbot_orchestrator/orchestrator_agent.py
```

Orchestrator tự động định tuyến câu hỏi đến agent phù hợp:
- **Account Agent**: Thông tin tài khoản AWS và resources
- **Architect Agent**: Thiết kế kiến trúc AWS
- **Docs Agent**: Tìm kiếm tài liệu AWS

### 2. Document Processing Graph
```bash
python agent_textract_graph/textract_agent.py
```

Xử lý tài liệu qua workflow:
1. **Textract**: Trích xuất text từ document
2. **Classify**: Phân loại nội dung
3. **Format**: Định dạng kết quả

### 3. Swarm Agent Pattern
```bash
python agent_plan_swarm/swarm_agent.py
```

Multi-agent collaboration với handoff mechanism.

### 4. Workflow Management
```bash
python agent_infra_workflow/flow_agent.py
```

Sequential workflow với dependencies:
- Research → Analysis → Report

### 5. FastAPI Server
```bash
python api/app.py
# hoặc
uvicorn api.app:app --reload
```

### 6. Streamlit UI (Textract)
```bash
streamlit run agent_textract_graph/ui_textract.py
```

### 7. Console Mode
```bash
python main.py
```

## 🧪 Testing

### Chạy tất cả tests
```bash
pytest tests/
```

### Test từng agent pattern
```bash
python tests/test_agent_orchestrator.py
python tests/test_agent_graph.py
python tests/test_agent_swarm.py
python tests/test_agent_workflow.py
```

## 🐳 Docker Deployment

```bash
cd docker
docker-compose up --build
```

Service sẽ chạy trên port 8000 với health check.

## ⚙️ Configuration

### Supported Models
- `us.anthropic.claude-3-7-sonnet-20250219-v1:0` (Default)
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `us.amazon.nova-micro-v1:0`

### AWS Tools Available
- **Resource Management**: List và detail AWS resources
- **Cost Analysis**: Usage và pricing information
- **Documentation**: AWS docs search
- **Textract**: Document processing

## 📚 API Examples

### Orchestrator với Streaming
```python
from agent_chatbot_orchestrator.orchestrator_agent import process_streaming_response

async for chunk in process_streaming_response("Account của tôi có những resource nào?"):
    print(chunk, end="")
```

### Document Processing
```python
from agent_textract_graph.textract_agent import process_document

result = process_document("/path/to/document.pdf")
print(result)
```

### Claude Client
```python
from bedrock.claude import ClaudeClient

client = ClaudeClient()
response = client.chat(
    message="Explain AWS Lambda",
    system_prompt="You are an AWS expert",
    temperature=0.7
)
```

## 🔧 Troubleshooting

### AWS Credentials
```bash
# Test AWS connection
aws sts get-caller-identity

# Hoặc check trong Python
python -c "import boto3; print(boto3.Session().get_credentials())"
```

### Model Access
Đảm bảo model được enable trong AWS Bedrock console:
1. Vào AWS Bedrock console
2. Model access → Request model access
3. Enable các model cần thiết

### Region Support
Sử dụng regions hỗ trợ Bedrock:
- `us-east-1` (Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

## 🎨 Agent Patterns

### 1. Orchestrator Pattern
- **Use case**: Routing queries to specialized agents
- **Benefits**: Clear separation of concerns, scalable
- **Example**: AWS support chatbot

### 2. Graph Pattern  
- **Use case**: Sequential processing with dependencies
- **Benefits**: Structured workflow, parallel execution
- **Example**: Document processing pipeline

### 3. Swarm Pattern
- **Use case**: Collaborative problem solving
- **Benefits**: Dynamic handoffs, flexible collaboration
- **Example**: Research and analysis tasks

### 4. Workflow Pattern
- **Use case**: Predefined business processes
- **Benefits**: Repeatable, auditable workflows
- **Example**: Infrastructure provisioning

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-agent-pattern`
3. Implement changes với tests
4. Commit: `git commit -m 'Add new agent pattern'`
5. Push: `git push origin feature/new-agent-pattern`
6. Tạo Pull Request

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

## 🆘 Support

### Debug Steps
1. Check AWS credentials: `aws configure list`
2. Test Bedrock access: `python tests/test_agent_orchestrator.py`
3. Verify model access trong AWS console
4. Check logs trong `logs/` directory

### Common Issues
- **Timeout errors**: Giảm `BEDROCK_MAX_TOKENS` hoặc tăng timeout
- **Model not found**: Enable model trong Bedrock console
- **Permission denied**: Check IAM permissions cho Bedrock

## 🔗 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Agent Framework](https://github.com/strands-ai/strands-agents)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Multi-Agent AI với AWS Bedrock! 🚀**