"""Fish Audio TTS helper.

Reads scripts/.env. Never prints the API key.
Subcommands: voices | say | lint
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
TTS_URL = "https://api.fish.audio/v1/tts"
UPLOAD_URL = "https://api.urusai.cc/v1/upload"
UPLOAD_MIME = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "opus": "audio/opus",
    "pcm": "application/octet-stream",
}
DEFAULT_MODEL = "s2.1-pro-free"
REQUEST_TIMEOUT = 300
UPLOAD_TIMEOUT = 120
ID_RE = re.compile(r"^[0-9a-fA-F]{32}$")

PRESETS = {
    "quality": {"latency": "normal", "chunk_length": 200, "mp3_bitrate": 192},
    "balanced": {"latency": "balanced", "chunk_length": 200, "mp3_bitrate": 128},
    "fast": {"latency": "balanced", "chunk_length": 150, "mp3_bitrate": 128},
}

BASIC_EMOTIONS = {
    "happy", "sad", "angry", "excited", "calm", "nervous", "confident", "surprised",
    "satisfied", "delighted", "scared", "worried", "upset", "frustrated", "depressed",
    "empathetic", "embarrassed", "disgusted", "moved", "proud", "relaxed", "grateful",
    "curious", "sarcastic",
}
ADVANCED_EMOTIONS = {
    "disdainful", "unhappy", "anxious", "hysterical", "indifferent", "uncertain",
    "doubtful", "confused", "disappointed", "regretful", "guilty", "ashamed", "jealous",
    "envious", "hopeful", "optimistic", "pessimistic", "nostalgic", "lonely", "bored",
    "contemptuous", "sympathetic", "compassionate", "determined", "resigned",
}
TONES = {"in a hurry tone", "shouting", "screaming", "whispering", "soft tone", "emphasis"}
EFFECTS = {
    "laughing", "chuckling", "sobbing", "crying loudly", "sighing", "groaning",
    "panting", "gasping", "yawning", "snoring", "clear throat",
}
SPECIAL = {"audience laughing", "background laughter", "crowd laughing", "break", "long-break"}
KNOWN_TAGS = BASIC_EMOTIONS | ADVANCED_EMOTIONS | TONES | EFFECTS | SPECIAL

CONFLICT_PAIRS = [
    ("happy", "sad"), ("happy", "angry"), ("calm", "excited"), ("calm", "angry"),
    ("relaxed", "anxious"), ("relaxed", "nervous"), ("confident", "nervous"),
    ("delighted", "depressed"), ("satisfied", "frustrated"), ("hopeful", "pessimistic"),
    ("indifferent", "excited"), ("proud", "ashamed"),
]

DRAMA_PAIRED_TAGS = {"whisper", "emphasis", "soft", "fast", "slow", "stress", "forceful"}


# ---------------------------------------------------------------- env parsing

def _depth(text):
    """Brace/bracket depth outside of JSON strings."""
    depth = 0
    in_str = False
    esc = False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
    return depth


def _unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_env(path=ENV_PATH):
    """Parse .env, supporting multi-line JSON values."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"未找到配置文件: {path}\n请从 scripts/.env.example 复制一份并填写 API_KEY / MODEL / REFERENCE_LIST。"
        )
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    data = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value[:1] in "{[" and _depth(value) > 0:
            buffer = [value]
            while index < len(lines) and _depth("\n".join(buffer)) > 0:
                buffer.append(lines[index])
                index += 1
            value = "\n".join(buffer).strip()
        else:
            value = _unquote(value)
        data[key] = value
    return data


def env_get(env, *keys):
    for key in keys:
        value = env.get(key)
        if value:
            return value.strip()
    return ""


def _voice_sort_key(key):
    digits = re.findall(r"\d+", key)
    return (int(digits[0]) if digits else 10**9, key)


