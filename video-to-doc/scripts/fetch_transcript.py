#!/usr/bin/env python3
"""下载视频字幕；无字幕则用 Whisper 转写。

只做脏活：产出一份干净的带时间戳文本（transcript.md）和元数据（meta.json），
供后续由 Claude 生成中文教学文档。不在本脚本里做翻译/总结/判重点。

B站说明：
  B站需要登录 Cookie 才能访问（否则 412），并且字幕走独立的 AI 字幕 API
  而非 yt-dlp 能直接抓的标准字幕格式。
  推荐使用 --cookies 传入 Netscape 格式的 Cookie 文件。
  Cookie 文件可以通过浏览器插件（如 "Get cookies.txt LOCALLY"）导出。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


def die(msg: str, code: int = 1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def require(tool: str, hint: str):
    if shutil.which(tool) is None:
        die(f"缺少依赖 `{tool}`。{hint}")


def run_json(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        stderr = p.stderr.strip()
        if "412" in stderr and "bilibili" in " ".join(cmd).lower():
            die(
                "B站返回 412，需要提供登录 Cookie。\n"
                "  解决方法：\n"
                "    1. 用浏览器登录 bilibili.com\n"
                "    2. 用插件（如 Get cookies.txt LOCALLY）导出 cookies.txt\n"
                "    3. 运行：python fetch_transcript.py <url> --cookies cookies.txt"
            )
        die(f"命令失败: {' '.join(cmd)}\n{stderr}")
    return json.loads(p.stdout)


def detect_platform(url: str) -> str:
    if re.search(r"(youtube\.com|youtu\.be)", url):
        return "youtube"
    if re.search(r"(bilibili\.com|b23\.tv)", url):
        return "bilibili"
    return "unknown"


# ── B站 AI 字幕 ──────────────────────────────────────────────────────────────


def _bilibili_fetch_json(url: str, cookies: str | None) -> dict:
    """带 Cookie 请求 B站 API，返回解析后的 JSON。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    }
    if cookies:
        # cookies 参数可以是文件路径或 Cookie 字符串
        cookie_path = Path(cookies)
        if cookie_path.exists():
            cookie_str = _parse_netscape_cookies(cookie_path)
        else:
            cookie_str = cookies
        headers["Cookie"] = cookie_str

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())


def _parse_netscape_cookies(path: Path) -> str:
    """把 Netscape 格式 Cookie 文件转成 HTTP Cookie 字符串。"""
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7:
            pairs.append(f"{parts[5]}={parts[6]}")
    return "; ".join(pairs)


