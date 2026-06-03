"""示例定时任务 — 每30秒执行一次。

任务文件格式：
- name: 任务名称（显示用）
- interval: 执行间隔（秒）
- description: 任务描述
- run(): 任务执行函数（可以是 async 或普通函数）
"""

import asyncio
from datetime import datetime

# 任务元数据
name = "示例任务"
interval = 30  # 每30秒执行
description = "打印当前时间，演示定时任务功能"


async def run():
    """任务执行函数。"""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[任务:示例] 当前时间 {now} - 这是一个示例定时任务")
