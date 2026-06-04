"""ImageAnalyzerTool — 分析图片内容（Qwen3.6-Plus 多模态，DashScope SDK）。"""

from pathlib import Path
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os
import base64
import io


class ImageAnalyzerInput(BaseModel):
    image_path: str = Field(
        description="图片文件的相对路径，例如: 'images/photo.jpg'"
    )
    prompt: str = Field(
        default="描述这张图片的内容",
        description="分析图片的提示词"
    )


class ImageAnalyzerTool(BaseTool):
    name: str = "analyze_image"
    description: str = (
        "分析图片内容，使用 Qwen3.6-Plus 多模态模型描述图片。"
        "适用于：图片内容理解、OCR识别、图片描述等。"
        "支持 JPG、PNG 等常见格式。"
    )
    args_schema: Type[BaseModel] = ImageAnalyzerInput
    root_dir: str = ""

    def _run(self, image_path: str, prompt: str = "描述这张图片的内容") -> str:
        try:
            import dashscope
            from PIL import Image

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return "❌ 需要设置 DASHSCOPE_API_KEY 环境变量"

            dashscope.api_key = api_key

            root = Path(self.root_dir) if self.root_dir else Path.cwd()
            normalized = image_path.replace("\\", "/").lstrip("./")
            full_path = (root / normalized).resolve()

            # 沙盒检查
            if self.root_dir:
                if not str(full_path).startswith(str(root.resolve())):
                    return "❌ Access denied: path escapes allowed directory"

            if not full_path.exists():
                return f"❌ File not found: {image_path}"

            # 读取图片并编码为 base64
            with Image.open(str(full_path)) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            data_url = f"data:image/png;base64,{b64}"
            print(f"[ImageAnalyze] 分析图片: {full_path.name}")

            # 使用 DashScope 多模态对话
            response = dashscope.MultiModalConversation.call(
                model="qwen3.6-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {"image": data_url},
                        {"text": prompt},
                    ]
                }],
            )

            if response.status_code == 200:
                choices = response.output.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", [])
                    for item in content:
                        if "text" in item:
                            return item["text"].strip()
                return "❌ 未能从响应中提取文本"
            else:
                return f"❌ API 错误 ({response.status_code}): {response.message}"

        except ImportError:
            return "❌ 需要安装依赖: pip install dashscope pillow"
        except Exception as e:
            return f"❌ 图片分析失败: {str(e)}"


def create_image_analyzer_tool(base_dir: Path) -> ImageAnalyzerTool:
    tool = ImageAnalyzerTool(root_dir=str(base_dir))
    return tool