def parse_reference_list(env):
    """Return [{id, name, description, tags}].

    Accepts either REFERENCE_LIST as a JSON dict {id: {name, description}},
    or repeated VOICE_N=id | name | description lines.
    """
    raw = env_get(env, "REFERENCE_LIST", "FISH_REFERENCE_LIST")
    voices = []
    if raw:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"REFERENCE_LIST 不是合法 JSON（注意引号与逗号）: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError('REFERENCE_LIST 必须是字典: {"<reference_id>": {"name": "...", "description": "..."}}')
        for voice_id, meta in obj.items():
            voice_id = str(voice_id).strip()
            if isinstance(meta, str):
                voices.append({"id": voice_id, "name": meta.strip() or voice_id, "description": "", "tags": []})
            elif isinstance(meta, dict):
                voices.append({
                    "id": voice_id,
                    "name": str(meta.get("name") or voice_id).strip(),
                    "description": str(meta.get("description") or "").strip(),
                    "tags": list(meta.get("tags") or []),
                })
            else:
                raise ValueError(f'音色 "{voice_id}" 的值必须是对象或字符串')
        return voices

    for key in sorted((k for k in env if k.upper().startswith("VOICE_")), key=_voice_sort_key):
        parts = [part.strip() for part in env[key].split("|")]
        voice_id = parts[0] if parts else ""
        if not voice_id:
            continue
        voices.append({
            "id": voice_id,
            "name": parts[1] if len(parts) > 1 and parts[1] else voice_id,
            "description": parts[2] if len(parts) > 2 else "",
            "tags": [t.strip() for t in parts[3].split(",")] if len(parts) > 3 and parts[3] else [],
        })
    return voices


def mask_key(key):
    return "已配置" if key else "未配置"


# ---------------------------------------------------------------- voice resolve

def resolve_voices(spec, voices):
    """Resolve '名称|名称2' or ids into a list of reference ids."""
    if not spec or not spec.strip():
        return []
    tokens = [t.strip() for t in re.split(r"[|,]", spec) if t.strip()]
    return [_resolve_one(token, voices) for token in tokens]


def _resolve_one(token, voices):
    if ID_RE.match(token):
        return token
    if not voices:
        raise ValueError(
            "REFERENCE_LIST 为空，无法按名称选音色。请先在 scripts/.env 里配置音色，"
            "或直接传 32 位 reference_id。"
        )
    lowered = token.lower()
    for voice in voices:
        if voice["id"].lower() == lowered:
            return voice["id"]
    exact = [v for v in voices if v["name"] == token]
    if len(exact) == 1:
        return exact[0]["id"]
    fuzzy = [v for v in voices if lowered in v["name"].lower() or lowered in v["description"].lower()]
    if len(fuzzy) == 1:
        return fuzzy[0]["id"]
    if len(fuzzy) > 1:
        candidates = "; ".join(f'{v["name"]} ({v["id"]})' for v in fuzzy)
        raise ValueError(f'音色 "{token}" 匹配到多个候选，请写得更精确: {candidates}')
    available = "; ".join(v["name"] for v in voices)
    raise ValueError(f'找不到音色 "{token}"。当前可用: {available}')


# ---------------------------------------------------------------- lint

def lint_text(text, model, voice_count):
    issues = []

    def add(level, message, fix=""):
        issues.append({"level": level, "issue": message, "fix": fix})

    if not text or not text.strip():
        add("error", "文本为空", "提供要合成的文本")
        return issues

    paren_tags = re.findall(r"\(([^()\n]{1,40})\)", text)
    bracket_tags = re.findall(r"\[([^\[\]\n]{1,120})\]", text)

    if paren_tags:
        add("error", f"检测到圆括号标签 {paren_tags[:3]}", "改成方括号 [happy]；API 不会自动转换")

    for sentence in re.split(r"[。！？!?\.\n]+", text):
        tags = [t.strip().lower() for t in re.findall(r"\[([^\[\]\n]{1,120})\]", sentence)]
        if len(tags) > 3:
            add("warn", f"同一句里叠了 {len(tags)} 个标签: {tags[:5]}",
                "官方建议每句最多 3 个；拆句或删减")
        lowered = " ".join(tags)
        for left, right in CONFLICT_PAIRS:
            if left in tags and right in tags:
                add("warn", f"同一句出现冲突情绪 [{left}] + [{right}]", "每句只保留一个主情绪")

    for tag in bracket_tags:
        stripped = tag.strip()
        lowered = stripped.lower()
        if len(stripped) > 40:
            add("info", f"标签描述过长（{len(stripped)} 字符）: {stripped[:30]}…", "压到 20 字符以内，避免打断可读性")
        if " " not in stripped and lowered not in KNOWN_TAGS:
            add("info", f"非常见单字标签 [{stripped}]",
                "自由描述是允许的；但如果本想用标准标签，检查拼写（如 excitd → excited）")

    paired = re.findall(r"<\s*(%s)\s*>" % "|".join(sorted(DRAMA_PAIRED_TAGS)), text, flags=re.I)
    if paired:
        add("warn", f"检测到 <{paired[0]}> 逐词标签，当前模型不支持，会被念出来", "改用 [方括号] 句子级标签")

    speaker_ids = [int(n) for n in re.findall(r"<\|speaker:(\d+)\|>", text)]
    if speaker_ids:
        if voice_count < 2:
            add("warn", f"文本里有说话人标记，但只解析到 {voice_count} 个音色",
                "用 --voice \"旁白|角色A|角色B\" 传数组")
        highest = max(speaker_ids)
        if highest >= voice_count:
            add("error", f"用了 <|speaker:{highest}|>，但只传了 {voice_count} 个音色",
                "说话人编号从 0 开始，必须小于音色数量")
    elif voice_count > 1:
        add("warn", f"传了 {voice_count} 个音色但没有 <|speaker:N|> 标记", "在每段开头加 <|speaker:0|> / <|speaker:1|>")

    if len(text) > 2000 and not re.search(r"[。！？!?\.\n]", text):
        add("info", "长文本没有任何句读", "补上标点，模型靠它切分停顿")

    return issues


