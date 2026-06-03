name: create_skill
description: 根据用户需求创建新的技能定义文件，或从GitHub仓库导入外部skill项目并整合到本地

# 创建技能 (create_skill)

## 使用场景
当用户提出需要创建一个新的技能（skill）时，使用此技能。例如：
- "帮我创建一个发送邮件的技能"
- "我需要一个数据分析的技能"
- "请创建一个技能来处理图片"
- "帮我导入这个GitHub上的skill项目：https://github.com/xxx/xxx"

## 执行步骤

### 场景A：根据用户需求创建新技能

#### Step 1：分析用户需求
仔细阅读用户的请求，理解用户想要创建的技能的核心功能和用途。

#### Step 2：提取关键信息
从用户描述中提取以下信息：
- 技能名称（name）：简短且描述性的名称
- 技能描述（description）：一句话概括技能的功能
- 使用场景：明确技能适用的具体场景
- 执行步骤：技能需要执行的具体操作步骤
- 输入输出：技能需要的输入参数和预期输出

#### Step 3：生成 SKILL.md 内容
按照标准格式生成完整的技能定义内容。

#### Step 4：保存SKILL.md文件到对应文件夹
建立skills/[技能名称]文件夹，将SKILL.md文件保存到该文件夹中

### 场景B：从GitHub导入外部skill项目

#### Step 1：分析用户提供的GitHub地址
1. 从用户输入中提取GitHub仓库URL
2. 确认URL格式正确（https://github.com/...）
3. 确定目标存放路径：skills/[技能名称]/

#### Step 2：Clone仓库到本地临时目录
1. 创建临时目录：mkdir -p /tmp/skill_import_temp
2. 执行 git clone <仓库URL> /tmp/skill_import_temp/<repo_name>
3. 如果clone失败，向用户报告错误并终止

#### Step 3：扫描并阅读该skill项目的内容
1. 使用 find / ls 命令列出仓库的完整目录结构
2. 必须读取以下核心文件：
   - SKILL.md — 技能定义文件（核心）
   - tools/ 目录下的所有脚本/工具文件
   - prompts/ 目录下的所有提示文件（如有）
   - 其他配置文件（如 requirements.txt、package.json 等）
3. 分析该skill所使用的工具类型：
   - 是否为现有Agent工具（terminal、python_repl、fetch_url、tavily_search、read_file等）能直接实现的？
   - 是否包含自定义脚本（Python/Shell/Node.js等）？
   - 是否包含文档/模版类文件（prompts、模版等）？

#### Step 4：总结分析
输出分析报告，包含：
- 技能名称与描述、目录结构、工具清单、执行步骤、依赖项、整合建议

#### Step 5：整合到本地skills目录
根据分析结果按以下规则整合：

**规则A：仅使用现有Agent工具**
- 直接提取SKILL.md，适配成本地格式
- 创建 skills/[技能名称]/SKILL.md

**规则B：包含自定义脚本/工具**
- 参考 skills/patent_disclosure/ 的目录结构
- 创建 skills/[技能名称]/ 含 SKILL.md + tools/ + prompts/ + requirements.txt

**规则C：包含文档/模版类文件**
- 创建 skills/[技能名称]/ 含 SKILL.md + templates/ + prompts/

#### Step 6：清理临时文件
删除临时clone目录：rm -rf /tmp/skill_import_temp/<repo_name>

#### Step 7：输出整合报告
包含整合后的本地路径、目录结构、差异说明、使用方式

## 注意事项

- Clone前先检查本地是否已存在同名技能目录，存在则询问是否覆盖
- 对于大型仓库，只关注与skill相关的核心文件（SKILL.md、tools/、prompts/等）
- 如果GitHub项目结构不规范（没有SKILL.md），则尝试从README.md或其他文档中提取技能定义
- 整合时保持原项目的许可证和版权声明
