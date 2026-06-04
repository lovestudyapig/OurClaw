"""ImageUnderstandingTool — 图像理解工具（Qwen3.6-Plus 多模态，DashScope SDK）。"""

from pathlib import Path
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os
import base64
import io


class ImageUnderstandingInput(BaseModel):
    image_path: str = Field(
        description="图片文件的相对路径，例如: 'images/photo.jpg'、'docs/diagram.png'"
    )
    prompt: str = Field(
        default="请详细描述这张图片的内容，包括其中的文字、物体、场景和布局。",
        description="对图片提出的问题或分析指令"
    )


class ImageUnderstandingTool(BaseTool):
    name: str = "understand_image"
    description: str = (
        "使用 Qwen3.6-Plus 多模态模型理解图像内容。"
        "适用于：图片内容描述、OCR文字识别、图表分析、场景理解、物体检测等。"
        "支持 JPG、PNG、GIF、WEBP 等常见图片格式。"
        "输入图片路径和可选的提示词，返回模型对图像的理解结果。"
    )
    args_schema: Type[BaseModel] = ImageUnderstandingInput
    root_dir: str = ""

    def _run(self, image_path: str, prompt: str = "请详细描述这张图片的内容，包括其中的文字、物体、场景和布局。") -> str:
        try:
            import dashscope
            from PIL import Image

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return "❌ DASHSCOPE_API_KEY not found in environment."

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
            if not full_path.is_file():
                return f"❌ Not a file: {image_path}"

            # 读取图片并编码为 base64
            with Image.open(str(full_path)) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                data_url = f"data:image/png;base64,{b64}"

            print(f"[ImageUnderstanding] 分析图片: {full_path.name}")
            print(f"[ImageUnderstanding] 提示词: {prompt[:60]}...")

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
            return f"❌ 图像理解失败: {str(e)}"


def create_image_understanding_tool(base_dir: Path) -> ImageUnderstandingTool:
    tool = ImageUnderstandingTool(root_dir=str(base_dir))
    return tool
