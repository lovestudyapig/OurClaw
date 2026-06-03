"""TavilySearchTool — 基于 Tavily 的联网搜索工具。"""

import os
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class TavilySearchInput(BaseModel):
    """Input schema for tavily_search tool."""

    query: str = Field(description="搜索查询内容")
    max_results: int = Field(default=3, description="返回结果数量，默认3条")


class TavilySearchTool(BaseTool):
    """Tool for searching the web using Tavily API."""

    name: str = "tavily_search"
    description: str = (
        "使用 Tavily 搜索引擎进行联网搜索，获取实时信息。"
        "当需要获取最新信息、新闻、实时数据时使用此工具。"
        "输入应为搜索查询字符串。"
    )
    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: str, max_results: int = 3) -> str:
        """Execute Tavily search."""
        try:
            from langchain_tavily import TavilySearch

            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                return "❌ TAVILY_API_KEY not found in environment. Please set it in .env file."

            search = TavilySearch(
                max_results=min(max_results, 5),  # 最多5条
                api_key=api_key,
            )

            result = search.invoke(query)

            # 格式化结果
            if isinstance(result, dict) and "results" in result:
                formatted = []
                for idx, item in enumerate(result["results"], 1):
                    title = item.get("title", "无标题")
                    content = item.get("content", "")
                    url = item.get("url", "")
                    formatted.append(f"{idx}. **{title}**\n{content[:300]}...\n[来源: {url}]\n")
                return "\n".join(formatted)

            return str(result)[:2000]

        except ImportError:
            return "❌ langchain-tavily not installed. Run: pip install langchain-tavily"
        except Exception as e:
            return f"❌ Tavily search error: {str(e)}"


def create_tavily_search_tool() -> TavilySearchTool:
    """Create a Tavily search tool instance."""
    return TavilySearchTool()
