# Strands Agent Chatbot

Dự án chatbot sử dụng framework Strands Agent với kiến trúc modular và khả năng mở rộng cao.

## Cấu trúc dự án

```
├── src/                    # Mã nguồn chính
│   ├── agents/            # Các agent modules
│   ├── core/              # Core framework components
│   └── utils/             # Tiện ích và helpers
├── config/                # File cấu hình
├── tests/                 # Test cases
├── api/                   # FastAPI application
├── docker/                # Docker configuration
├── scripts/               # Utility scripts
├── docs/                  # Tài liệu
└── logs/                  # Log files (tự động tạo)
```

## Tính năng chính

- **Kiến trúc Strands**: Quản lý nhiều agent và luồng xử lý
- **Base Agent**: Lớp cơ sở cho tất cả agents
- **Message Handler**: Xử lý và định tuyến tin nhắn
- **Configuration**: Quản lý cấu hình linh hoạt
- **Logging**: Hệ thống log chi tiết
- **API REST**: FastAPI endpoint cho tích hợp
- **Docker**: Containerization support

## Cài đặt

1. Clone repository
2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Sử dụng

### Console Mode
```bash
python main.py
```

### API Mode
```bash
python scripts/run.py --mode api
```

### Docker
```bash
cd docker
docker-compose up --build
```

## Testing

```bash
pytest tests/
```

## Cấu hình

Chỉnh sửa file `config/config.json` để tùy chỉnh:
- Agent personality
- Logging levels
- API settings
- Strands parameters