"""
Claw 桌面版 (sysapp) — Tkinter 原生应用

与 Web 版相同的三栏布局，直接调用 CoreClawAgent。

启动方式:  python sysapp.py
"""

import asyncio
import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, ttk

# --- 路径设置 ---
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

from Claw import CoreClawAgent


# ==================== 异步事件循环线程 ====================

class AsyncLoopThread(threading.Thread):
    """在后台线程运行 asyncio 事件循环。"""

    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()
        self._agent = None
        self._ready = False

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def get_agent(self):
        if self._agent is None:
            self._agent = CoreClawAgent(base_dir=BASE_DIR)
        return self._agent

    def wait_ready(self):
        while not self._ready:
            time.sleep(0.1)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def submit(self, coro):
        """提交协程到事件循环，返回 Future。"""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


# ==================== 主窗口 ====================

class ClawDesktopApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("🐾 Claw Desktop — 桌面版")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)

        # ===== 清新风格颜色方案 =====
        self.bg_main = "#f0f2f5"          # 主背景 - 暖灰
        self.bg_sidebar = "#ffffff"        # 侧栏 - 纯白
        self.bg_chat = "#f5f7fa"          # 聊天区背景
        self.accent = "#1976d2"           # 主题蓝
        self.accent_light = "#e3f2fd"     # 浅蓝
        self.accent_dark = "#1565c0"      # 深蓝（hover）
        self.text_primary = "#1a2332"     # 主文字 - 深灰
        self.text_secondary = "#5f6b7a"   # 次要文字 - 中灰
        self.text_white = "#ffffff"       # 白色文字
        self.border_color = "#dce0e5"     # 边框色
        self.success = "#43a047"          # 绿色
        self.warning = "#ff9800"          # 橙色
        self.error = "#e53935"            # 红色
        self.code_bg = "#f0f2f5"          # 代码背景

        self.root.configure(bg=self.bg_main)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        # 配置 ttk 组件样式
        self.style.configure("TFrame", background=self.bg_main)
        self.style.configure("TLabel", background=self.bg_main, foreground=self.text_primary)
        self.style.configure("Sidebar.TFrame", background=self.bg_sidebar)
        self.style.configure("Header.TLabel", foreground=self.accent, background=self.bg_sidebar,
                             font=("", 14, "bold"))
        self.style.configure("Status.TLabel", foreground=self.text_secondary, background=self.bg_sidebar,
                             font=("", 10))

        # 状态
        self.work_dir = ""
        self.async_thread = AsyncLoopThread()
        self.async_thread.start()
        time.sleep(0.5)  # 等待事件循环启动

        self._build_ui()

        # 日志导出队列
        self.log_entries = []

        # 启动后初始化 Agent
        self.root.after(100, self._init_agent)

    def _init_agent(self):
        try:
            agent = self.async_thread.get_agent()
            tool_count = len(agent.tools)
            self._update_status(f"就绪 ({tool_count}个工具)")
            self._append_log("system", "系统", "Claw Desktop 已启动")
            self._append_chat("assistant", "👋 欢迎使用 Claw Desktop！\n\n左侧选择工作目录，中间输入问题开始对话。")
        except Exception as e:
            self._update_status(f"错误: {e}")

    def _build_ui(self):
        # 主容器
        main_frame = Frame(self.root, bg=self.bg_main)
        main_frame.pack(fill=BOTH, expand=True)

        # === 左侧：工作目录 ===
        left_frame = Frame(main_frame, bg=self.bg_sidebar, width=260)
        left_frame.pack(side=LEFT, fill=Y)
        left_frame.pack_propagate(False)
        # 右侧分割线
        Frame(left_frame, bg=self.border_color, width=1).pack(side=RIGHT, fill=Y)

        # 标题 + 选择按钮
        header = Frame(left_frame, bg=self.bg_sidebar)
        header.pack(fill=X, padx=14, pady=(14, 10))

        Label(header, text="📁 工作目录", font=("", 14, "bold"),
              fg=self.accent, bg=self.bg_sidebar).pack(anchor=W)

        btn_row = Frame(header, bg=self.bg_sidebar)
        btn_row.pack(fill=X, pady=(8, 0))

        self.select_btn = Button(btn_row, text="📂 选择文件夹",
                                 command=self._select_folder,
                                 bg=self.accent, fg=self.text_primary,
                                 relief=FLAT, cursor="hand2",
                                 font=("", 12), pady=7, padx=14)
        self.select_btn.pack(side=LEFT, fill=X, expand=True)

        self.refresh_btn = Button(btn_row, text="⟳",
                                  command=self._refresh_file_tree,
                                  bg="#f0f2f5", fg=self.text_primary,
                                  relief=FLAT, cursor="hand2",
                                  font=("", 14), pady=5, padx=10)
        self.refresh_btn.pack(side=RIGHT, padx=(4, 0))

        # 文件树
        tree_frame = Frame(left_frame, bg=self.bg_main)
        tree_frame.pack(fill=BOTH, expand=True, padx=8, pady=4)

        self.file_tree = Text(tree_frame, bg=self.bg_sidebar, fg=self.text_primary,
                              font=("", 12), relief=FLAT,
                              state=DISABLED, cursor="hand2",
                              padx=10, pady=8, bd=0,
                              highlightthickness=1, highlightbackground=self.border_color)
        self.file_tree.pack(fill=BOTH, expand=True)

        # 当前路径
        self.path_label = Label(left_frame, text="未选择工作目录",
                                font=("", 11), fg=self.text_secondary, bg=self.bg_sidebar,
                                anchor=W, padx=14, pady=8)
        self.path_label.pack(fill=X, side=BOTTOM)

        # === 中间：聊天区 ===
        center_frame = Frame(main_frame, bg=self.bg_main)
        center_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # 头部
        chat_header = Frame(center_frame, bg=self.bg_sidebar)
        chat_header.pack(fill=X, padx=0, pady=0)
        Label(chat_header, text="🐾 Claw 对话", font=("", 14, "bold"),
              fg=self.accent, bg=self.bg_sidebar).pack(side=LEFT, padx=20, pady=10)
        self.status_label = Label(chat_header, text="启动中...",
                                  font=("", 12), fg=self.text_secondary, bg=self.bg_sidebar)
        self.status_label.pack(side=RIGHT, padx=20, pady=10)

        # === 可拖拽分割面板（上方: 聊天+输入, 下方: 文件预览） ===
        self.paned = ttk.PanedWindow(center_frame, orient=VERTICAL)
        self.paned.pack(fill=BOTH, expand=True)

        # === 上方面板：聊天消息 + 输入区 ===
        top_pane = Frame(self.paned, bg=self.bg_main)
        self.paned.add(top_pane, weight=1)

        # 聊天消息区域
        self.chat_text = scrolledtext.ScrolledText(
            top_pane, bg=self.bg_chat, fg=self.text_primary,
            font=("", 13), relief=FLAT, wrap=WORD,
            padx=20, pady=16, state=DISABLED,
            spacing1=3, spacing2=1, spacing3=12,
            cursor="arrow", bd=0,
        )
        self.chat_text.pack(fill=BOTH, expand=True)
        # 聊天气泡标签
        self.chat_text.tag_config("user", foreground=self.text_white,
                                  background=self.accent, lmargin1=60,
                                  rmargin=20, spacing1=10, spacing2=4, spacing3=10,
                                  font=("", 13))
        self.chat_text.tag_config("assistant", foreground=self.text_primary,
                                  background=self.bg_sidebar, lmargin1=20,
                                  rmargin=60, spacing1=10, spacing2=4, spacing3=10,
                                  font=("", 13))
        self.chat_text.tag_config("system", foreground=self.text_secondary,
                                  background="#eef1f5", lmargin1=20,
                                  rmargin=20, spacing1=8, spacing2=3, spacing3=8,
                                  font=("", 12, "italic"))
        self.chat_text.tag_config("time", foreground="#99a7b9", font=("", 10))

        # 输入区
        self.input_frame = Frame(top_pane, bg=self.bg_sidebar)
        self.input_frame.pack(fill=X, side=BOTTOM)

        input_row = Frame(self.input_frame, bg=self.bg_sidebar)
        input_row.pack(fill=X, padx=20, pady=12)

        self.record_btn = Button(input_row, text="🎤",
                                 command=self._toggle_recording,
                                 bg="#f0f2f5", fg=self.text_primary,
                                 relief=FLAT, cursor="hand2",
                                 font=("", 15), padx=12, pady=8)
        self.record_btn.pack(side=LEFT, padx=(0, 8))

        input_bg = Frame(input_row, bg=self.border_color, bd=0)
        input_bg.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))

        self.input_entry = Text(input_bg, height=2,
                                bg=self.bg_chat, fg=self.text_primary,
                                font=("", 13), relief=FLAT,
                                insertbackground=self.text_primary,
                                padx=14, pady=10, bd=0)
        self.input_entry.pack(fill=BOTH, expand=True)
        self.input_entry.bind("<Return>", self._on_enter_key)
        self.input_entry.bind("<Shift-Return>", lambda e: None)
        # Add placeholder behavior
        self.input_entry.insert("1.0", "输入消息 (Enter 发送, Shift+Enter 换行)")
        self.input_entry.config(fg=self.text_secondary)
        self.input_entry.bind("<FocusIn>", self._on_input_focus)
        self.input_entry.bind("<FocusOut>", self._on_input_blur)

        self.send_btn = Button(input_row, text="发送 ➤",
                               command=self._send_message,
                               bg=self.accent, fg=self.text_primary,
                               relief=FLAT, cursor="hand2",
                               font=("", 13), padx=20, pady=8)
        self.send_btn.pack(side=LEFT)

        # === 下方面板：文件预览（可拖拽调整大小） ===
        self.preview_pane = Frame(self.paned, bg=self.bg_sidebar)

        # 预览标题栏
        preview_header = Frame(self.preview_pane, bg=self.accent)
        preview_header.pack(fill=X)
        self.preview_filename = Label(preview_header, text="",
                                      font=("", 12, "bold"),
                                      fg=self.text_primary, bg=self.accent,
                                      anchor=W, padx=14)
        self.preview_filename.pack(side=LEFT, pady=5)
        close_btn = Button(preview_header, text="✕",
                           command=self._close_file_preview,
                           bg=self.accent, fg=self.text_primary,
                           relief=FLAT, cursor="hand2",
                           font=("", 14, "bold"), padx=12, activebackground="#c62828")
        close_btn.pack(side=RIGHT, pady=2, padx=4)

        # 预览内容（expand=True 使内容随拖拽填满空间）
        self.preview_content = scrolledtext.ScrolledText(
            self.preview_pane, bg=self.bg_sidebar, fg=self.text_primary,
            font=("Consolas", 12), relief=FLAT, wrap=WORD,
            padx=14, pady=8, state=DISABLED, bd=0,
        )
        self.preview_content.pack(fill=BOTH, expand=True)

        # 预览状态（初始隐藏）
        self._preview_visible = False

        # === 右侧：日志面板 ===
        right_frame = Frame(main_frame, bg=self.bg_sidebar, width=300)
        right_frame.pack(side=RIGHT, fill=Y)
        right_frame.pack_propagate(False)
        # 左侧分割线
        Frame(right_frame, bg=self.border_color, width=1).pack(side=LEFT, fill=Y)

        log_header = Frame(right_frame, bg=self.bg_sidebar)
        log_header.pack(fill=X, padx=14, pady=(14, 10))

        Label(log_header, text="📋 执行日志", font=("", 14, "bold"),
              fg=self.accent, bg=self.bg_sidebar).pack(side=LEFT)

        log_actions = Frame(log_header, bg=self.bg_sidebar)
        log_actions.pack(side=RIGHT)

        Button(log_actions, text="清空", command=self._clear_log,
               bg="#f0f2f5", fg=self.text_primary,
               relief=FLAT, cursor="hand2",
               font=("", 11), padx=10, pady=3).pack(side=LEFT, padx=2)
        Button(log_actions, text="导出", command=self._export_log,
               bg=self.accent, fg=self.text_primary,
               relief=FLAT, cursor="hand2",
               font=("", 11), padx=10, pady=3).pack(side=LEFT, padx=2)

        self.log_text = scrolledtext.ScrolledText(
            right_frame, bg=self.bg_sidebar, fg=self.text_primary,
            font=("Consolas", 11), relief=FLAT, wrap=WORD,
            padx=12, pady=8, state=DISABLED, cursor="arrow", bd=0,
        )
        self.log_text.pack(fill=BOTH, expand=True, padx=8, pady=(0, 8))

        # 日志标签颜色
        self.log_text.tag_config("thinking", foreground=self.accent)
        self.log_text.tag_config("tool_call", foreground=self.warning)
        self.log_text.tag_config("tool_result", foreground=self.success)
        self.log_text.tag_config("final", foreground=self.accent, font=("Consolas", 11, "bold"))
        self.log_text.tag_config("error", foreground=self.error, font=("Consolas", 11, "bold"))

        # 文件树标签配置
        self.file_tree.tag_config("folder_collapsed", foreground=self.accent, font=("", 12))
        self.file_tree.tag_config("folder_expanded", foreground=self.accent, font=("", 12))
        self.file_tree.tag_config("file", foreground=self.text_primary, font=("", 11))
        self.file_tree.tag_config("root", foreground=self.accent, font=("", 12, "bold"))
        self.file_tree.tag_config("file_size", foreground=self.text_secondary, font=("", 10))

    # ==================== 辅助方法 ====================

    def _update_status(self, text):
        self.status_label.config(text=text)

    def _append_chat(self, role, content):
        self.chat_text.config(state=NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if role == "user":
            self.chat_text.insert(END, f"你 [{timestamp}]\n", "user")
            self.chat_text.insert(END, f"{content}\n\n", "user")
        elif role == "system":
            self.chat_text.insert(END, f"⚙ [{timestamp}]\n", "system")
            self.chat_text.insert(END, f"{content}\n\n", "system")
        else:
            self.chat_text.insert(END, f"Claw [{timestamp}]\n", "assistant")
            self.chat_text.insert(END, f"{content}\n\n", "assistant")
        self.chat_text.see(END)
        self.chat_text.config(state=DISABLED)

    def _append_log(self, log_type, name, content):
        self.log_text.config(state=NORMAL)
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{log_type.upper()}] {name}: {content[:200]}\n"
        self.log_text.insert(END, line, log_type)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)

        # 同时记录到日志列表（导出用）
        self.log_entries.append({
            "timestamp": ts,
            "type": log_type,
            "name": name,
            "content": content,
        })

    def _clear_log(self):
        self.log_text.config(state=NORMAL)
        self.log_text.delete("1.0", END)
        self.log_text.insert(END, "等待执行任务...\n")
        self.log_text.config(state=DISABLED)
        self.log_entries = []

    # ==================== 输入框占位文本 ====================

    def _on_input_focus(self, event):
        if self.input_entry.get("1.0", END).strip() == "输入消息 (Enter 发送, Shift+Enter 换行)":
            self.input_entry.delete("1.0", END)
            self.input_entry.config(fg=self.text_primary)

    def _on_input_blur(self, event):
        if not self.input_entry.get("1.0", END).strip():
            self.input_entry.delete("1.0", END)
            self.input_entry.insert("1.0", "输入消息 (Enter 发送, Shift+Enter 换行)")
            self.input_entry.config(fg=self.text_secondary)

    # ==================== 文件夹选择与可折叠文件树 ====================

    def _select_folder(self):
        folder = filedialog.askdirectory(title="选择工作文件夹")
        if not folder:
            return
        self.work_dir = folder
        self.path_label.config(text=f"📂 {Path(folder).name}")
        self._append_log("final", "文件系统", f"已选择工作目录: {folder}")

        # 通知 Claw 设置工作目录
        try:
            agent = self.async_thread.get_agent()
            result = agent.set_work_dir(folder)
            self._append_log("final", "工作目录", result)
            self._append_chat("system", f"📂 工作目录已锁定为:\n`{folder}`\n文件操作限制在此目录内。")
        except Exception as e:
            self._append_log("error", "工作目录", str(e))

        # 加载可折叠文件树
        self._build_tree_data(folder)
        self._render_file_tree()

    def _refresh_file_tree(self):
        """刷新文件树"""
        if self.work_dir:
            self._build_tree_data(self.work_dir)
            self._render_file_tree()
            self._append_log("final", "文件系统", "文件树已刷新")

    def _build_tree_data(self, root_path):
        """递归构建文件树数据结构"""
        self._tree_root_path = root_path
        # _tree_data: { "path": str, "name": str, "is_dir": bool, "children": [...], "expanded": bool }
        self._tree_data = self._build_node(Path(root_path), depth=0)
        # 存储可点击项的映射: tag_name -> {"type": "file"/"folder", "path": str, "node": node}
        self._tree_clickable = {}
        self._tree_tag_counter = 0

    def _build_node(self, dir_path: Path, depth: int = 0) -> dict:
        """递归构建目录节点，depth=0 为根节点默认展开，其余默认折叠"""
        try:
            items = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (PermissionError, OSError):
            return None

        children = []
        for item in items[:200]:
            try:
                if item.is_dir():
                    child = self._build_node(item, depth + 1)
                    if child:
                        children.append(child)
                else:
                    size = item.stat().st_size
                    children.append({
                        "path": str(item.resolve()),
                        "name": item.name,
                        "is_dir": False,
                        "size": size,
                    })
            except (PermissionError, OSError):
                continue

        # 目录排前面
        children.sort(key=lambda c: (not c["is_dir"], c["name"].lower()))

        return {
            "path": str(dir_path.resolve()),
            "name": dir_path.name,
            "is_dir": True,
            "expanded": depth == 0,  # 根目录展开，子目录折叠
            "children": children,
        }

    def _render_file_tree(self):
        """根据 tree_data 渲染文件树（含可折叠）"""
        self.file_tree.config(state=NORMAL)
        self.file_tree.delete("1.0", END)
        self._tree_clickable = {}
        self._tree_tag_counter = 0

        # 渲染根节点
        if self._tree_data:
            self._render_tree_node(self._tree_data, 0)

        # 绑定所有可点击项
        for tag_name in list(self._tree_clickable.keys()):
            self.file_tree.tag_bind(tag_name, "<Button-1>",
                                     lambda e, t=tag_name: self._on_tree_item_click(t))

        self.file_tree.config(state=DISABLED)

    def _render_tree_node(self, node: dict, depth: int):
        """递归渲染一个节点及其子节点"""
        if node is None:
            return

        prefix = "  " * depth
        tag_name = f"tree_{self._tree_tag_counter}"
        self._tree_tag_counter += 1

        if node["is_dir"]:
            # 目录 - 可折叠
            if node.get("expanded", False):
                icon = "▼"
                tag = "folder_expanded"
            else:
                icon = "▶"
                tag = "folder_collapsed"

            line = f"{prefix}{icon} 📁 {node['name']}/\n"
            self.file_tree.insert(END, line, (tag, tag_name))

            self._tree_clickable[tag_name] = {
                "type": "folder",
                "node": node,
            }

            # 如果展开，渲染子节点
            if node.get("expanded", False):
                for child in node.get("children", []):
                    self._render_tree_node(child, depth + 1)
        else:
            # 文件 - 可点击预览
            sz = node.get("size", 0)
            sz_str = f"({sz//1024}KB)" if sz > 1024 else f"({sz}B)"
            line = f"{prefix}📄 {node['name']} {sz_str}\n"
            self.file_tree.insert(END, line, ("file", tag_name))

            self._tree_clickable[tag_name] = {
                "type": "file",
                "path": node["path"],
                "name": node["name"],
            }

    def _on_tree_item_click(self, tag_name):
        """文件树中的项被点击"""
        info = self._tree_clickable.get(tag_name)
        if not info:
            return

        if info["type"] == "folder":
            # 切换展开/折叠
            node = info["node"]
            node["expanded"] = not node.get("expanded", False)
            self._render_file_tree()
        elif info["type"] == "file":
            # 预览文件
            self._preview_file(info["path"], info["name"])

    def _preview_file(self, full_path, display_name):
        """读取并显示文件预览"""
        self._append_log("tool_call", "文件预览", f"读取: {display_name}")
        self.preview_filename.config(text=f"📄 {display_name}")
        self.preview_content.config(state=NORMAL)
        self.preview_content.delete("1.0", END)
        self.preview_content.insert(END, "⏳ 加载中...\n")
        self.preview_content.config(state=DISABLED)

        # 首次显示时加入 PanedWindow 下方面板，初始高度 250px
        if not self._preview_visible:
            self.paned.add(self.preview_pane, weight=0)
            self.root.update_idletasks()
            # 设置 sash 位置：总高度 - 300px（预览区高度）
            total_h = self.paned.winfo_height()
            try:
                self.paned.sashpos(0, max(total_h - 300, 150))
            except Exception:
                pass
            self._preview_visible = True

        self.root.update()

        try:
            content, size, truncated = self._read_file_content(full_path)
            self.preview_content.config(state=NORMAL)
            self.preview_content.delete("1.0", END)
            if truncated:
                self.preview_content.insert(END, f"⚠️ 文件过大 ({size//1024}KB)，仅显示前 2000 字符。\n\n")
            self.preview_content.insert(END, content)
            self.preview_content.config(state=DISABLED)
            self._append_log("final", "文件预览", f"已加载 {(size/1024):.1f}KB")
        except Exception as e:
            self.preview_content.config(state=NORMAL)
            self.preview_content.delete("1.0", END)
            self.preview_content.insert(END, f"❌ 读取失败: {e}")
            self.preview_content.config(state=DISABLED)
            self._append_log("error", "文件预览", str(e))

    def _close_file_preview(self):
        """关闭文件预览面板"""
        try:
            self.paned.forget(self.preview_pane)
        except Exception:
            pass
        self._preview_visible = False

    def _read_file_content(self, full_path: str) -> tuple:
        """读取文件内容，自动检测编码"""
        target = Path(full_path)
        if not target.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")
        if not target.is_file():
            raise ValueError(f"不是文件: {full_path}")

        size = target.stat().st_size
        raw = target.read_bytes()

        # 自动检测编码
        text = ""
        for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            text = raw.decode("utf-8", errors="replace")

        # 截断过大的文件
        truncated = False
        if len(text) > 2000:
            text = text[:2000]
            truncated = True

        return text, size, truncated

    # ==================== 消息发送 ====================

    def _on_enter_key(self, event):
        if not event.state & 0x1:  # 没有按 Shift
            self._send_message()
            return "break"

    def _send_message(self):
        text = self.input_entry.get("1.0", END).strip()
        if not text or text == "输入消息 (Enter 发送, Shift+Enter 换行)":
            return

        self.input_entry.delete("1.0", END)
        self.input_entry.config(fg=self.text_primary)
        self._append_chat("user", text)
        self._update_status("处理中...")
        self.send_btn.config(state=DISABLED)
        self.record_btn.config(state=DISABLED)

        # 加载消息 ID 占位
        loading_id = self._append_chat_loading()

        def on_done(future):
            try:
                events = future.result()
                self.root.after(0, self._process_events, events, loading_id)
            except Exception as e:
                self.root.after(0, self._update_chat_loading, loading_id, f"❌ 错误: {e}")
            finally:
                self.root.after(0, self._enable_input)

        # 收集所有事件
        all_events = []
        async def collect_events():
            async for event in self.async_thread.get_agent().stream_chat_with_events(text):
                all_events.append(event)
            return all_events

        future = self.async_thread.submit(collect_events())
        future.add_done_callback(on_done)

    def _append_chat_loading(self):
        self.chat_text.config(state=NORMAL)
        tag = f"loading_{datetime.now().timestamp()}"
        self.chat_text.tag_config(tag, foreground=self.accent)
        self.chat_text.insert(END, f"Claw [{datetime.now().strftime('%H:%M:%S')}]\n", "assistant")
        idx = self.chat_text.index(END)
        self.chat_text.insert(END, "⏳ 思考中...\n\n", tag)
        self.chat_text.see(END)
        self.chat_text.config(state=DISABLED)
        return tag

    def _update_chat_loading(self, tag, content):
        self.chat_text.config(state=NORMAL)
        # 查找并替换
        start = self.chat_text.search("⏳", "1.0", END)
        if start:
            line_end = self.chat_text.index(f"{start} lineend")
            self.chat_text.delete(start, line_end)
            self.chat_text.insert(start, content, "assistant")
        self.chat_text.see(END)
        self.chat_text.config(state=DISABLED)

    def _process_events(self, events, loading_id):
        final_content = ""
        for event in events:
            if event.get("type") == "thinking":
                self._update_chat_loading(loading_id, event.get("content", "") or "思考中...")
            elif event.get("type") == "tool_call":
                args_str = json.dumps(event.get("args", {}), ensure_ascii=False)[:100]
                self._append_log("tool_call", f"调用: {event.get('name', '')}", args_str)
            elif event.get("type") == "tool_result":
                self._append_log("tool_result", f"结果: {event.get('name', '')}",
                                 (event.get("content", "") or "")[:200])
            elif event.get("type") == "final":
                final_content = event.get("content", "")
            elif event.get("type") == "error":
                self._update_chat_loading(loading_id, "❌ " + event.get("content", ""))
                self._append_log("error", "错误", event.get("content", ""))

        if final_content:
            self._update_chat_loading(loading_id, final_content)

    def _enable_input(self):
        self.send_btn.config(state=NORMAL)
        self.record_btn.config(state=NORMAL)
        self._update_status("就绪")
        self.input_entry.focus()

    # ==================== 录音（桌面版暂时仅浏览器支持，此处预留） ====================

    def _toggle_recording(self):
        messagebox.showinfo("录音", "桌面版录音功能需要浏览器 Web API 支持。\n请使用 Web 版进行语音输入。\n(python app.py → http://127.0.0.1:8000)")

    # ==================== 日志导出 ====================

    def _export_log(self):
        if not self.work_dir:
            if not messagebox.askyesno("导出日志", "未选择工作目录，导出到项目根目录？"):
                return

        try:
            agent = self.async_thread.get_agent()
            log_path = agent.export_log(self.work_dir if self.work_dir else None)
            messagebox.showinfo("导出成功", f"日志已导出到:\n{log_path}")
            self._append_log("final", "日志导出", f"已保存到: {log_path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    # ==================== 运行 ====================

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.input_entry.focus()
        self.root.mainloop()

    def _on_close(self):
        try:
            agent = self.async_thread.get_agent()
            agent.close()
        except Exception:
            pass
        self.async_thread.stop()
        self.root.destroy()


if __name__ == "__main__":
    app = ClawDesktopApp()
    app.run()
