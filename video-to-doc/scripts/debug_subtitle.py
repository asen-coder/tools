#!/usr/bin/env python3
"""调试字幕 API。"""

import json
import urllib.request

def fetch_json(url: str) -> dict:
    """请求 JSON 数据，返回解析后的字典。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

# 第一集的信息
AID = 116328551750167
CID = 37145937565

api_url = f"https://api.bilibili.com/x/player/wbi/v2?aid={AID}&cid={CID}"
print(f"请求 URL: {api_url}\n")

data = fetch_json(api_url)

# 打印完整的 subtitle 相关信息
subtitle_info = data.get("data", {}).get("subtitle", {})
print(f"字幕信息: {json.dumps(subtitle_info, ensure_ascii=False, indent=2)}")
