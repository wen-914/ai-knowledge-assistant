# 简易版AI知识助手

## 界面参考
<img width="1382" height="1244" alt="image" src="https://github.com/user-attachments/assets/357991d4-c4ae-477c-8a7a-9dc8f833cb74" />

简易版AI知识助手是一个基于FastAPI的文档问答系统，集成了阿里云DashScope的自然语言处理能力，可以上传文档并进行基于文档内容的智能问答。

## 功能特性

- **文档上传**：支持上传TXT和PDF格式的文档
- **智能问答**：基于上传的文档内容进行智能问答（RAG技术）
- **向量检索**：使用FAISS向量数据库进行高效文档检索
- **Web界面**：提供简洁易用的Web界面
- **多模型支持**：集成阿里云DashScope的多种语言模型

## 技术栈

- **框架**：FastAPI
- **向量数据库**：FAISS
- **文本嵌入**：DashScope text-embedding-v2
- **语言模型**：DashScope qwen-turbo
- **前端**：HTML + JavaScript
- **文件处理**：PyPDF2（PDF解析）

## 环境要求

- Python 3.11+
- 阿里云DashScope API密钥

## 安装部署

### 1. 克隆项目

```bash
git clone <项目地址>
cd ai-knowledge-assistant
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

设置环境变量：

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

### 5. 启动应用

```bash
uvicorn app:app --reload
```

应用将运行在 `http://localhost:8000`

## 使用方法

1. 启动应用后，打开浏览器访问 `http://localhost:8000`
2. 上传TXT或PDF文档（支持多文档）
3. 在聊天框中输入问题，系统会基于已上传文档的内容进行回答
4. 如果没有上传文档，系统会直接调用大语言模型进行回答

## API接口

- `GET /` - 主页
- `POST /upload` - 上传文档
- `POST /chat` - 聊天接口
- `POST /reset_index` - 重置向量库（开发用）

## 项目结构

```
ai-knowledge-assistant/
├── app.py          # FastAPI应用主文件
├── requirements.txt # 依赖包列表
├── web/            # 前端模板目录
│   └── index.html
├── static/         # 静态资源目录
└── uploads/        # 上传文件目录
```

## 开发说明

项目采用RAG（Retrieval-Augmented Generation）架构，通过以下步骤处理用户问题：

1. 对用户问题进行文本嵌入，生成向量表示
2. 在FAISS向量数据库中检索相关文档片段
3. 将检索到的文档内容与用户问题合并，构建提示
4. 调用大语言模型生成基于文档的回答

## 常见问题

Q: 为什么需要API密钥？
A: 项目使用阿里云DashScope的文本嵌入和语言模型服务，需要有效的API密钥。

Q: 支持哪些文档格式？
A: 目前支持TXT和PDF格式文档。

## 许可证

MIT License
