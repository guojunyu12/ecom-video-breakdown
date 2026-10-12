#!/usr/bin/env python3
"""抖音分享链接/口令 → 视频文件（尽力而为，失败就请用户直接上传文件）。

做法：从分享文本提取 URL → 跟随短链拿作品 ID → 读取公开分享页中的播放地址 →
失败时可选回退 yt-dlp（不传 cookie）。
本脚本 **不读取、不导出、不打印任何 Cookie、msToken、a_bogus 等签名参数**。
抖音风控经常变化，失败是正常情况，请提示用户：在抖音 App 里「保存本地」后上传 mp4。

用法：
  python douyin_fetch.py "7.94 复制打开抖音… https://v.douyin.com/xxxx/" --out downloads/ [--no-ytdlp]
"""
import argparse, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
FAIL_HINT = "下载失败。请在抖音 App 里点「分享 → 保存本地」，然后直接上传视频文件。"


def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read()


def extract_url(text):
    m = re.search(r"https?://[^\s，。]+", text)
    return m.group(0) if m else None


def video_id(url):
    m = re.search(r"/(?:video|note)/(\d{10,})", url) or re.search(r"(?:modal_id|aweme_id)=(\d{10,})", url)
    return m.group(1) if m else None


def via_share_page(vid):
    _, html = get(f"https://www.iesdouyin.com/share/video/{vid}/")
    html = html.decode("utf-8", "ignore")
    m = re.search(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", html, re.S)
    if not m:
        raise RuntimeError("分享页没有数据（可能被风控或作品已删除）")
    data = json.loads(m.group(1))
    def find(o):
        if isinstance(o, dict):
            if "play_addr" in o and isinstance(o["play_addr"], dict):
                return o
            for v in o.values():
                r = find(v)
                if r: return r
        elif isinstance(o, list):
            for v in o:
                r = find(v)
                if r: return r
    v = find(data)
    if not v:
        raise RuntimeError("没找到播放地址（可能是图文作品）")
    url = v["play_addr"]["url_list"][0].replace("playwm", "play")
    return url


def main():
    p = argparse.ArgumentParser(description="抖音分享链接/口令下载（尽力而为，不读取 Cookie）。")
    p.add_argument("share", help="抖音分享文本或链接")
    p.add_argument("--out", default="downloads", help="保存目录，默认 downloads/")
    p.add_argument("--name", help="保存文件名（不含扩展名），建议用 爆款_xxx 或 自家_xxx")
    p.add_argument("--no-ytdlp", action="store_true", help="失败时不尝试 yt-dlp")
    a = p.parse_args()
    url = extract_url(a.share)
    if not url:
        print(f"[错误] 没有在文本里找到链接。{FAIL_HINT}", file=sys.stderr); sys.exit(1)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    try:
        final, _ = get(url)
        vid = video_id(final) or video_id(url)
        if not vid:
            raise RuntimeError(f"无法识别作品 ID：{final[:80]}")
        dest = out / f"{a.name or 'douyin_' + vid}.mp4"
        play = via_share_page(vid)
        _, body = get(play, timeout=60)
        if len(body) < 50_000:
            raise RuntimeError("下载内容过小，不像视频")
        dest.write_bytes(body)
        print(f"[完成] {dest}（{len(body)//1024} KB）")
        return
    except Exception as e:
        print(f"[提示] 分享页方式失败：{e}", file=sys.stderr)
    if not a.no_ytdlp and shutil.which("yt-dlp"):
        tmpl = str(out / f"{a.name or 'douyin_%(id)s'}.%(ext)s")
        r = subprocess.run(["yt-dlp", "-q", "-o", tmpl, url], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"[完成] yt-dlp 下载到 {out}/"); return
        print(f"[提示] yt-dlp 也失败了：{r.stderr.strip()[-200:]}", file=sys.stderr)
    print(f"[失败] {FAIL_HINT}", file=sys.stderr)
    sys.exit(3)


if __name__ == "__main__":
    main()
