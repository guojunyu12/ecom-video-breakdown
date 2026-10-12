#!/usr/bin/env python3
"""中文语音转写：FunASR(SenseVoice-Small) 优先，faster-whisper 兜底。

用法：
  python asr.py work/视频名/audio.wav [--engine auto|funasr|whisper] [--whisper-model small] [--out transcript.json]
输出 JSON：{"engine":..., "text":..., "segments":[{"start":秒,"end":秒,"text":...}]}
安装（任选其一）：
  pip install funasr modelscope torch torchaudio     # 推荐，中文效果好，首次运行自动下载模型
  pip install faster-whisper                         # 兜底，首次运行自动下载 whisper 模型
注意：模型首次下载需要联网；SenseVoice 模型许可请以其官方仓库为准。
"""
import argparse, json, re, sys
from pathlib import Path


def by_funasr(audio: str):
    from funasr import AutoModel  # noqa
    model = AutoModel(model="iic/SenseVoiceSmall", vad_model="fsmn-vad", disable_update=True)
    res = model.generate(input=audio, language="zh", use_itn=True, batch_size_s=60)
    text = ""
    for r in res:
        text += re.sub(r"<\|[^|]*\|>", "", r.get("text", ""))
    # SenseVoice 默认不返回逐句时间戳，这里只给全文
    return {"engine": "funasr-sensevoice", "text": text.strip(), "segments": []}


def by_whisper(audio: str, size: str):
    from faster_whisper import WhisperModel  # noqa
    import subprocess, numpy as np
    # 用 ffmpeg 自行解码，避开 PyAV 版本兼容问题
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    m = WhisperModel(size, device="auto", compute_type="int8")
    segs, _ = m.transcribe(pcm, language="zh", vad_filter=True, initial_prompt="以下是普通话的句子，带标点。")
    out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
    return {"engine": f"faster-whisper-{size}", "text": "".join(s["text"] for s in out), "segments": out}


def main():
    p = argparse.ArgumentParser(description="中文 ASR：FunASR/SenseVoice 优先，faster-whisper 兜底。")
    p.add_argument("audio", help="音频文件（probe_frames.py 生成的 audio.wav）")
    p.add_argument("--engine", choices=["auto", "funasr", "whisper"], default="auto")
    p.add_argument("--whisper-model", default="small", help="faster-whisper 模型：tiny/base/small/medium，默认 small")
    p.add_argument("--out", help="输出 JSON 路径，默认与音频同目录 transcript.json")
    a = p.parse_args()
    if not Path(a.audio).is_file():
        print(f"[错误] 音频不存在：{a.audio}。没有音轨的视频请跳过转写，在报告中标注「无口播」。", file=sys.stderr); sys.exit(1)
    order = {"auto": ["funasr", "whisper"], "funasr": ["funasr"], "whisper": ["whisper"]}[a.engine]
    errors = []
    for eng in order:
        try:
            r = by_funasr(a.audio) if eng == "funasr" else by_whisper(a.audio, a.whisper_model)
            out = Path(a.out) if a.out else Path(a.audio).with_name("transcript.json")
            out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[完成] 引擎 {r['engine']}，{len(r['text'])} 字 → {out}")
            if not r["text"]:
                print("[提示] 转写为空：可能是纯音乐/无口播视频，报告里标注「无口播」。")
            return
        except ImportError:
            errors.append(f"{eng}: 未安装")
        except Exception as e:
            errors.append(f"{eng}: {e}")
    print("[错误] 所有转写引擎都不可用：\n  " + "\n  ".join(errors) +
          "\n  安装：pip install funasr modelscope torch torchaudio 或 pip install faster-whisper"
          "\n  也可以让用户直接粘贴口播文案，报告标注「转写来自用户提供」。", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
