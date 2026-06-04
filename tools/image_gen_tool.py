"""ImageGenTool — 图像生成工具（Qwen-Image-2.0，DashScope SDK）。"""

from pathlib import Path
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

import os
import requests


class ImageGenInput(BaseModel):
    prompt: str = Field(
        description="图像描述提示词，例如：'一只可爱的橘猫坐在书桌上，午后阳光，皮克斯风格'"
    )
    size: str = Field(
        default="1024x1024",
        description="图像尺寸，可选: 1024x1024, 768x768, 768x1344, 1344x768, 720x1280, 1280x720"
    )
    save_path: str = Field(
        default="generated_image.png",
        description="保存图像的路径，相对于项目根目录"
    )


class ImageGenTool(BaseTool):
    name: str = "generate_image"
    description: str = (
        "使用 Qwen-Image-2.0 模型根据文字描述生成图像。"
        "适用于：AI绘画、插图生成、概念图创作等。"
        "输入提示词描述想要的画面，工具会生成图像并保存到本地文件。"
    )
    args_schema: Type[BaseModel] = ImageGenInput
    root_dir: str = ""

    def _run(self, prompt: str, size: str = "1024x1024", save_path: str = "generated_image.png") -> str:
        try:
            import dashscope

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                return "❌ DASHSCOPE_API_KEY not found in environment."

            dashscope.api_key = api_key

            print(f"[ImageGen] 生成图像: Qwen-Image-2.0, 尺寸: {size}")
            print(f"[ImageGen] 提示词: {prompt[:80]}...")

            response = dashscope.ImageSynthesis.call(
                model="qwen-image-2.0",
                prompt=prompt,
                size=size,
                n=1,
            )

            if response.status_code != 200:
                return f"❌ API 错误 ({response.status_code}): {response.message}"

            image_url = response.output.results[0].url
            if not image_url:
                return "❌ 图像生成成功但未返回 URL"

            print(f"[ImageGen] 下载图像中...")

            img_resp = requests.get(image_url, timeout=60)
            img_resp.raise_for_status()

            # 保存到本地
            root = Path(self.root_dir) if self.root_dir else Path.cwd()
            save_full = (root / save_path).resolve()

            if self.root_dir:
                if not str(save_full).startswith(str(root.resolve())):
                    return "❌ Access denied: path escapes allowed directory"

            save_full.parent.mkdir(parents=True, exist_ok=True)
            save_full.write_bytes(img_resp.content)

            file_size = len(img_resp.content) / 1024
            return f"✅ 图像已保存到: {save_full} ({file_size:.1f} KB)"

        except ImportError:
            return "❌ 需要安装依赖: pip install dashscope requests pillow"
        except Exception as e:
            return f"❌ 图像生成失败: {str(e)}"


def create_image_gen_tool(base_dir: Path) -> ImageGenTool:
    tool = ImageGenTool(root_dir=str(base_dir))
    return tool
