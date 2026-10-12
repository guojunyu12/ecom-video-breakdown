#!/usr/bin/env python3
"""视频预处理：元信息 + 首帧 + 前3秒密集抽帧 + 镜头切分代表帧 + 联系表 + 音轨。

依赖：ffmpeg / ffprobe（需在 PATH 中）。只用 Python 标准库。
用法：
  python probe_frames.py VIDEO [VIDEO ...] --out work/ [--threshold 0.3] [--hook-fps 4]
输出（每条视频一个子目录）：
  meta.json        时长/分辨率/帧率/镜头列表/ASL
  first_frame.jpg  首帧（用于角色确认和首帧分析）
  hook/            前3秒密集帧
  shots/           每个镜头的代表帧（文件名含起始秒）
  contact.jpg      联系表（所有镜头代表帧拼图）
  audio.wav        16k 单声道音轨（无音轨时跳过）
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path


def die(msg, code=1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(video: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)])
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe 读取失败，文件可能损坏或不是视频：{r.stderr.strip()[:200]}")
    d = json.loads(r.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    if not v:
        raise RuntimeError("没有找到视频流")
    a = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den) if float(den) else 0.0
    return {
        "file": str(video), "duration": round(float(d["format"].get("duration", 0)), 2),
        "width": v.get("width"), "height": v.get("height"), "fps": round(fps, 2), "has_audio": a,
    }


def scene_times(video: Path, threshold: float) -> list:
    r = run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    return sorted({round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", r.stderr)})


def grab(video: Path, t: float, out: Path):
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(out)])


def process(video: Path, out_root: Path, threshold: float, hook_fps: int, min_shot: float):
    meta = probe(video)
    out = out_root / video.stem
    (out / "hook").mkdir(parents=True, exist_ok=True)
    (out / "shots").mkdir(exist_ok=True)
    grab(video, 0, out / "first_frame.jpg")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-t", "3", "-vf", f"fps={hook_fps}", "-q:v", "3", str(out / "hook" / "%02d.jpg")])

    dur = meta["duration"]
    cuts = [t for t in scene_times(video, threshold) if 0 < t < dur]
    starts = [0.0]
    for t in cuts:  # 合并过短镜头
        if t - starts[-1] >= min_shot:
            starts.append(t)
    mode = "scene_detection" if len(starts) > 1 else "fallback_uniform"
    if mode == "fallback_uniform":  # 没检测到切点：每2秒一帧兜底
        starts = [float(i) for i in range(0, max(1, int(dur)), 2)]
    shots = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else dur
        mid = s + (e - s) / 2
        fn = out / "shots" / f"{i+1:03d}_{s:06.2f}s.jpg"
        grab(video, mid, fn)
        shots.append({"index": i + 1, "start": round(s, 2), "end": round(e, 2), "duration": round(e - s, 2), "frame": str(fn)})
    meta.update({"shot_mode": mode, "threshold": threshold, "shots": shots, "shot_count": len(shots),
                 "asl": round(dur / len(shots), 2) if shots else None})

    cols = 6
    rows = (len(shots) + cols - 1) // cols
    r = run(["ffmpeg", "-y", "-loglevel", "error", "-pattern_type", "glob", "-i", str(out / "shots" / "*.jpg"),
             "-vf", f"scale=240:-1,tile={cols}x{max(rows,1)}", "-frames:v", "1", str(out / "contact.jpg")])
    if r.returncode != 0:
        print(f"[提示] 联系表生成失败（不影响其他输出）：{r.stderr.strip()[:120]}", file=sys.stderr)
    if meta["has_audio"]:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(out / "audio.wav")])
        meta["audio"] = str(out / "audio.wav")
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def main():
    p = argparse.ArgumentParser(description="抖音带货视频预处理：首帧、前3秒密集帧、镜头切分、联系表、音轨。")
    p.add_argument("videos", nargs="+", help="视频文件路径（mp4/mov 等）")
    p.add_argument("--out", default="work", help="输出目录，默认 work/")
    p.add_argument("--threshold", type=float, default=0.3, help="镜头切换阈值 0-1，默认 0.3；镜头太多调高，太少调低")
    p.add_argument("--hook-fps", type=int, default=4, help="前3秒每秒抽几帧，默认 4")
    p.add_argument("--min-shot", type=float, default=0.4, help="最短镜头秒数，短于此合并，默认 0.4")
    a = p.parse_args()
    for b in ("ffmpeg", "ffprobe"):
        if not shutil.which(b):
            die(f"没有找到 {b}。安装：macOS `brew install ffmpeg`，Ubuntu `sudo apt install ffmpeg`，Windows `winget install ffmpeg`")
    out_root = Path(a.out); out_root.mkdir(parents=True, exist_ok=True)
    ok = 0
    summary = []
    for v in a.videos:
        vp = Path(v)
        if not vp.is_file():
            print(f"[跳过] 文件不存在：{v}", file=sys.stderr); continue
        try:
            m = process(vp, out_root, a.threshold, a.hook_fps, a.min_shot)
            ok += 1
            summary.append({"file": v, "duration": m["duration"], "shots": m["shot_count"], "asl": m["asl"],
                            "first_frame": str(out_root / vp.stem / "first_frame.jpg")})
            print(f"[完成] {v}：{m['duration']}s，{m['shot_count']} 个镜头（{m['shot_mode']}），ASL {m['asl']}s")
        except Exception as e:
            print(f"[失败] {v}：{e}", file=sys.stderr)
    (out_root / "index.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if ok == 0:
        die("没有成功处理任何视频")


if __name__ == "__main__":
    main()
