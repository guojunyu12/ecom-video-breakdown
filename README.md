# ecom-video-breakdown

**抖音电商爆款视频拆解 Skill：拆结构、对比自家视频、生成适合自己商品的新脚本。**

上传参考视频，让 Agent 分析前 3 秒钩子、卖点表达、内容节奏、镜头和花字。加入自家视频，可以得到差距表和优先改法；加入商品信息，可以按参考结构生成新的带货脚本。

[查看中文产品介绍页](https://guojunyu12.github.io/ecom-video-breakdown/)

## 解决什么问题

找到一条值得参考的带货视频后，往往还需要弄清楚：

- 开场如何吸引注意，卖点如何展开？
- 哪些镜头在展示商品，哪些在建立信任？
- 自家视频在钩子、节奏、证明方式上差在哪里？
- 换成自己的商品，应该怎么组织画面和台词？

这个 Skill 将这些分析整理成拆解报告、对比建议和拍摄脚本，帮助你把参考视频用到下一条素材中。

## 核心功能

| 功能 | 分析内容 | 输出 |
|---|---|---|
| 爆款结构拆解 | 目标人群、主卖点、内容节拍、镜头作用、钩子与行动引导 | 四层拆解报告、时间轴、分镜表 |
| 自家视频对比 | 双方的开场、卖点、节奏、证明方式和产品展示 | 差距表、7 维评分、Top 3 改法、改版脚本 |
| 商品脚本生成 | 将参考结构映射到自家商品卖点和证据 | 3 个创作角度、推荐方案、完整脚本 |
| 花字与静音分析 | 屏幕文字承载了哪些信息，静音时能否理解卖点 | 花字整理、静音可看性判断 |
| 多视频归纳 | 多条参考视频中重复出现的结构 | 共性公式、可迁移与不可迁移因素 |
| 合规风险检查 | 极限词、效果承诺、原创表达、AI 内容标识等 | 风险项及修改提示 |

### 四层拆解框架

| 层级 | 关注点 |
|---|---|
| 策略层 | 卖给谁、主要卖点、内容形式、情绪基调 |
| 节拍层 | 开场、卖点、证明、收尾如何安排，各段持续多久 |
| 镜头层 | 每个镜头的画面、口播、花字和作用 |
| 元素层 | 前 3 秒钩子、首帧、声音、转场、产品露出、行动引导 |

## 你提供什么，会得到什么

| 输入 | 输出 |
|---|---|
| 1 条参考视频 | 单条拆解报告，标注单样本局限 |
| 2–5 条参考视频 | 逐条拆解与共性结构 |
| 参考视频 + 自家视频 | 拆解、差距表、评分、优先改法与改版脚本 |
| 参考视频 + 商品信息 | 卖点映射、创作角度与新脚本 |

Agent 会根据素材自动判断处理方式。

## 使用示例

安装后，在支持 Skills 的 Agent 中上传视频或提供本地文件路径，然后直接描述需求。

### 拆解一条视频

```text
拆解这个带货视频，重点看前 3 秒钩子、
卖点表达和镜头节奏，给我时间轴和分镜表。

文件：爆款_保温杯.mp4
```

### 对比自家视频

```text
第一条是参考爆款，第二条是我家的。
按同一套框架拆解，告诉我差在哪里，
给出最优先的 3 个改法和改版脚本。

文件：爆款_保温杯.mp4、自家_保温杯.mp4
```

### 给自己的商品写脚本

```text
参考这条视频的结构，给我的通勤双肩包写一条新脚本。

价格：199 元
人群：每天乘地铁通勤的上班族
卖点：独立电脑仓、可放雨伞的侧袋、背部透气设计
可用素材：收纳实拍、上身实拍、细节特写

给我 3 个创作角度，推荐一个，并写出完整分镜和口播。
文件：爆款_双肩包.mp4
```

### 提炼多条视频的共性

```text
拆解这 3 条同品类视频，找出共同的开场方式、
卖点顺序和证明方式，整理成可复用的结构模板。
```

## 素材怎么提供

**优先使用本地视频文件**，支持 mp4、mov 等常见格式。

建议用文件名说明角色：

```text
爆款_商品名.mp4
自家_商品名.mp4
```

也可以直接在消息里说明「第 2 条是我家的」。角色不明确时，Agent 会先确认，再进行对比。

抖音分享链接或口令可以尝试下载；失败时，请保存视频后提供本地文件。只有文案或截图时，可以做部分分析，报告会标注缺失信息。

## 安装

将仓库下载到你的 Agent 支持的 Skills 目录。以 Claude Code 为例：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/guojunyu12/ecom-video-breakdown.git \
  ~/.claude/skills/ecom-video-breakdown
```

运行视频预处理脚本需要 Python 3 和 FFmpeg。以 macOS 为例：

```bash
brew install ffmpeg

cd ~/.claude/skills/ecom-video-breakdown
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

OCR 用于识别花字，ASR 用于转写口播。工具不可用时，可以由 Agent 看帧读取文字，或使用你提供的口播文案，报告会注明来源。

## 使用说明

- 「爆款」由用户提供的表现数据、公开互动数据或主观选择确定，报告会注明证据来源。
- 评分用于整理对比意见，权重尚待真实样本校准，不预测播放量或成交额。
- 新脚本中的效果、数字和承诺必须有商品信息或证据支持。
- 示例均为虚构；真实视频完整流程及部分转写、下载路径仍待验证。
- 学习参考视频的结构，重新组织自家商品的画面和表达。

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

## License

MIT。
