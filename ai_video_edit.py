#!/usr/bin/env python3
"""
AI 自动剪辑脚本（基于字幕关键词）

功能：
1. 调用 Whisper 识别视频语音并生成分段时间轴
2. 仅保留包含关键词的片段
3. 自动拼接并导出新视频

依赖：
- ffmpeg
- openai-whisper
- moviepy

用法示例：
python ai_video_edit.py \
  --input input.mp4 \
  --output output.mp4 \
  --keywords "重点,结论,总结"
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import whisper
from moviepy.editor import VideoFileClip, concatenate_videoclips


@dataclass
class Segment:
    start: float
    end: float
    text: str



def transcribe_with_whisper(video_path: Path, model_name: str = "base") -> list[Segment]:
    model = whisper.load_model(model_name)
    result = model.transcribe(str(video_path), verbose=False)

    segments: list[Segment] = []
    for item in result.get("segments", []):
        segments.append(
            Segment(
                start=float(item["start"]),
                end=float(item["end"]),
                text=str(item["text"]).strip(),
            )
        )
    return segments


def merge_segments(segments: Iterable[Segment], gap_threshold: float = 0.6) -> list[Segment]:
    segments = sorted(segments, key=lambda s: s.start)
    if not segments:
        return []

    merged: list[Segment] = [segments[0]]
    for seg in segments[1:]:
        last = merged[-1]
        if seg.start - last.end <= gap_threshold:
            merged[-1] = Segment(
                start=last.start,
                end=max(last.end, seg.end),
                text=f"{last.text} {seg.text}".strip(),
            )
        else:
            merged.append(seg)
    return merged


def filter_by_keywords(segments: Iterable[Segment], keywords: list[str]) -> list[Segment]:
    clean_keywords = [k.strip() for k in keywords if k.strip()]
    if not clean_keywords:
        return list(segments)

    matched: list[Segment] = []
    for seg in segments:
        if any(k in seg.text for k in clean_keywords):
            matched.append(seg)
    return matched


def clip_video(input_path: Path, output_path: Path, segments: list[Segment], pad: float = 0.2) -> None:
    if not segments:
        raise ValueError("没有匹配到任何片段，请调整关键词。")

    with VideoFileClip(str(input_path)) as video:
        clips = []
        duration = video.duration
        for seg in segments:
            start = max(0, seg.start - pad)
            end = min(duration, seg.end + pad)
            if end > start:
                clips.append(video.subclip(start, end))

        if not clips:
            raise ValueError("切片为空，请检查输入视频或关键词配置。")

        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI 自动剪辑视频（关键词提取）")
    parser.add_argument("--input", required=True, type=Path, help="输入视频路径")
    parser.add_argument("--output", required=True, type=Path, help="输出视频路径")
    parser.add_argument(
        "--keywords",
        required=True,
        help="关键词列表，使用逗号分隔，例如：重点,总结,结论",
    )
    parser.add_argument(
        "--model",
        default="base",
        help="Whisper 模型名称：tiny/base/small/medium/large",
    )
    parser.add_argument(
        "--gap-threshold",
        type=float,
        default=0.6,
        help="合并相邻片段的最大间隔秒数",
    )
    parser.add_argument(
        "--pad",
        type=float,
        default=0.2,
        help="每个片段前后补偿秒数",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    keywords = [x.strip() for x in args.keywords.split(",")]

    segments = transcribe_with_whisper(args.input, model_name=args.model)
    matched = filter_by_keywords(segments, keywords)
    merged = merge_segments(matched, gap_threshold=args.gap_threshold)

    clip_video(args.input, args.output, merged, pad=args.pad)

    print(f"完成：共识别 {len(segments)} 段，保留 {len(merged)} 段。")
    print(f"输出文件：{args.output}")


if __name__ == "__main__":
    main()
