# ecom-video-breakdown · 抖音电商爆款视频拆解 Skill

拆解抖音电商爆款视频的结构（策略层 → 节拍层 → 镜头层 → 元素层 + 抖音合规），可以和你自家的视频逐项对比，给出差距表、评分和 Top 3 改法；也可以按爆款结构给你的商品写复刻脚本。
**学结构，不抄表达；不编数据；合规前置。**

作者：jun yu ｜ 许可：MIT ｜ 格式：Anthropic Agent Skill（SKILL.md），适用于 Claude Code、Codex、Cursor 等支持 Skills 的 Agent。

## 能做什么
| 你给 | 你得到 |
|---|---|
| 1–5 条爆款视频 | 四层拆解报告；多条时给出共性公式 |
| 爆款 + 自家视频 | 再加：差距表、7 维加权评分（权重为初稿）、Top 3 改法、改版脚本 |
| 爆款 + 自家商品卖点 | 卖点映射（无证据的说法删除）、3 个复刻角度（保守照搬结构 / 换钩子 / 换证明方式）、完整脚本 |

模式会根据你给的东西自动判断，不用选。

## 安装
```bash
# 1. 下载 Skill
git clone https://github.com/guojunyu12/ecom-video-breakdown.git
# 2. 把整个文件夹放进 skills 目录，例如 Claude Code：
mkdir -p ~/.claude/skills
cp -r ecom-video-breakdown ~/.claude/skills/
# 3. 系统依赖
brew install ffmpeg        # macOS；Ubuntu: sudo apt install ffmpeg
# 4. Python 依赖（建议用虚拟环境）
cd ecom-video-breakdown
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 中文转写效果更好的话（较大）：pip install funasr modelscope torch torchaudio
```
Codex 用户可以将整个文件夹复制到 `~/.agents/skills/`；其他 Agent 请使用其支持的 Skills 目录。运行脚本前激活上述虚拟环境，并在安装后的 Skill 目录中执行命令。

没有装 OCR 或 ASR 也能用：Agent 会直接看帧读花字，或请你粘贴口播文案，并在报告里注明来源。

## 怎么用
1. **上传视频文件**（mp4/mov 最稳）。**文件名加前缀** `爆款_xxx.mp4` / `自家_xxx.mp4`，或者在消息里写「第 2 条是我家的」，就不用再确认谁是谁。
2. 想按爆款写新脚本，就附上你的商品：卖点、价格、人群、有哪些证据（检测报告、实拍、评价）。
3. 抖音分享链接也能试，但抖音风控变化快，经常下载失败；失败时请在 App 里「保存本地」后上传。

示例对话：
> 拆一下这两条，看看我的差在哪 [爆款_保温杯.mp4] [自家_保温杯.mp4]

## 目录
```
SKILL.md                 主流程（角色识别 → 素材 → 模式 → 预处理 → 四层拆解 → 输出）
scripts/
  probe_frames.py        元信息、首帧、前3秒密集帧、镜头切分、联系表、音轨（ffmpeg）
  asr.py                 中文转写：FunASR/SenseVoice 优先，faster-whisper 兜底
  ocr.py                 花字/字幕 OCR：RapidOCR 优先，PaddleOCR 兜底
  douyin_fetch.py        抖音分享链接下载（尽力而为，不读取 Cookie）
references/              四层框架、钩子分类、结构模板、评分量表、合规清单、角色识别规则
templates/               拆解报告、差距表、复刻脚本
examples/                2 个虚构示例
```

## 系列路线图
| Skill | 状态 |
|---|---|
| `ecom-video-breakdown` 爆款拆解 + 对比 + 复刻脚本 | ✅ v0.1 |
| `douyin-hook-library` 前 3 秒钩子库（按品类沉淀、检索、改写） | 计划中 |
| `batch-sku-script` 一个结构 × N 个 SKU 批量出脚本和拍摄清单 | 计划中 |
| `douyin-compliance-check` 脚本/成片合规检查（AI 标识、极限词、原创度） | 计划中 |
| `ads-creative-review` 投放素材数据复盘 | 草稿 |

## 致谢
思路和部分规则参考了以下 MIT 许可项目（**没有复制无许可证项目的代码**）：
- [alchaincyf/huashu-skills](https://github.com/alchaincyf/huashu-skills)：文案 6 类 + 画面 6 类钩子分类、结构模板
- [xianyu110/ecommerce-video-skills](https://github.com/xianyu110/ecommerce-video-skills)：卖点映射列、复刻角度、字数 ÷ 4.5 估时长
- [wocha-xiaoli/video-shot-analysis-feishu](https://github.com/wocha-xiaoli/video-shot-analysis-feishu)：ffmpeg 场景检测切镜、镜头字段
- [chubbyguan/chubbyskills](https://github.com/chubbyguan/chubbyskills)：抖音分享页解析 + 回退思路、SenseVoice 用法
- [creatify-ai/ad-creative-evaluator](https://github.com/creatify-ai/ad-creative-evaluator)：量表 + 加权评分形式、静音可看性维度
- [KINNONG/viral-video-breakdown](https://github.com/KINNONG/viral-video-breakdown)：文件夹式输出、可借鉴/不可照抄
以上代码均为本项目重写，未整段复制。
依赖库：FFmpeg、FunASR（MIT）、faster-whisper（MIT）、RapidOCR（Apache-2.0）、PaddleOCR（Apache-2.0）、yt-dlp（Unlicense）。SenseVoice 模型的许可请以其官方仓库为准。

## 声明
- 合规清单是风险提示，**不构成法律意见**；平台规则以抖音、巨量引擎官方最新公告为准。
- 请尊重原作者版权：本 Skill 只学结构，不支持搬运、换脸或照搬原画面和原台词。
- 下载功能仅供分析你有权使用的公开内容；不读取 Cookie 或签名参数。
- 评分权重是初稿，没有用真实投放数据校准，不预测播放量或成交额。

## 验证范围与已知局限

- 构建阶段使用合成视频验证了抽帧、镜头切分、RapidOCR 和 faster-whisper 的无口播路径；示例均为虚构。
- 发布前复查了四个脚本的 Python 语法、`--help` 和 Skill 引用文件是否存在。
- FunASR/SenseVoice、PaddleOCR、真实中文口播、真实抖音下载成功路径及真实带货视频完整流程尚未验证。
- 抖音分享页变化可能导致下载失败；SenseVoice 默认不提供逐句时间戳。
- 评分权重和静音可看性规则待真实样本校准。
- 项目代码采用 MIT；第三方依赖和模型各自的许可证独立适用。
