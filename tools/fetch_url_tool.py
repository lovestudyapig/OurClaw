"""FetchURLTool — Fetch a URL and return cleaned Markdown content."""

from typing import Type

import html2text
import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class FetchURLInput(BaseModel):
    url: str = Field(description="The URL to fetch content from")


class FetchURLTool(BaseTool):
    name: str = "fetch_url"
    description: str = (
        "Fetch the content of a web page and return it as cleaned Markdown text. "
        "Use this to retrieve information from the internet. "
        "Input should be a valid URL (starting with http:// or https://)."
    )
    args_schema: Type[BaseModel] = FetchURLInput

    def _run(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; MiniOpenClaw/0.1)"
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")

            # If JSON, return directly
            if "application/json" in content_type:
                text = resp.text
                if len(text) > 5000:
                    text = text[:5000] + "\n...[truncated]"
                return text

            # Convert HTML to Markdown
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = True
            converter.body_width = 0
            markdown = converter.handle(resp.text)

            if len(markdown) > 5000:
                markdown = markdown[:5000] + "\n...[truncated]"
            return markdown

        except requests.Timeout:
            return "❌ Request timed out (15s limit)"
        except requests.RequestException as e:
            return f"❌ Fetch error: {str(e)}"


def create_fetch_url_tool() -> FetchURLTool:
    return FetchURLTool()


if __name__ == "__main__":
    # 1. 创建工具
    fetch_tool = create_fetch_url_tool()

    # 2. 测试1：请求天气API（JSON格式）
    print("===== 测试1：请求上海天气 =====")
    result1 = fetch_tool.invoke("https://wttr.in/shanghai,cn?format=j1&lang=zh-cn")
    print(result1)

    # 3. 测试2：请求普通网页（转Markdown）
    print("\n===== 测试2：请求网页 =====")
    result2 = fetch_tool.invoke("https://www.baidu.com")
    print(result2[:500])  # 只打印前500字符方便看