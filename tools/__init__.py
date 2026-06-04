"""Core Tools factory — returns all tools for the Agent."""

from pathlib import Path
from typing import List, Union

from langchain_core.tools import BaseTool

from .fetch_tavily_tool import create_tavily_search_tool
from .fetch_url_tool import create_fetch_url_tool
from .python_repl_tool import create_python_repl_tool
from .read_file_tool import create_read_file_tool, create_read_skill_tool
from .terminal_tool import create_terminal_tool
from .write_memory_tool import create_write_memory_tool
# 导入新工具
from .pdf_parser_tool import create_pdf_parser_tool
from .word_parser_tool import create_word_parser_tool
from .image_analyzer_tool import create_image_analyzer_tool
from .image_gen_tool import create_image_gen_tool
from .image_understanding_tool import create_image_understanding_tool
from .speech_recognition_tool import create_speech_recognition_tool


def get_all_tools(base_dir: Union[Path, str]) -> List[BaseTool]:
    """Create and return all tools, sandboxed to base_dir."""
    base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir
    memory_dir = base_dir / "memory"
    skills_dir = base_dir / "skills"
    return [
        create_terminal_tool(base_dir),
        create_python_repl_tool(),
        create_fetch_url_tool(),
        create_tavily_search_tool(),
        create_read_file_tool(base_dir),
        create_read_skill_tool(skills_dir),
        create_write_memory_tool(memory_dir),
        # 文档解析工具
        create_pdf_parser_tool(base_dir),
        create_word_parser_tool(base_dir),
        # 图像工具（双模型：原 GPT-4V + 新增 Qwen）
        create_image_analyzer_tool(base_dir),
        create_image_gen_tool(base_dir),
        create_image_understanding_tool(base_dir),
        # 语音工具
        create_speech_recognition_tool(base_dir),
    ]