# ---------------------------------------------------------------- payload

def read_text(args):
    if args.text_file:
        if args.text_file == "-":
            return sys.stdin.read()
        path = Path(args.text_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"文本文件不存在: {path}")
        return path.read_text(encoding="utf-8-sig")
    if args.text:
        return args.text
    raise ValueError("缺少文本：传位置参数 text，或用 --text-file <路径|->")


def build_payload(args, env, voices):
    text = read_text(args)
    model = (args.model or env_get(env, "MODEL") or DEFAULT_MODEL).strip()

    voice_spec = args.voice if args.voice is not None else env_get(env, "DEFAULT_VOICE")
    voice_ids = resolve_voices(voice_spec, voices)

    fmt = (args.format or env_get(env, "FORMAT") or "mp3").strip().lower()
    if fmt not in {"mp3", "wav", "pcm", "opus"}:
        raise ValueError("format 只能是 mp3 / wav / pcm / opus")

    preset_name = (args.preset or env_get(env, "PRESET") or "quality").strip().lower()
    preset = PRESETS.get(preset_name)
    if preset is None:
        raise ValueError(f"preset 只能是 {' / '.join(PRESETS)}")
    if args.latency:
        preset = dict(preset, latency=args.latency)

    payload = {"text": text, "format": fmt}
    if voice_ids:
        payload["reference_id"] = voice_ids[0] if len(voice_ids) == 1 else voice_ids
    payload["latency"] = preset["latency"]
    payload["chunk_length"] = args.chunk_length or preset["chunk_length"]

    if fmt == "mp3":
        payload["mp3_bitrate"] = args.mp3_bitrate or preset["mp3_bitrate"]
    if fmt == "wav":
        payload["sample_rate"] = int(args.sample_rate or env_get(env, "SAMPLE_RATE") or 44100)

    speed = args.speed if args.speed is not None else None
    if speed is not None:
        if not 0.5 <= speed <= 2.0:
            raise ValueError("speed 必须在 0.5 到 2.0 之间")
        payload["prosody"] = {"speed": speed}

    language = args.language or env_get(env, "LANGUAGE")
    if language:
        payload["language"] = language
    if args.no_normalize:
        payload["normalize"] = False
    if args.repetition_penalty is not None:
        payload["repetition_penalty"] = args.repetition_penalty

    meta = {
        "model": model,
        "preset": preset_name,
        "format": fmt,
        "voice_count": len(voice_ids),
        "voice_ids": voice_ids,
        "voice_names": [next((v["name"] for v in voices if v["id"] == vid), vid) for vid in voice_ids],
    }
    return payload, meta


def upload_audio(path, fmt, token=""):
    """Upload to the urusai.cc free file host; return {url, delete_url}."""
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")
    mime = UPLOAD_MIME.get(fmt, "application/octet-stream")
    data = {"r18": "0"}
    if token:
        data["token"] = token
    try:
        with open(path, "rb") as handle:
            response = requests.post(
                UPLOAD_URL,
                files={"file": (Path(path).name, handle, mime)},
                data=data,
                timeout=UPLOAD_TIMEOUT,
            )
    except requests.RequestException as exc:
        raise RuntimeError(f"上传失败: {exc}") from exc
    if response.status_code != 200:
        raise RuntimeError(f"上传失败 HTTP {response.status_code}: {response.text[:300]}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"上传返回非 JSON: {response.text[:300]}") from exc
    if payload.get("status") != "success":
        raise RuntimeError(f"上传失败: {payload.get('message') or payload}")
    block = payload.get("data") or {}
    direct = block.get("url_direct")
    if not direct:
        raise RuntimeError("上传返回缺少 url_direct")
    return {"url": direct, "delete_url": block.get("url_delete")}


def safe_stem(name):
    cleaned = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff._-]+", "_", (name or "").strip()).strip("._-")
    return cleaned or f"fish_{int(time.time())}"


