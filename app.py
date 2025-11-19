
import faiss
import numpy as np
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dashscope import Generation, TextEmbedding
import os
from dashscope import Models

print("\n=== 你账号可用模型列表 ===")
try:
    models = Models.list()
    print(models)
except Exception as e:
    print("模型列表查询失败：", e)
print("=== END ===\n")

api_key = os.getenv('DASHSCOPE_API_KEY')
# ============ FastAPI 初始化 ============
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="web")

API_KEY = api_key   # ←← 修改这里！


# ============ 向量库（FAISS） ============
index = None        # faiss.IndexFlatL2 实例
index_dim = None    # 向量维度
doc_texts = []      # chunk 文本
doc_ids = []        # chunk 对应文件名


# ============ 工具：创建/重建索引 ============
def ensure_index(dim: int):
    global index, index_dim, doc_texts, doc_ids

    if index is None:
        print(f"\n== 创建新的 FAISS 索引，dim={dim} ==")
        index = faiss.IndexFlatL2(dim)
        index_dim = dim

    elif index_dim != dim:
        print(f"\n==⚠ 索引维度变化：旧 dim={index_dim} → 新 dim={dim} ==")
        print("== 重建索引并清空已有文档 ==")
        index = faiss.IndexFlatL2(dim)
        index_dim = dim
        doc_texts = []
        doc_ids = []


# ============ 工具：embedding ============
def embed_text(text: str):
    print("\n>>> 调用 embedding API")
    result = TextEmbedding.call(
        model="text-embedding-v2",   # ← 官方当前版本
        api_key=API_KEY,
        input=text
    )
    print("embedding API 返回：", result.output)

    emb_raw = result.output.get("embeddings", [None])[0]

    if emb_raw is None:
        raise ValueError("embedding API 返回结构异常：", result.output)

    # 兼容多种格式：{'embedding': [...]}
    if isinstance(emb_raw, dict):
        emb_list = emb_raw.get("embedding")
        if emb_list is None:
            raise ValueError("embedding 格式不含 'embedding' 字段：", emb_raw)
    else:
        emb_list = emb_raw

    emb_arr = np.array(emb_list, dtype="float32")
    print("最终 embedding 长度：", emb_arr.shape[0])

    return emb_arr


# ============ 工具：文本切分 ============
def split_text(text, chunk_size=200):
    """简单按字符窗口切分，更适合中文"""
    chunks = []
    text = text.replace("\n", " ").strip()

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


# ============ 首页 ============
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ============ 上传文件 ============
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global index, index_dim, doc_texts, doc_ids

    try:
        content = await file.read()

        # ---- 解析 txt ----
        if file.filename.endswith(".txt"):
            text = content.decode("utf-8", errors="ignore")

        # ---- 解析 pdf ----
        elif file.filename.endswith(".pdf"):
            import PyPDF2
            from io import BytesIO
            pdf = PyPDF2.PdfReader(BytesIO(content))
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])

        else:
            return JSONResponse({"error": "仅支持 txt / pdf"}, status_code=400)

        print("== 文档读取成功 ==")

        chunks = split_text(text)
        print(f"== 切分完成，共 {len(chunks)} 段 ==")

        for i, chunk in enumerate(chunks):
            print(f"\n--- 处理第 {i} 段 ---")
            print("chunk 内容（前50字符）：", chunk[:50])

            vec = embed_text(chunk)      # (dim,)
            ensure_index(vec.shape[0])   # 确保索引存在且维度一致

            vec_2d = np.expand_dims(vec, axis=0).astype("float32")  # shape (1, dim)
            index.add(vec_2d)

            doc_texts.append(chunk)
            doc_ids.append(file.filename)

        print("== 向量写入完成 ==")

        return JSONResponse({"msg": "success"})

    except Exception as e:
        print("\n❗❗ 捕获到错误：", e)
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


# ============ 重置向量库（开发用） ============
@app.post("/reset_index")
async def reset_index():
    global index, index_dim, doc_texts, doc_ids
    index = None
    index_dim = None
    doc_texts = []
    doc_ids = []
    print("\n== 已重置向量库 ==")
    return JSONResponse({"msg": "index reset"})


# ============ 聊天（RAG） ============
@app.post("/chat")
async def chat(req: dict):
    try:
        user_message = req.get("message", "")
        if not user_message:
            return JSONResponse({"reply": "收到空消息"}, status_code=400)

        #（1）没有文档，直接调用大模型
        if index is None or len(doc_texts) == 0:
            print("== 无文档，直接调用 qwen-turbo ==")

            result = Generation.call(
                model="qwen-turbo",       # ← 用你账号支持的模型
                api_key=API_KEY,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )

            print("raw generation output:", result.output)
            reply = parse_generation_result(result)
            return JSONResponse({
                "reply": reply or "模型返回为空，请检查服务器日志",
                "references": []
            })

        #（2）有文档 → RAG：embedding 检索
        query_vec = embed_text(user_message)
        ensure_index(query_vec.shape[0])

        D, I = index.search(np.array([query_vec]).astype("float32"), k=3)

        retrieved = []
        refs = set()
        for idx in I[0]:
            if 0 <= idx < len(doc_texts):
                retrieved.append(doc_texts[idx])
                refs.add(doc_ids[idx])

        context = "\n\n".join(retrieved)

        final_prompt = f"""
以下是和用户问题相关的文档内容片段：

{context}

请基于以上内容回答用户问题：
{user_message}
"""

        result = Generation.call(
            model="qwen-turbo",     # ← 仍然用你可用的模型
            api_key=API_KEY,
            messages=[{
                "role": "user",
                "content": final_prompt
            }]
        )

        print("raw generation output:", result.output)
        reply = parse_generation_result(result)

        return JSONResponse({
            "reply": reply or "模型返回为空，请检查服务器日志",
            "references": list(refs)
        })

    except Exception as e:
        print("聊天异常：", e)
        import traceback
        traceback.print_exc()
        return JSONResponse({"reply": "系统错误", "references": []})



def parse_generation_result(result):
    raw = getattr(result, "output", None)
    print("parse_generation_result raw:", raw)

    if not raw:
        return None

    if isinstance(raw, dict):
        if "choices" in raw:
            try:
                return raw["choices"][0]["message"]["content"]
            except:
                pass

        if "output_text" in raw:
            return raw["output_text"]

        if "text" in raw:
            return raw["text"]

    for attr in ("output_text", "text", "content"):
        val = getattr(result, attr, None)
        if isinstance(val, str):
            return val

    return None

