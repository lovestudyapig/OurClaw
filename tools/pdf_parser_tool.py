"""PDFParserTool — 解析 PDF 文件内容。"""

from pathlib import Path
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class PDFParserInput(BaseModel):
    file_path: str = Field(
        description="PDF 文件的相对路径，例如: 'docs/report.pdf'"
    )


class PDFParserTool(BaseTool):
    name: str = "parse_pdf"
    description: str = (
        "解析 PDF 文件内容并提取文本。适用于读取 PDF 文档、报告、论文等。 "
        "特点：支持提取文本内容和元数据。"
    )
    args_schema: Type[BaseModel] = PDFParserInput
    root_dir: str = ""

    def _run(self, file_path: str) -> str:
        try:
            from PyPDF2 import PdfReader

            root = Path(self.root_dir)
            normalized = file_path.replace("\\", "/").lstrip("./")
            full_path = (root / normalized).resolve()

            # 沙盒检查
            if not str(full_path).startswith(str(root.resolve())):
                return f"❌ Access denied: path escapes allowed directory"

            if not full_path.exists():
                return f"❌ File not found: {file_path}"

            reader = PdfReader(str(full_path))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            if not text.strip():
                return "⚠️ PDF 中未提取到文本内容（可能是扫描件或加密文档）"

            if len(text) > 15000:
                text = text[:15000] + "\n...[truncated]"

            return text

        except ImportError:
            return "❌ 需要安装 PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"❌ Error parsing PDF: {str(e)}"


def create_pdf_parser_tool(base_dir: Path) -> PDFParserTool:
    tool = PDFParserTool(root_dir=str(base_dir))
    return tool

# create_pdf_parser_tool("Pansharpening_for_Thin-Cloud_Contaminated_Remote_Sensing_Images_AAAI2026.pdf")
# print("wanc hui")