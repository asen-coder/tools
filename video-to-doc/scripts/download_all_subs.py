#!/usr/bin/env python3
"""批量下载B站系列视频的字幕。"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict

# B站视频信息
AID = 116328551750167

# 70集的 cid 信息
EPISODES = [
    {"cid": 37145937565, "page": 1, "part": "1.最新版1LangGraph的介绍"},
    {"cid": 37145938416, "page": 2, "part": "2.Agent和WorkFlow"},
    {"cid": 37145938783, "page": 3, "part": "3.安装LangGraph本地服务(一)"},
    {"cid": 37145938839, "page": 4, "part": "4.安装LangGraph本地服务(二)"},
    {"cid": 37145939055, "page": 5, "part": "5.启动LangGraph服务器"},
    {"cid": 37145939339, "page": 6, "part": "6.调用Agent发布的API接口(一)"},
    {"cid": 37145939782, "page": 7, "part": "7.调用Agent发布的API接口(二)"},
    {"cid": 37145939778, "page": 8, "part": "8.Tool的定义(一)"},
    {"cid": 37145939946, "page": 9, "part": "9.Tool的定义(二)"},
    {"cid": 37146001848, "page": 10, "part": "10.Tool的定义(三)"},
    {"cid": 37146001820, "page": 11, "part": "11.Qwen3大模型工具调用解析器的错误"},
    {"cid": 37146002187, "page": 12, "part": "12.解决Qwen3流式输出的问题"},
    {"cid": 37146002521, "page": 13, "part": "13.根据Rannable对象创建工具"},
    {"cid": 37146002692, "page": 14, "part": "14.继承BaseTool创建工具"},
    {"cid": 37146002892, "page": 15, "part": "15.Configurable静态配置(一)"},
    {"cid": 37146003235, "page": 16, "part": "16.Configurable静态配置(二)"},
    {"cid": 37146003013, "page": 17, "part": "17.AgentState状态详解(一)"},
    {"cid": 37146003602, "page": 18, "part": "18.AgentState状态详解(二)"},
    {"cid": 37146003962, "page": 19, "part": "19.AgentState状态详解(三)"},
    {"cid": 37146004017, "page": 20, "part": "20.记忆存储的介绍"},
    {"cid": 37146004183, "page": 21, "part": "21.开发环境下的短期记忆案例"},
    {"cid": 37146004581, "page": 22, "part": "22.Postgresql实现Agent短期存储"},
    {"cid": 37146004869, "page": 23, "part": "23.Postgresql实现长期存储"},
    {"cid": 37146004961, "page": 24, "part": "24.LangGraph中WorkFlow的概念"},
    {"cid": 37146005061, "page": 25, "part": "25.工作流的State和Reducer函数"},
    {"cid": 37146067083, "page": 26, "part": "26.工作流的节点和路由函数"},
    {"cid": 37146067181, "page": 27, "part": "27.评估器案例(一)"},
    {"cid": 37146067477, "page": 28, "part": "28.评估器案例(二)"},
    {"cid": 37146067876, "page": 29, "part": "29.评估器案例(三)"},
    {"cid": 37146067938, "page": 30, "part": "30.评估器案例(四)"},
    {"cid": 37146068289, "page": 31, "part": "31.智能小秘书案例+MCP工具"},
    {"cid": 37146068429, "page": 32, "part": "32.异步+并发执行工具类"},
    {"cid": 37146068886, "page": 33, "part": "33.定义小秘书工作流(一)"},
    {"cid": 37146068955, "page": 34, "part": "34.定义小秘书工作流(二)"},
    {"cid": 37146069241, "page": 35, "part": "35.测试完整的工具调用"},
    {"cid": 37146069437, "page": 36, "part": "36.简化代码+ToolNode节点"},
    {"cid": 37146069520, "page": 37, "part": "37.加入第一种人工介入"},
    {"cid": 37146069878, "page": 38, "part": "38.用户审批工具的执行"},
    {"cid": 37146069846, "page": 39, "part": "39.人工填写审批理由修改状态"},
    {"cid": 37146070050, "page": 40, "part": "40.新版本加入的中断方法"},
    {"cid": 37146527728, "page": 41, "part": "41.LCEL语法案例(一)"},
    {"cid": 37146528642, "page": 42, "part": "42.Embeddings是什么？ - 副本"},
    {"cid": 37146529216, "page": 43, "part": "43.Embeddings是什么？"},
    {"cid": 37146591686, "page": 44, "part": "44.LCEL语法案例(二)"},
    {"cid": 37146592692, "page": 45, "part": "45.Embeddings和One-Hot比较"},
    {"cid": 37146593053, "page": 46, "part": "46.LCEL语法案例(三)"},
    {"cid": 37146594319, "page": 47, "part": "47.OpenAI的Embedding"},
    {"cid": 37146594885, "page": 48, "part": "48.LCEL语法案例(四)"},
    {"cid": 37146656934, "page": 49, "part": "49.部署BGE-Large的嵌入模型"},
    {"cid": 37146657743, "page": 50, "part": "50.LCEL语法案例(五)"},
    {"cid": 37146658325, "page": 51, "part": "51.部署Qwen3的嵌入模型"},
    {"cid": 37146658487, "page": 52, "part": "52.LCEL语法案例(六)"},
    {"cid": 37146659107, "page": 53, "part": "53.Qwen3的嵌入模型和Langchain整合"},
    {"cid": 37146659529, "page": 54, "part": "54.LCEL语法案例(七)"},
    {"cid": 37146660439, "page": 55, "part": "55.评论数据语义搜索案例(一)"},
    {"cid": 37146722611, "page": 56, "part": "56.LCEL语法案例(八)"},
    {"cid": 37146723661, "page": 57, "part": "57.评论数据语义搜索案例(二)"},
    {"cid": 37146724064, "page": 58, "part": "58.FAISS向量数据库(一)"},
    {"cid": 37146724733, "page": 59, "part": "59.LCEL语法案例(九)"},
    {"cid": 37146725019, "page": 60, "part": "60.LCEL语法案例(十)"},
    {"cid": 37146984517, "page": 61, "part": "61.MCP的介绍"},
    {"cid": 37146985134, "page": 62, "part": "62.MCP的通信机制原理"},
    {"cid": 37146985506, "page": 63, "part": "63.FastMCP的sse通信实现"},
    {"cid": 37146985826, "page": 64, "part": "64.FastMCP的Streamable通信实现"},
    {"cid": 37146985809, "page": 65, "part": "65.Agent+MCP工具"},
    {"cid": 37146986341, "page": 66, "part": "66.Agent调用Java的MCP服务器"},
    {"cid": 37146986660, "page": 67, "part": "67.Agent调用外网的MCP服务"},
    {"cid": 37146986851, "page": 68, "part": "68.MCP服务的认证机制"},
    {"cid": 37146987292, "page": 69, "part": "69.MCP服务的认证实现(一)"},
    {"cid": 37146987488, "page": 70, "part": "70.MCP服务的认证实现(二)"}
]

def fetch_json(url: str) -> dict:
    """请求 JSON 数据，返回解析后的字典。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def download_subtitle(aid: int, cid: int, output_path: Path) -> bool:
    """下载单个视频的字幕。"""
    try:
        # 调用 B站播放器 API 获取字幕信息
        api_url = f"https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}"
        data = fetch_json(api_url)

        # 调试：打印第一集的 API 返回结构
        if cid == 37145937565:
            print(f"[调试] API 返回结构: {json.dumps(data, ensure_ascii=False, indent=2)[:800]}")

        subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])

        # 调试：打印第一集的字幕列表
        if cid == 37145937565:
            print(f"[调试] 字幕列表: {subtitles}")

        # 查找 AI 中文字幕
        ai_sub = next((s for s in subtitles if s.get("lan") == "ai-zh"), None)

        if not ai_sub and subtitles:
            # 如果没有 AI 字幕，使用第一个可用字幕
            ai_sub = subtitles[0]

        if not ai_sub:
            print(f"[警告] 第 {cid} 没有找到字幕")
            return False

        sub_url = ai_sub.get("subtitle_url", "")
        if not sub_url:
            print(f"[警告] 第 {cid} 字幕 URL 为空")
            return False

        # 补全 URL 协议
        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url

        # 下载字幕 JSON
        sub_data = fetch_json(sub_url)

        # 保存字幕文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(sub_data, f, ensure_ascii=False, indent=2)

        print(f"[完成] {output_path.name}")
        return True

    except Exception as e:
        print(f"[错误] 第 {cid} 字幕下载失败: {e}")
        return False

def main():
    # 输出目录
    out_dir = Path(__file__).parent.parent / "out" / "subtitles"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"开始下载 {len(EPISODES)} 集字幕...")

    success_count = 0
    for ep in EPISODES:
        page_num = ep["page"]
        cid = ep["cid"]
        part_name = ep["part"]

        # 输出文件名：ep01.json, ep02.json, ...
        output_file = out_dir / f"ep{page_num:02d}.json"

        print(f"[{page_num:02d}/{len(EPISODES)}] {part_name} (cid={cid})")

        if download_subtitle(AID, cid, output_file):
            success_count += 1

    print(f"\n下载完成！成功: {success_count}/{len(EPISODES)}")
    print(f"字幕保存在: {out_dir}")

if __name__ == "__main__":
    main()