def build_output_path(save_dir, filename, fmt):
    save_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(filename) if filename else f"fish_{int(time.time())}_{time.strftime('%H%M%S')}"
    suffix = f".{fmt}"
    if stem.lower().endswith(suffix):
        stem = stem[: -len(suffix)]
    target = save_dir / f"{stem}{suffix}"
    if not target.exists():
        return target
    for index in range(1, 10000):
        candidate = save_dir / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError("无法生成唯一的输出文件名")


# ---------------------------------------------------------------- commands

def cmd_voices(args):
    env = load_env()
    voices = parse_reference_list(env)
    model = env_get(env, "MODEL") or DEFAULT_MODEL
    header = {
        "voices": len(voices),
        "model": model,
        "preset": env_get(env, "PRESET") or "quality",
        "format": env_get(env, "FORMAT") or "mp3",
        "default_voice": env_get(env, "DEFAULT_VOICE"),
        "save_path": env_get(env, "SAVE_PATH"),
        "api_key": mask_key(env_get(env, "API_KEY", "API")),
        "env_source": str(ENV_PATH),
    }
    if args.json:
        return {"status": "success", "config": header, "voices": voices}

    lines = [f"# Fish Audio 音色目录（{len(voices)} 个）", ""]
    lines.append(
        f"- model: `{header['model']}` ｜ preset: `{header['preset']}` ｜ format: `{header['format']}`"
    )
    lines.append(f"- API Key: {header['api_key']} ｜ 输出目录: `{header['save_path'] or '未配置'}`")
    if header["default_voice"]:
        lines.append(f"- 默认音色: `{header['default_voice']}`")
    lines.append("")
    if not voices:
        lines.append("_REFERENCE_LIST 为空。在 scripts/.env 里填入音色后重新运行。_")
        return {"status": "success", "text": "\n".join(lines)}

    lines.append("| # | 名称 | reference_id | 描述 |")
    lines.append("|---|---|---|---|")
    for index, voice in enumerate(voices, 1):
        desc = voice["description"].replace("|", "/").replace("\n", " ")
        tags = f"（{', '.join(voice['tags'])}）" if voice["tags"] else ""
        lines.append(f"| {index} | {voice['name']} | `{voice['id']}` | {desc}{tags} |")
    return {"status": "success", "text": "\n".join(lines)}


def cmd_lint(args):
    env = load_env()
    voices = parse_reference_list(env)
    model = (args.model or env_get(env, "MODEL") or DEFAULT_MODEL).strip()
    text = read_text(args)
    voice_ids = resolve_voices(args.voice, voices) if args.voice else []
    issues = lint_text(text, model, len(voice_ids) or 1)
    return {
        "status": "success",
        "issues": issues,
        "blocking": any(i["level"] == "error" for i in issues),
    }


