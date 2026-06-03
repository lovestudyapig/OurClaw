"""WordParserTool — 解析 Word 文档内容。"""

from pathlib import Path
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class WordParserInput(BaseModel):
    file_path: str = Field(
        description="Word 文件的相对路径，例如: 'docs/report.docx'"
    )


class WordParserTool(BaseTool):
    name: str = "parse_word"
    description: str = (
        "解析 Word 文档 (.docx) 内容并提取文本。适用于读取报告、文档等。"
    )
    args_schema: Type[BaseModel] = WordParserInput
    root_dir: str = ""

    def _run(self, file_path: str) -> str:
        try:
            from docx import Document

            root = Path(self.root_dir)
            normalized = file_path.replace("\\", "/").lstrip("./")
            full_path = (root / normalized).resolve()

            if not str(full_path).startswith(str(root.resolve())):
                return f"❌ Access denied: path escapes allowed directory"

            if not full_path.exists():
                return f"❌ File not found: {file_path}"

            doc = Document(str(full_path))
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])

            if len(text) > 15000:
                text = text[:15000] + "\n...[truncated]"

            return text

        except ImportError:
            return "❌ 需要安装 python-docx: pip install python-docx"
        except Exception as e:
            return f"❌ Error parsing Word: {str(e)}"


def create_word_parser_tool(base_dir: Path) -> WordParserTool:
    tool = WordParserTool(root_dir=str(base_dir))
    return tool
