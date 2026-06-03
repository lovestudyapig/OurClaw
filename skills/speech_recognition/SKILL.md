name: speech_recognition
description: 语音识别技能，使用 Qwen 多模态模型将语音文件转换为文字，支持多种音频格式（WAV、MP3、M4A、AAC、FLAC、OGG、AMR等）

# 语音识别技能 (speech_recognition)

## 使用场景

当用户需要将语音/音频文件转换为文字时使用此技能。例如：
- "帮我识别这段语音说了什么"
- "把这个mp3文件转成文字"
- "语音识别一下这个文件"
- "帮我听一下这个录音"

## 识别通道（降级策略）

| 优先级 | 通道 | 方式 | 状态 |
|--------|------|------|------|
| 🥇 主通道 | qwen3.5-omni-flash 多模态 | DashScope MultiModalConversation | ✅ 已验证 |
| 🥈 备选1 | qwen3-asr-flash | OpenAI 兼容接口 /v1/audio/transcriptions | ⚠️ 待端点上架 |
| 🥉 备选2 | qwen3-asr-flash | DashScope 原生 Transcription API | ⚠️ 待适配 |

## 支持格式

WAV、MP3、M4A、AAC、FLAC、OGG、AMR 等常见音频格式。

## 执行步骤

### Step 1：获取音频文件路径
确认用户提供的音频文件路径（相对或绝对路径）。

### Step 2：自动识别
调用 `recognize_speech` 工具，传入 `audio_path` 参数。
工具内部自动走三通道降级策略。

### Step 3：返回结果
将识别后的文字内容返回给用户。

## 输入输出

### 输入
- **audio_path**（必需）：音频文件路径
- **language**（可选，默认 auto）：语言类型（zh/en/ja/auto）

### 输出
- 语音识别后的文字内容

## 示例

用户：帮我识别这个语音文件 "Audio/meeting.wav"
助手：调用 recognize_speech 工具 → 返回识别文字

用户：识别这个英文音频 "audio/speech.mp3"
助手：调用 recognize_speech(audio_path="audio/speech.mp3") → 返回识别文字