def cmd_say(args):
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")

    env = load_env()
    voices = parse_reference_list(env)
    payload, meta = build_payload(args, env, voices)

    save_path = args.out_dir or env_get(env, "SAVE_PATH")
    if not save_path:
        raise ValueError("SAVE_PATH 未配置：请在 scripts/.env 里设置输出目录，或传 --out-dir")
    save_dir = Path(save_path).expanduser()

    if args.dry_run:
        return {"status": "success", "dry_run": True, "payload": payload}

    api_key = env_get(env, "API_KEY", "API")
    if not api_key:
        raise ValueError("API_KEY 未配置：请在 scripts/.env 里填写")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": meta["model"],
    }
    try:
        response = requests.post(TTS_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise RuntimeError(f"网络请求失败: {exc}") from exc

    if response.status_code != 200:
        detail = response.text[:600]
        hints = {
            401: "API Key 无效或已过期，检查 scripts/.env 的 API_KEY",
            402: "该模型需要额度。免费方案请把 MODEL 设为 s2.1-pro-free",
            429: "并发超限（无 Retry-After），请指数退避重试或降低并发",
            400: "请求被拒绝，常见原因：language 标签非法、音色 id 不存在、参数越界",
        }
        hint = hints.get(response.status_code, "")
        raise RuntimeError(f"HTTP {response.status_code}: {detail}" + (f" ｜ 建议: {hint}" if hint else ""))

    output_path = build_output_path(save_dir, args.name, meta["format"])
    output_path.write_bytes(response.content)
    if output_path.stat().st_size == 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("返回了空音频文件")

    if args.keep_script:
        output_path.with_suffix(".txt").write_text(payload["text"], encoding="utf-8")

    share = args.share
    if share is None:
        share = env_get(env, "SHARE").lower() not in ("", "0", "false", "off", "no")

    shared, share_error = None, None
    if share:
        try:
            shared = upload_audio(output_path, meta["format"], env_get(env, "URUSAI_API_TOKEN"))
        except Exception as exc:
            share_error = str(exc)

    result = {"status": "success"}
    if shared:
        result["url"] = shared["url"]
        if shared.get("delete_url"):
            result["delete_url"] = shared["delete_url"]
    else:
        result["url"] = output_path.resolve().as_uri()
        if share_error:
            result["share_error"] = share_error
    result["local_path"] = str(output_path)
    result["bytes"] = output_path.stat().st_size
    return result


# ---------------------------------------------------------------- cli

def build_parser():
    parser = argparse.ArgumentParser(
        prog="fish_core.py",
        description="Fish Audio TTS：读音色目录 / 生成语音 / 检查脚本",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    voices = sub.add_parser("voices", help="列出 .env 里配置的所有音色、描述和 reference id")
    voices.add_argument("--json", action="store_true", help="输出 JSON 而非 Markdown 表格")
    voices.set_defaults(func=cmd_voices)

    def add_text_args(p):
        p.add_argument("text", nargs="?", help="要合成的文本（含 [情绪] 标签）")
        p.add_argument("--text-file", help="从文件读取文本；用 - 表示 stdin")

    lint = sub.add_parser("lint", help="可选：静态检查脚本，不发起请求、不花钱")
    add_text_args(lint)
    lint.add_argument("--model", help="覆盖 .env 的 MODEL")
    lint.add_argument("--voice", help="音色名或 id，多说话人用 | 分隔")
    lint.set_defaults(func=cmd_lint)

    say = sub.add_parser("say", help="生成语音并保存到 SAVE_PATH")
    add_text_args(say)
    say.add_argument("--voice", help="音色名或 reference_id；多说话人用 | 分隔，如 \"旁白|船长\"")
    say.add_argument("--name", help="输出文件名（不含扩展名）")
    say.add_argument("--model", help="覆盖 .env 的 MODEL，如 s2.1-pro-free / drama-3")
    say.add_argument("--format", help="mp3 / wav / pcm / opus")
    say.add_argument("--preset", help="quality / balanced / fast")
    say.add_argument("--latency", choices=["normal", "balanced"], help="覆盖 preset 的延迟策略")
    say.add_argument("--chunk-length", type=int, help="100-300，越大越稳")
    say.add_argument("--mp3-bitrate", type=int, choices=[64, 128, 192], help="mp3 码率")
    say.add_argument("--sample-rate", type=int, help="wav 采样率，如 44100")
    say.add_argument("--speed", type=float, help="0.5-2.0")
    say.add_argument("--language", help="BCP-47，如 zh-CN / en / es-MX；只影响数字日期读法")
    say.add_argument("--repetition-penalty", type=float, help=">1.0 抑制重复发音，如 1.2")
    say.add_argument("--no-normalize", action="store_true", help="关闭文本规范化")
    say.add_argument("--out-dir", help="覆盖 .env 的 SAVE_PATH")
    say.add_argument("--share", action=argparse.BooleanOptionalAction, default=None,
                     help="上传到免费文件床并返回直链（默认读 .env 的 SHARE）")
    say.add_argument("--dry-run", action="store_true", help="只打印最终 payload，不发起请求")
    say.add_argument("--keep-script", action="store_true", help="把文本另存为同名 .txt")
    say.set_defaults(func=cmd_say)

    return parser


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    args = build_parser().parse_args(argv[1:])
    try:
        result = args.func(args)
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 2

    if "text" in result:
        print(result.pop("text"))
        if result.get("config") or result.get("voices"):
            print()
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "success" else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