def fetch_bilibili_ai_subtitle(
    info: dict, cookies: str | None
) -> list[tuple[float, str]]:
    """通过 B站播放器 API 获取 AI 生成字幕，返回 [(start_sec, text)]。

    B站 AI 字幕不走标准字幕接口，需要：
      1. 从 yt-dlp info 提取 aid / cid
      2. 调 /x/player/wbi/v2 拿字幕 URL
      3. 下载字幕 JSON（aisubtitle.hdslb.com）
    """
    # 从 info 拿 aid（yt-dlp 对 B站把 id 当 BV 号，aid 在 formats 里）
    aid = None
    cid = None
    for fmt in info.get("formats") or []:
        if fmt.get("format_id", "").startswith("0") or True:
            # 尝试从 http_headers 或 url 里找 cid
            u = fmt.get("url", "")
            m = re.search(r"[?&]cid=(\d+)", u)
            if m:
                cid = int(m.group(1))
            break

    # 另一种方式：从 webpage_url 重新抓页面 __INITIAL_STATE__
    # 但 yt-dlp info 里有 _api_url 或类似字段有时包含 aid
    # 最可靠的：从 yt-dlp 的 subtitles 字段（B站 AI 字幕在 automatic_captions）
    # 实际上 yt-dlp >= 2024.03 已支持 B站 AI 字幕，只要有 Cookie 就能抓到
    # 所以本函数是备用路径
    entries = info.get("entries") or [info]
    all_segments: list[tuple[float, str]] = []

    for entry in entries:
        entry_aid = None
        entry_cid = None

        # 尝试从 formats url 提取 cid
        for fmt in entry.get("formats") or []:
            u = fmt.get("url", "")
            m = re.search(r"[?&]cid=(\d+)", u)
            if m:
                entry_cid = int(m.group(1))
                break

        # 尝试从 entry id 提取（格式：BV1xxxxx_p1）
        entry_id = entry.get("id", "")

        if not entry_cid:
            print(f"[B站] 无法从 info 提取 cid，跳过条目 {entry_id}", file=sys.stderr)
            continue

        # 需要 aid，从 formats 的 url 里有时能找到
        for fmt in entry.get("formats") or []:
            u = fmt.get("url", "")
            m = re.search(r"/(\d{10,})/", u)
            if m:
                entry_aid = int(m.group(1))
                break

        if not entry_aid:
            print(f"[B站] 无法从 info 提取 aid，跳过条目 {entry_id}", file=sys.stderr)
            continue

        try:
            api_url = (
                f"https://api.bilibili.com/x/player/wbi/v2"
                f"?aid={entry_aid}&cid={entry_cid}"
            )
            data = _bilibili_fetch_json(api_url, cookies)
            subtitles = (
                (data.get("data") or {}).get("subtitle", {}).get("subtitles", [])
            )
            sub = next((s for s in subtitles if s.get("lan") == "ai-zh"), None)
            sub = sub or (subtitles[0] if subtitles else None)
            if not sub:
                continue

            sub_url = sub.get("subtitle_url", "")
            if sub_url.startswith("//"):
                sub_url = "https:" + sub_url

            sub_data = _bilibili_fetch_json(sub_url, None)  # CDN 不需要 cookie
            for seg in sub_data.get("body") or []:
                text = (seg.get("content") or "").strip()
                if text:
                    all_segments.append((float(seg.get("from", 0)), text))
        except Exception as e:
            print(f"[B站] 获取 AI 字幕失败 ({entry_id}): {e}", file=sys.stderr)

    return all_segments


# ── 通用字幕处理 ──────────────────────────────────────────────────────────────


def pick_subtitle(info: dict) -> tuple[str, bool] | None:
    """优先人工字幕，其次自动字幕。返回 (lang, is_auto)。"""
    orig = info.get("language") or ""
    for store, is_auto in (
        (info.get("subtitles") or {}, False),
        (info.get("automatic_captions") or {}, True),
    ):
        if not store:
            continue
        langs = list(store.keys())
        if orig and orig in langs:
            return orig, is_auto
        preferred = [l for l in langs if "-" not in l] or langs
        return preferred[0], is_auto
    return None


_TAG = re.compile(r"<[^>]+>")
_TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")


def _to_seconds(h, m, s, ms) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_subtitle(path: Path) -> list[tuple[float, str]]:
    """解析 vtt/srt，返回 [(start_seconds, text)]，去掉滚动重复。"""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    segments: list[tuple[float, str]] = []
    last_text = None
    for block in re.split(r"\n\s*\n", raw):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        timing = next((l for l in lines if "-->" in l), None)
        if not timing:
            continue
        m = _TS.search(timing)
        if not m:
            continue
        start = _to_seconds(*m.groups())
        text_lines = [
            l for l in lines if "-->" not in l and l != "WEBVTT" and not l.isdigit()
        ]
        text = " ".join(_TAG.sub("", l) for l in text_lines).strip()
        text = re.sub(r"\s+", " ", text)
        if not text or text == last_text:
            continue
        segments.append((start, text))
        last_text = text
    return segments


