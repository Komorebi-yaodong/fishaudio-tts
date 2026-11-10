# Fish Audio TTS CLI

一个基于 [Fish Audio](https://fish.audio/) TTS API 的命令行助手：读取本地音色目录，检查带情绪标签的脚本，生成语音并保存到指定目录；也可选择上传生成结果以获得分享链接。

> **安全提示：** `scripts/.env` 通常包含 API Key、私有音色 ID、输出路径和可选上传令牌。该文件已由 `.gitignore` 排除，**不要提交到 GitHub**。请仅提交 `scripts/.env.example`。

## 功能

- 从 `.env` 读取 Fish Audio 配置和自定义音色目录。
- 通过音色名称、名称片段或 32 位 `reference_id` 选择音色。
- 支持多说话人音色数组和 `<|speaker:N|>` 标记。
- 支持 `[happy]`、`[whispering]`、`[laughing]` 等情绪、语气和音效标签。
- `lint` 命令在发起请求前检查常见脚本问题，不消耗 API 额度。
- 支持 `mp3`、`wav`、`opus`、`pcm` 输出，支持速率、语言、延迟和重复惩罚等参数。
- 可选上传到 `api.urusai.cc` 获取可分享的直链；上传失败不会影响本地音频生成。

## 环境要求

- Python 3.9+
- Fish Audio API Key
- Python 依赖：[`requests`](https://pypi.org/project/requests/)

## 安装与配置

```powershell
cd E:\Programming\fishaudio-tts

# 建议使用虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
python -m pip install requests

# 从示例配置创建本地配置
Copy-Item scripts\.env.example scripts\.env
```

然后编辑 `scripts/.env`：

```dotenv
MODEL=s2.1-pro-free
API_KEY=sk-your-real-key
SAVE_PATH=E:\TMP\Audio
SHARE=0
```

完整的配置项、音色列表示例和说明请见 [`scripts/.env.example`](scripts/.env.example)。

### 配置项概览

| 配置项                   | 说明                                                        |
| ------------------------ | ----------------------------------------------------------- |
| `MODEL`                | 模型名，例如 `s2.1-pro-free`、`s2.1-pro` 或 `drama-3` |
| `API_KEY`              | Fish Audio API Key（敏感信息，禁止提交）                    |
| `REFERENCE_LIST`       | JSON 格式的音色目录：ID、名称、描述和标签                   |
| `VOICE_1`、`VOICE_2` | `REFERENCE_LIST` 的可选替代写法：`id                      |
| `DEFAULT_VOICE`        | 默认音色名称或 reference ID                                 |
| `SAVE_PATH`            | 生成音频的本地输出目录                                      |
| `PRESET`               | `quality`、`balanced` 或 `fast`                       |
| `FORMAT`               | `mp3`、`wav`、`opus` 或 `pcm`                       |
| `LANGUAGE`             | 可选 BCP-47 语言标签，例如 `zh-CN`                        |
| `SHARE`                | `1` 上传后返回分享链接；`0` 仅保存本地                  |
| `URUSAI_API_TOKEN`     | 可选的上传服务令牌（敏感信息，禁止提交）                    |

## 快速开始

### 1. 查看音色目录

```powershell
python scripts\fish_core.py voices

# 获取 JSON 结果
python scripts\fish_core.py voices --json
```

请按返回的音色描述选择 `--voice`，不要猜测音色 ID。

### 2. 检查脚本（可选，不请求 API）

```powershell
python scripts\fish_core.py lint "[happy] 你好，欢迎使用 Fish Audio。"
```

### 3. 合成语音

```powershell
# 短文本
python scripts\fish_core.py say "[excited] 你好，欢迎来到今天的节目。" --voice "旁白" --name intro

# 长文本、引号较多或多行文本时，建议使用文本文件
python scripts\fish_core.py say --text-file script.txt --voice "旁白" --name episode-01
```

成功后，命令会返回 JSON，其中包括本地保存路径、文件大小和 URL：

```json
{
  "status": "success",
  "url": "file:///E:/TMP/Audio/intro.mp3",
  "local_path": "E:\\TMP\\Audio\\intro.mp3",
  "bytes": 151091
}
```

如果启用了分享且上传成功，`url` 将是 HTTPS 分享链接；若上传失败，结果会携带 `share_error`，本地文件仍然可用。

## 常用命令

```powershell
# 查看帮助
python scripts\fish_core.py --help
python scripts\fish_core.py say --help

# 指定模型、预设和输出格式
python scripts\fish_core.py say --text-file script.txt --voice "旁白" `
  --model drama-3 --preset quality --format wav --sample-rate 44100

# 调整语速与重复惩罚
python scripts\fish_core.py say "[calm] 请稍候。" --voice "旁白" `
  --speed 1.1 --repetition-penalty 1.2

# 指定输出目录，不改 .env
python scripts\fish_core.py say --text-file script.txt --out-dir E:\Output\Audio

# 只预览最终请求体，不实际调用 API
python scripts\fish_core.py say --text-file script.txt --voice "旁白" --dry-run

# 生成时保存同名文本脚本
python scripts\fish_core.py say --text-file script.txt --name episode-01 --keep-script

# 覆盖 .env 的分享选项
python scripts\fish_core.py say "你好" --no-share
python scripts\fish_core.py say "你好" --share
```

## 情绪与多说话人

### 情绪标签

使用方括号标签，并尽量让每句只有一个主情绪：

```text
[excited] Hi there! I'm your new voice agent.
[laughing] Ha ha, I promise I'm friendlier than a phone menu.
[whispering] Want to know a secret?
[break] This whole reply came from one API call.
```

常见建议：

- 使用 `[happy]`，每句最多叠加 3 个标签，避免冲突情绪同时出现。
- 音效标签后补充实际台词，例如：`[laughing] 我们成功了，哈哈！`。
- 更完整的标签、强度和 `drama-3` 用法见 [references/performance-tags.md](references/performance-tags.md)。

### 多说话人

传入多个音色后，以 `<|speaker:N|>` 标记各段说话人，编号从 0 开始：

```text
<|speaker:0|>[calm] 欢迎登船。
<|speaker:1|>[excited] 收到，船长！
```

```powershell
python scripts\fish_core.py say --text-file dialogue.txt --voice "船长|工程师" --name dialogue
```

## 目录结构

```text
.
├─ scripts/
│  ├─ fish_core.py          # CLI 主程序
│  ├─ .env.example          # 可提交的配置模板
│  └─ .env                  # 本地私密配置（不提交）
├─ references/
│  ├─ performance-tags.md   # 情绪、语气与音效标签指南
│  └─ tuning.md             # 参数调优和故障排查
└─ SKILL.md                 # 面向 Agent 的使用说明
```

## 安全与发布前检查

提交前建议运行：

```powershell
# 检查即将提交的文件；确保没有 scripts/.env、音频或私密脚本
Get-ChildItem -Force

git status
git diff --cached
```

请特别确认以下内容没有进入 Git 历史：

- Fish Audio API Key 与任何其他 Token
- 私有音色 `reference_id` 或带身份信息的音色描述
- 生成的音频、配音文本、日志和临时输出
- 上传服务返回的删除链接（`delete_url`）

如果曾经误提交密钥，应立即在服务后台撤销/轮换密钥，并按 GitHub 官方文档清理历史记录。

## 故障排查

- **`缺少依赖 requests`**：执行 `python -m pip install requests`。
- **找不到 `.env`**：从 `.env.example` 复制一份为 `scripts/.env`，再填写必要配置。
- **401**：检查或轮换 `API_KEY`。
- **402**：模型可能需要额度；可尝试 `MODEL=s2.1-pro-free`。
- **400**：检查音色 ID、语言标签与参数范围；先用 `--dry-run` 查看请求体。
- **上传失败**：不影响本地文件生成，请使用返回的 `local_path`；或通过 `--no-share` 关闭上传。

更多参数说明请阅读 [references/tuning.md](references/tuning.md)。

## License

本项目采用 [MIT License](LICENSE) 开源。

Copyright (c) 2026 Komorebi-yaodong

> MIT 许可证仅适用于本仓库中的代码与文档，不授予 Fish Audio API、第三方音色、生成音频或第三方上传服务相关内容的额外权利。使用这些服务与素材时，请遵守其各自的服务条款和授权要求。
