"""
Claw Web UI — FastAPI Web 服务器

启动方式:  uvicorn app:app --reload --host 0.0.0.0 --port 8000
或直接:    python app.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# 将项目根目录加入 sys.path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv

load_dotenv()

# 延迟导入 Claw，确保环境变量先加载
from Claw import CoreClawAgent

app = FastAPI(title="Claw Web UI", version="1.0.0")

# 挂载静态文件
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 全局 Agent 实例（单例）
_agent: Optional[CoreClawAgent] = None


def get_agent() -> CoreClawAgent:
    global _agent
    if _agent is None:
        _agent = CoreClawAgent(base_dir=BASE_DIR)
    return _agent


# ==================== API 路由 ====================


@app.get("/")
async def index():
    """首页 - 返回前端界面"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "index.html not found"}


@app.get("/api/files")
async def list_files(path: str = Query("", description="要列出的目录路径")):
    """列出指定路径下的文件和目录"""
    try:
        if not path:
            # 默认返回当前工作目录
            agent = get_agent()
            work_dir = agent.get_work_dir()
            if work_dir:
                path = work_dir
            else:
                return {
                    "path": "",
                    "entries": [
                        {"name": d.name, "type": "dir", "path": str(d)}
                        for d in [BASE_DIR, Path.home(), Path("/Volumes") if os.name == "posix" else Path("C:\\")]
                        if d.exists()
                    ],
                }

        target = Path(path)
        if not target.exists():
            return JSONResponse({"error": f"路径不存在: {path}"}, status_code=404)
        if not target.is_dir():
            return JSONResponse({"error": f"不是目录: {path}"}, status_code=400)

        entries = []
        for item in sorted(target.iterdir()):
            try:
                info = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else 0,
                }
                entries.append(info)
            except (PermissionError, OSError):
                continue

        return {"path": str(target), "entries": entries}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/read-file")
async def read_file(path: str = Query("", description="要读取的文件路径")):
    """读取文件内容（文本文件），支持 .md/.py/.txt/.json/.yaml 等"""
    if not path:
        return JSONResponse({"error": "path 参数必填"}, status_code=400)
    try:
        # 如果是相对路径（如 webkitRelativePath），用工作目录拼接
        p = Path(path)
        if not p.is_absolute():
            agent = get_agent()
            work_dir = agent.get_work_dir()
            if work_dir:
                target = (Path(work_dir) / path).resolve()
            else:
                target = p.resolve()
        else:
            target = p.resolve()

        if not target.exists():
            return JSONResponse({"error": f"文件不存在: {path}"}, status_code=404)
        if not target.is_file():
            return JSONResponse({"error": f"不是文件: {path}"}, status_code=400)

        size = target.stat().st_size
        if size > 512 * 1024:  # 大于 512KB 只返回提示
            return {"path": str(target), "size": size, "truncated": True,
                    "content": f"⚠️ 文件过大 ({size//1024}KB)，仅显示前 512KB。\n\n"}

        # 自动检测编码
        raw = target.read_bytes()
        for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            text = raw.decode("utf-8", errors="replace")

        return {"path": str(target), "size": size, "content": text, "truncated": False}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """流式聊天接口（SSE）"""
    body = await request.json()
    user_input = body.get("message", "").strip()
    if not user_input:
        return JSONResponse({"error": "消息不能为空"}, status_code=400)

    agent = get_agent()

    async def event_generator():
        try:
            async for event in agent.stream_chat_with_events(user_input):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/chat/send")
async def chat_send(request: Request):
    """非流式聊天接口（简单调用）"""
    body = await request.json()
    user_input = body.get("message", "").strip()
    if not user_input:
        return JSONResponse({"error": "消息不能为空"}, status_code=400)

    agent = get_agent()
    try:
        response = await agent.chat(user_input)
        return {"response": response}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/export-log")
async def export_log(request: Request):
    """导出完整对话日志到指定目录"""
    body = await request.json()
    save_dir = body.get("save_dir", "")
    agent = get_agent()

    try:
        log_path = agent.export_log(save_dir if save_dir else None)
        return {"path": log_path, "message": f"日志已导出到: {log_path}"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/status")
async def status():
    """获取 Agent 状态"""
    agent = get_agent()
    tools = [{"name": t.name, "description": t.description[:60]} for t in agent.tools]
    return {
        "tools": tools,
        "model": getattr(agent.llm, "model_name", None) or getattr(agent.llm, "model", "unknown"),
        "message_count": len(agent.messages),
    }


@app.post("/api/clear")
async def clear_history():
    """清除对话历史"""
    agent = get_agent()
    agent.clear_history()
    return {"message": "对话历史已清除"}


@app.post("/api/set-work-dir")
async def set_work_dir(request: Request):
    """设置工作目录（通知 Claw + 更新工具沙盒）"""
    body = await request.json()
    path = body.get("path", "").strip()
    if not path:
        return JSONResponse({"error": "路径不能为空"}, status_code=400)

    agent = get_agent()
    result = agent.set_work_dir(path)
    return {"message": result}


@app.get("/api/current-dir")
async def current_dir():
    """获取当前工作目录"""
    agent = get_agent()
    return {"work_dir": agent.get_work_dir()}


@app.post("/api/upload-audio")
async def upload_audio(request: Request):
    """上传音频到 Audio/ 目录，返回绝对路径"""
    try:
        # 确保 Audio 目录存在
        audio_dir = BASE_DIR / "Audio"
        audio_dir.mkdir(exist_ok=True)

        form = await request.form()
        audio_file = form.get("audio")
        if not audio_file:
            return JSONResponse({"error": "未找到音频文件"}, status_code=400)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = Path(audio_file.filename).suffix if audio_file.filename else ".mp3"
        save_name = f"voice_{timestamp}{suffix}"
        save_path = audio_dir / save_name

        content = await audio_file.read()
        save_path.write_bytes(content)

        return {
            "path": str(save_path.resolve()),
            "filename": save_name,
            "size": len(content),
        }
    except Exception as e:
        return JSONResponse({"error": f"音频上传失败: {str(e)}"}, status_code=500)


# ==================== 入口 ====================

if __name__ == "__main__":
    print(f"🚀 Claw Web UI 启动中...")
    print(f"📁 项目目录: {BASE_DIR}")
    print(f"🌐 打开浏览器访问: http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