def download_subtitle(
    url: str, lang: str, is_auto: bool, outdir: Path, cookies: str | None
) -> Path | None:
    flag = "--write-auto-subs" if is_auto else "--write-subs"
    tmpl = str(outdir / "sub")
    cmd = [
        "yt-dlp",
        "--skip-download",
        flag,
        "--sub-langs",
        lang,
        "--sub-format",
        "vtt/srt/best",
        "-o",
        tmpl,
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    cmd.append(url)
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    files = list(outdir.glob("sub*.vtt")) + list(outdir.glob("sub*.srt"))
    return files[0] if files else None


def transcribe_whisper(
    url: str, outdir: Path, cookies: str | None
) -> list[tuple[float, str]]:
    require("ffmpeg", "Whisper 转写需要 ffmpeg。安装后重试。")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die(
            "无字幕需 Whisper 兜底，但未安装 faster-whisper。\n  pip install faster-whisper"
        )
    audio = outdir / "audio.m4a"
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format",
        "m4a",
        "-o",
        str(outdir / "audio.%(ext)s"),
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    cmd.append(url)
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0 or not audio.exists():
        die(f"音频下载失败:\n{p.stderr.strip()}")
    print("[whisper] 转写中，长视频较慢…", file=sys.stderr)
    model = WhisperModel("base", compute_type="int8")
    segs, _ = model.transcribe(str(audio))
    return [(s.start, s.text.strip()) for s in segs if s.text.strip()]


def fmt_ts(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ── 主流程 ────────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(description="下载视频字幕或 Whisper 转写")
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default="./out", help="产物目录（默认 ./out）")
    ap.add_argument(
        "--cookies",
        metavar="FILE",
        help="Netscape 格式 Cookie 文件路径。B站必须提供，否则会 412。",
    )
    args = ap.parse_args()

    require("yt-dlp", "安装: pip install yt-dlp")
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    platform = detect_platform(args.url)
    print(f"[平台] {platform}", file=sys.stderr)

    ytdlp_cmd = ["yt-dlp", "-J", "--no-warnings"]
    if args.cookies:
        ytdlp_cmd += ["--cookies", args.cookies]
    ytdlp_cmd.append(args.url)

    info = run_json(ytdlp_cmd)

    # 处理播放列表：取第一条
    if info.get("entries"):
        print(f"[播放列表] 共 {len(info['entries'])} 条，取第一条", file=sys.stderr)
        info = info["entries"][0]

    title = info.get("title", "")
    lang = info.get("language") or ""

    segments: list[tuple[float, str]] = []
    source = "subtitle"
    used_lang = lang

    # 1. 优先 yt-dlp 能拿到的字幕
    pick = pick_subtitle(info)
    if pick:
        used_lang, is_auto = pick
        sub_file = download_subtitle(args.url, used_lang, is_auto, outdir, args.cookies)
        if sub_file:
            segments = parse_subtitle(sub_file)
            source = f"subtitle({'auto' if is_auto else 'manual'},{used_lang})"

    # 2. B站 AI 字幕备用路径（yt-dlp 拿不到时）
    if not segments and platform == "bilibili":
        print("[B站] 尝试通过 AI 字幕 API 获取字幕…", file=sys.stderr)
        if not args.cookies:
            print(
                "[警告] 未提供 --cookies，B站 AI 字幕 API 可能失败。\n"
                "       建议：python fetch_transcript.py <url> --cookies cookies.txt",
                file=sys.stderr,
            )
        # 重新拿完整 info（含所有分 P）
        full_info = run_json(ytdlp_cmd)
        segments = fetch_bilibili_ai_subtitle(full_info, args.cookies)
        if segments:
            source = "bilibili-ai-subtitle"
            used_lang = "zh"

    # 3. Whisper 兜底
    if not segments:
        print("[兜底] 无可用字幕，转 Whisper", file=sys.stderr)
        segments = transcribe_whisper(args.url, outdir, args.cookies)
        source = "whisper"
        used_lang = lang or "unknown"

    if not segments:
        die("既无字幕也未能转写出文本。")

    transcript = outdir / "transcript.md"
    with transcript.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for start, text in segments:
            f.write(f"[{fmt_ts(start)}] {text}\n")

    meta = {
        "url": args.url,
        "platform": platform,
        "title": title,
        "uploader": info.get("uploader"),
        "duration_sec": info.get("duration"),
        "original_language": lang,
        "transcript_language": used_lang,
        "transcript_source": source,
        "segment_count": len(segments),
    }
    (outdir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[完成] {transcript}  ({len(segments)} 段, 来源: {source})")


if __name__ == "__main__":
    main()
