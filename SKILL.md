---
name: fishaudio-tts
description: "Generate speech with Fish Audio (TTS). Use when the user wants text turned into audio, voiceover, narration, audiobook/dialogue lines, podcast or short-video voiceover, an AI voice-agent reply, or wants to pick/reuse one of their curated Fish Audio voices. The skill reads scripts/.env (model, API key, reference_list), exposes the voice catalog with names, descriptions and reference ids, writes emotion/performance markup that the S2 and drama-3 models actually obey, and saves the audio locally. Triggers include: 语音合成, 配音, 生成语音, 文本转语音, TTS, 朗读, 旁白, 有声书, 多说话人对话, 音色, 克隆音色, 情绪配音, fish audio, fishaudio-tts, text to speech, voiceover."
---
# Fish Audio TTS

Turn a script into speech that sounds human, not like a phone menu.

## 铁律

1. 先跑 `voices`们获取音色目录。
2. **情绪用方括号 `[happy]`。**
3. **长文本或含引号的文本，一律走 `--text-file`。** PowerShell 里 `'` 和 `"` 转义极易出错。
4. **交付只报 url + 字节大小。**

## 工作流

### 1. 读音色目录

```powershell
python scripts/fish_core.py voices
```

输出 Markdown 表格：序号 / 名称 / reference_id / 描述。**按描述挑音色，不要猜 id。**
加 `--json` 拿结构化数据。

### 2. 选音色

`--voice` 接受 **名称**、**名称片段**、或 **32 位 id**，大小写不敏感。
多说话人用 `|` 分隔 → 自动变成 `reference_id` 数组：

```powershell
--voice "旁白|船长|工程师"
```

匹配到多个候选时脚本会报错并列出候选，换更精确的名称即可。
不传 `--voice` 时用 `.env` 的 `DEFAULT_VOICE`；都没配就不传 `reference_id`（用模型默认音色）。

### 3. 写表演脚本

决定语音效果的一步：表演指令。

```text
[excited] Hi there! I'm your new voice agent.
[laughing] Ha ha, I promise I'm friendlier than a phone menu.
[whispering] Want to know a secret?
[break] This whole reply came from one API call.
```

必读：`references/performance-tags.md`（49 个情绪 + 6 语气 + 11 音效 + 强度调节 + drama-3 导演语法 + 音素控制）。
参数与排错：`references/tuning.md`。

三条最有效的规则：

- **每句一个主情绪**，最多叠 3 个标签。
- **音效后面补文字**：`[laughing] We won! Ha ha!`
- **情绪要递进、要拉开**，别一句一换。

### 4. 生成

```powershell
python scripts/fish_core.py say --text-file script.txt --voice "旁白" --name ep01
```

返回就三行：`status` / `local_path` / `bytes`（外加 `url`）。拿到后直接报路径和大小，收工。

## 命令速查

```powershell
python scripts/fish_core.py voices [--json]
python scripts/fish_core.py say "<文本>" | --text-file <路径|->  [选项]
python scripts/fish_core.py lint "<文本>" | --text-file <路径|->   # 可选，调试用
```

`say` 常用选项：

| 选项                                 | 作用                                               |
| ------------------------------------ | -------------------------------------------------- |
| `--voice "名\|名2"`                 | 音色名或 id，`\|` 分隔即多说话人                  |
| `--name ep01`                      | 输出文件名（不含扩展名）                           |
| `--model drama-3`                  | 覆盖 `.env` 的 MODEL                             |
| `--preset quality\|balanced\|fast`   | quality=最稳（latency=normal + 192k）；fast=首音快 |
| `--format wav --sample-rate 44100` | 发布级音质                                         |
| `--speed 1.1`                      | 0.5–2.0                                           |
| `--repetition-penalty 1.2`         | 治"卡带式重复发音"                                 |
| `--language zh-CN`                 | 只影响数字/日期读法，不改音色                      |
| `--out-dir D:\out`                 | 覆盖 SAVE_PATH                                     |
| `--share` / `--no-share`         | 生成后是否上传取直链，默认读 `.env` 的 `SHARE` |
| `--dry-run`                        | 只打印最终 payload，不发请求                       |
| `--keep-script`                    | 顺便把脚本存成同名 `.txt`                        |

`lint` 只在脚本听着不对劲、想排查标签写法时用，正常流程不必跑。

## 配置（`scripts/.env`）

| 键                                     | 说明                                                               |
| -------------------------------------- | ------------------------------------------------------------------ |
| `MODEL`                              | `s2.1-pro-free`（免费）/ `s2.1-pro` / `drama-3`              |
| `API_KEY`                            | `sk-...`，在 fish.audio 后台生成                                 |
| `REFERENCE_LIST`                     | `{"<id>": {"name": "...", "description": "..."}}`，支持多行 JSON |
| `DEFAULT_VOICE`                      | 默认音色（name 或 id）                                             |
| `SAVE_PATH`                          | 输出目录，必填                                                     |
| `SHARE`                              | `1` 生成后上传取直链，`0` 只留本地                             |
| `URUSAI_API_TOKEN`                   | 可选，不填也能上传                                                 |
| `PRESET` / `FORMAT` / `LANGUAGE` | 默认档位 / 格式 / 规范化语言（中英混排留空）                       |

也支持 `VOICE_1=id | 名称 | 描述` 的逐行写法，见 `.env.example`。

用户要加音色时：往 `REFERENCE_LIST` 里加一条，`name` 写得像人话，`description` 写"什么场景用它、什么语言、什么性别/年龄感"。AI 就是靠这两项选音色的。

## 已知的坑

- **`model` 头拼错不会报错**，会静默回落到 `s2.1-pro`。
- **`language` 填错不会毁音色**，只会让数字/单位读错，可以不填自动识别。
- 输出目录取 `.env` 的 `SAVE_PATH`，想指定音频目录使用`--out-dir`参数。

## 输出

```json
{"status": "success", "url": "https://i.urusai.cc/aLhq8.mp3", "local_path": "E:\\TMP\\Audio\\ep01.mp3", "bytes": 151091}
```

`url` 是可直接播放和分享的 https 直链（默认上传到 `api.urusai.cc` 免费文件床）。

```html
<audio class="chat-audio-player" controls="" preload="none">
  <source id="Audio Format" src="URL">
</audio>
```

加 `--no-share` 则不上传，`url` 退回 `file:///` 本地 URI，只有本机能用。

上传失败**不会中断生成**：返回里会多一个 `share_error`，此时改用 `local_path`，**不要编造链接**。

失败时把脚本返回的 `message` 原样说明并给出下一步（换音色 / 改标签 / 调参数）。
