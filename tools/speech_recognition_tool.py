"""SpeechRecognitionTool — 语音识别工具。

三通道降级策略：
1. 主通道: qwen3.5-omni-flash 多模态模型（DashScope MultiModalConversation）— ✅ 已验证可用
2. 备选1: qwen3-asr-flash OpenAI 兼容接口（/v1/audio/transcriptions）
3. 备选2: qwen3-asr-flash DashScope 原生 Transcription API
"""

from __future__ import annotations

from pathlib import Path
from typing import Type
import base64
import os

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class SpeechRecognitionInput(BaseModel):
    audio_path: str = Field(
        description="音频文件的相对路径，例如: 'recordings/meeting.wav'、'audio/speech.mp3'"
    )
    language: str = Field(
        default="auto",
        description="音频语言，可选: zh（中文）、en（英文）、ja（日文），auto 自动检测"
    )


class SpeechRecognitionTool(BaseTool):
    name: str = "recognize_speech"
    description: str = (
        "使用 Qwen 多模态模型将语音转换为文字。"
        "适用于：语音转文字、会议记录转写、音频内容提取等。"
        "支持常见音频格式：WAV、MP3、M4A、AAC、FLAC、OGG、AMR 等。"
        "输入音频文件路径，返回识别后的文字内容。"
    )
    args_schema: Type[BaseModel] = SpeechRecognitionInput
    root_dir: str = ""

    def _resolve_path(self, audio_path: str) -> Path:
        p = Path(audio_path)
        if p.is_absolute():
            return p.resolve()
        root = Path(self.root_dir) if self.root_dir else Path.cwd()
        normalized = audio_path.replace("\\", "/").lstrip("./")
        return (root / normalized).resolve()

    # ── 主通道: qwen3.5-omni-flash 多模态 ──
    def _channel_omni(self, full_path: Path) -> str | None:
        try:
            import dashscope
            api_key = os.getenv("DASHSCOPE_API_KEY")
            dashscope.api_key = api_key

            with open(str(full_path), "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")

            suffix = full_path.suffix.lower()
            mime_map = {
                ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
                ".aac": "audio/aac", ".flac": "audio/flac", ".ogg": "audio/ogg",
                ".amr": "audio/amr",
            }
            mime = mime_map.get(suffix, "audio/mpeg")

            messages = [{"role": "user", "content": [
                {"audio": f"data:{mime};base64,{audio_b64}"},
                {"text": "请识别这段音频中的语音内容，直接输出识别出的文字，不要加任何额外说明。"}
            ]}]

            response = dashscope.MultiModalConversation.call(
                model="qwen3.5-omni-flash", messages=messages
            )

            if response.status_code == 200:
                choices = response.output.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", [])
                    for item in content:
                        if "text" in item:
                            return item["text"].strip()
            return None
        except Exception as e:
            print(f"[ASR] Omni 通道失败: {type(e).__name__}: {e}")
            return None

    # ── 备选1: OpenAI 兼容接口 ──
    def _channel_openai_asr(self, full_path: Path) -> str | None:
        try:
            from openai import OpenAI
            api_key = os.getenv("DASHSCOPE_API_KEY")
            base_url = os.getenv("DASHSCOPE_BASE_URL",
                                  "https://dashscope.aliyuncs.com/compatible-mode/v1")
            client = OpenAI(api_key=api_key, base_url=base_url)

            with open(str(full_path), "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="qwen3-asr-flash", file=audio_file,
                )
            return transcript.text.strip()
        except Exception as e:
            print(f"[ASR] OpenAI ASR 通道失败: {type(e).__name__}: {e}")
            return None

    # ── 备选2: DashScope 原生 ASR ──
    def _channel_dashscope_asr(self, full_path: Path) -> str | None:
        try:
            import dashscope
            import requests
            api_key = os.getenv("DASHSCOPE_API_KEY")
            dashscope.api_key = api_key

            with open(str(full_path), "rb") as f:
                upload_resp = requests.post(
                    "https://dashscope.aliyuncs.com/api/v1/files",
                    headers={"Authorization": f"Bearer {api_key}"},
                    files={"file": ("audio", f, "audio/mpeg")},
                    data={"purpose": "transcription", "model": "qwen3-asr-flash"}
                )
            if upload_resp.status_code != 200:
                return None
            file_id = upload_resp.json()["data"]["uploaded_files"][0]["file_id"]

            info_resp = requests.get(
                f"https://dashscope.aliyuncs.com/api/v1/files/{file_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if info_resp.status_code != 200:
                return None
            file_url = info_resp.json()["data"]["url"]

            result = dashscope.audio.asr.Transcription.call(
                model="qwen3-asr-flash", file_urls=[file_url],
            )
            if result.status_code == 200 and hasattr(result, 'output'):
                return result.output.get("text", "")
            return None
        except Exception as e:
            print(f"[ASR] DashScope ASR 通道失败: {type(e).__name__}: {e}")
            return None

    def _run(self, audio_path: str, language: str = "auto") -> str:
        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return "❌ DASHSCOPE_API_KEY 未配置"

            full_path = self._resolve_path(audio_path)

            if self.root_dir and not Path(audio_path).is_absolute():
                root = Path(self.root_dir).resolve()
                if not str(full_path).startswith(str(root)):
                    return "❌ 路径越权"

            if not full_path.exists():
                return f"❌ 文件不存在: {audio_path}"
            if not full_path.is_file():
                return f"❌ 不是文件: {audio_path}"

            file_size_mb = full_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 25:
                return f"❌ 音频文件过大 ({file_size_mb:.1f}MB)，需小于 25MB"

            print(f"[ASR] 识别: {full_path.name} ({file_size_mb:.1f}MB)")

            # 主通道 → 备选1 → 备选2
            result = self._channel_omni(full_path)
            if result:
                return result

            result = self._channel_openai_asr(full_path)
            if result:
                return result

            result = self._channel_dashscope_asr(full_path)
            if result:
                return result

            return "❌ 所有识别通道均失败，请检查 DashScope API 状态"

        except Exception as e:
            return f"❌ 语音识别失败: {type(e).__name__}: {str(e)}"


def create_speech_recognition_tool(base_dir: Path) -> SpeechRecognitionTool:
    return SpeechRecognitionTool(root_dir=str(base_dir))
