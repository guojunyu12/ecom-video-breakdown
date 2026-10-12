#!/usr/bin/env python3
"""花字/字幕 OCR：对抽出的帧做文字识别，合并成按时间排列的文字层，供「静音可看性」评估。

用法：
  python ocr.py work/视频名 [--engine auto|rapidocr|paddle] [--min-score 0.6]
读取 work/视频名/hook/*.jpg 与 shots/*.jpg，输出 work/视频名/ocr.json：
  {"engine":..., "items":[{"frame":..., "t":秒, "texts":[{"text":..., "score":..., "box_y":相对高度}]}],
   "unique_texts":[按首次出现排序的去重文字]}
安装：pip install rapidocr_onnxruntime   （推荐，轻量）
  或：pip install paddleocr paddlepaddle
"""
import argparse, json, re, sys
from pathlib import Path


def frame_time(p: Path, hook_fps: int):
    m = re.search(r"_(\d+\.\d+)s", p.name)
    if m:
        return float(m.group(1))
    if p.parent.name == "hook":
        return round((int(p.stem) - 1) / hook_fps, 2)
    return None


def load_engine(name):
    if name in ("auto", "rapidocr"):
        try:
            from rapidocr_onnxruntime import RapidOCR
            eng = RapidOCR()
            def f(img):
                res, _ = eng(str(img))
                return [(r[1], float(r[2]), r[0]) for r in (res or [])]
            return "rapidocr", f
        except ImportError:
            if name == "rapidocr":
                raise
    from paddleocr import PaddleOCR
    eng = PaddleOCR(lang="ch")
    def g(img):
        out = []
        for page in eng.ocr(str(img)) or []:
            for box, (txt, sc) in page or []:
                out.append((txt, float(sc), box))
        return out
    return "paddleocr", g


def main():
    p = argparse.ArgumentParser(description="花字/字幕 OCR（RapidOCR 优先，PaddleOCR 兜底）。")
    p.add_argument("workdir", help="probe_frames.py 生成的单条视频目录")
    p.add_argument("--engine", choices=["auto", "rapidocr", "paddle"], default="auto")
    p.add_argument("--min-score", type=float, default=0.6, help="置信度下限，默认 0.6")
    p.add_argument("--hook-fps", type=int, default=4, help="与 probe_frames.py 保持一致，默认 4")
    a = p.parse_args()
    wd = Path(a.workdir)
    frames = sorted((wd / "hook").glob("*.jpg")) + sorted((wd / "shots").glob("*.jpg"))
    if not frames:
        print(f"[错误] {wd} 下没有帧，请先运行 probe_frames.py", file=sys.stderr); sys.exit(1)
    try:
        name, fn = load_engine(a.engine)
    except ImportError:
        print("[错误] 未安装 OCR 引擎：pip install rapidocr_onnxruntime（或 paddleocr）。"
              "\n  无法 OCR 时，由模型直接看帧读花字，并在报告中注明「花字为目测，未经 OCR」。", file=sys.stderr)
        sys.exit(2)
    items, seen, uniq = [], set(), []
    for fr in frames:
        texts = []
        for txt, sc, box in fn(fr):
            if sc < a.min_score or not txt.strip():
                continue
            try:
                ys = [pt[1] for pt in box]
                y = sum(ys) / len(ys)
            except Exception:
                y = None
            texts.append({"text": txt.strip(), "score": round(sc, 3), "y": round(y, 1) if y is not None else None})
            key = re.sub(r"\s+", "", txt)
            if key not in seen:
                seen.add(key); uniq.append(txt.strip())
        items.append({"frame": str(fr), "t": frame_time(fr, a.hook_fps), "texts": texts})
    items.sort(key=lambda x: (x["t"] is None, x["t"] or 0))
    (wd / "ocr.json").write_text(json.dumps({"engine": name, "items": items, "unique_texts": uniq}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[完成] {name}：{len(frames)} 帧，识别到 {len(uniq)} 条不重复文字 → {wd/'ocr.json'}")


if __name__ == "__main__":
    main()
