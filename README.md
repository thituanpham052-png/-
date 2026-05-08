# AI 剪辑视频：代码 + 教程

这是一个可直接运行的「AI 自动剪辑」示例，核心思路是：

1. 用 Whisper 把视频语音转文字并拿到时间轴。
2. 按关键词筛选出你要保留的句子片段。
3. 自动裁剪并拼接成新视频。

## 1) 环境准备

### 安装 FFmpeg
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt update && sudo apt install -y ffmpeg`
- Windows: 安装 ffmpeg 并加到 PATH

### 安装 Python 依赖
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\\Scripts\\activate
pip install -U pip
pip install openai-whisper moviepy
```

## 2) 运行脚本

```bash
python ai_video_edit.py \
  --input input.mp4 \
  --output output.mp4 \
  --keywords "重点,总结,结论"
```

可选参数：
- `--model`: Whisper 模型（`tiny/base/small/medium/large`）
- `--gap-threshold`: 片段合并阈值（秒）
- `--pad`: 每个片段前后留白（秒）

## 3) 常见用法

### 只保留“干货”
把关键词换成：`"核心,重点,结论,注意"`。

### 做课程精华版
把关键词换成：`"总结,作业,考试,重点"`。

### 做访谈高光
把关键词换成：`"惊讶,关键,第一次,最重要"`。

## 4) 调优建议

- 识别不准：把 `--model` 从 `base` 提升到 `small/medium`。
- 片段太碎：增大 `--gap-threshold`（如 `1.2`）。
- 切点太硬：增大 `--pad`（如 `0.35`）。
- 视频太长：先用 `tiny/base` 跑流程，最后再切到 `small`。

## 5) 进阶方向

- 情绪高光：结合音量峰值、语速变化、笑声检测。
- 多条件筛选：关键词 + 人脸出现 + OCR 文本（字幕/标题）。
- 自动出封面和标题：再接一个 LLM 生成文案。

---

如果你愿意，我还能继续帮你加：
- 自动去除口头禅（嗯、啊、然后）
- 自动加字幕（SRT/ASS）
- 批量处理整文件夹视频
