"""自动保存记忆任务 — 每60秒检查并保存未持久化的记忆。

任务文件格式：
- name: 任务名称
- interval: 执行间隔（秒）
- description: 任务描述
- run(): 任务执行函数
"""

import asyncio
from datetime import datetime
from pathlib import Path

# 任务元数据
name = "自动保存记忆"
interval = 60  # 每60秒执行
description = "自动将缓冲区中的记忆写入磁盘"


async def run():
    """任务执行函数。"""
    # 这里可以添加实际的记忆保存逻辑
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[任务:记忆保存] {now} - 检查并保存记忆缓冲区")
