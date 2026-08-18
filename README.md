# Resume Engineering

> 写给真正做过项目、但每次投 JD 都要重新改一遍简历的人。

我自己准备 AI Agent、RAG 和 Python 后端岗位时，最麻烦的不是没有项目，而是：同一个项目，投不同岗位要换不同重点；写得太技术，HR 看不懂；写得太泛，面试官又会追问“到底做了什么”。

这个 Skill 做的事情比较朴素：先把做过的事、代码、测试和指标整理成一份证据库，再根据具体 JD 选出最相关的内容，改成能被 ATS 识别、也经得起技术面试追问的简历，最后生成一页 PDF。

它不会把每个人都写成“精通大模型的全栈专家”，也不会凭空补数字。

## 它适合谁

尤其适合准备下面这些岗位的人：

- 大模型应用开发 / LLM Application
- AI Agent / Agent Runtime / Agent Harness
- RAG / Agentic RAG / Research Agent
- Python / FastAPI 后端
- AI 平台 / 模型网关 / LLMOps
- 计算机视觉、深度学习、时序建模

如果你只想做一份通用的排版模板，这个项目可能有点重；如果你需要针对几十个相似 JD 持续投递，它会比较省时间。

## 它解决什么问题

很多简历项目看起来像这样：

```text
熟悉 Python、LangGraph、RAG、MCP、Docker，开发了一个智能 Agent。
```

面试官看完仍然不知道：

- 具体解决了什么问题？
- 哪部分是你自己做的？
- 为什么选这个方案？
- 出错时怎么处理？
- 所谓“提升”到底怎么测？

这个 Skill 会把项目改成一条更容易解释的证据链：

```text
场景/问题 → 个人动作 → 技术机制 → 结果或边界
```

例如：

```text
面向本地代码仓库长任务中工具误用和失败难恢复的问题，
实现 AgentLoop、Supervisor/TaskGraph 与 ExecutionPolicy，
接入 ToolGateway、Checkpoint/Resume 和 Docker 沙盒，
固定回归任务 24/24 通过。
```

这比单独列出十几个框架更能说明项目深度。

## 主要做法

### 1. 先建素材库，再做定向简历

简历母版只是展示文件，真正长期积累的是职业证据库。里面记录：

- 实习和项目卡片；
- 个人负责范围；
- 技术机制和设计取舍；
- 测试、实验和部署证据；
- 已知缺口；
- 可以使用的保守表述；
- 面试可能追问的问题。

以后新增一个测试结果或项目功能，先补进证据库，再生成新的岗位版本，不用从头回忆。

### 2. 根据 JD 选项目，不是把关键词全塞进去

每项要求会被分成四类：

| 类型 | 说明 |
|---|---|
| Direct | 直接做过，并且有证据 |
| Transferable | 技术机制可以迁移，业务场景不同 |
| Adjacent | 只有相邻知识或部分实现 |
| Gap | 目前没有可验证证据 |

例如：

- Agent Runtime 岗位优先展示 Repo Coding Runtime；
- RAG 岗位优先展示 PaperTrail；
- AI 平台岗位突出模型网关、权限、审计和部署；
- Python 后端岗位突出 FastAPI、异步任务、持久化和失败恢复；
- CV 岗位再加入论文、数据集和消融实验。

### 3. 用技术岗位能看懂的方式写项目

核心写法是 `PAR + Tech`：

```text
Problem / 场景问题
Action / 个人动作
Tech / 技术机制和取舍
Result / 结果或边界
```

有真实基线时，再用 `XYZ` 压缩结果：

```text
改善 X，结果达到 Y，通过 Z 实现。
```

没有可靠数字时，宁愿写“覆盖了哪些状态、工具、协议和测试项”，也不编造准确率、用户数或上线规模。

### 4. 交付前过两遍检查

第一遍站在 HR/ATS 的角度，看岗位标题、关键词、项目相关性和首屏可读性；第二遍站在面试官的角度，看架构、个人贡献、失败处理、设计取舍和指标口径。

只有两遍都能讲通，才生成最终 PDF。

## 一句话工作流

```text
JD
  → 岗位画像
  → 证据匹配
  → 项目改写
  → ATS/技术面试检查
  → RenderCV/PDF 校验
```

## 使用方式

### 在 Codex 中安装

把整个目录放到：

```text
Windows: %USERPROFILE%\.codex\skills\resume-engineering
macOS/Linux: ~/.codex/skills/resume-engineering
```

目录结构如下：

```text
resume-engineering/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    └── evidence-ledger-and-writing.md
```

### 常用调用

```text
$resume-engineering
根据这个 JD 生成一份 Agent 开发工程师简历，突出 Repo 和 PaperTrail。
```

```text
$resume-engineering
只优化 PaperTrail 项目描述，不生成 PDF。
```

```text
$resume-engineering
把这次测试结果加入证据库，并检查哪些岗位可以使用。
```

## 输入和输出

### 可以提供

- JD 文本、截图、链接或表格；
- 简历母版 YAML/PDF；
- 项目仓库、README、测试报告、论文或部署文档；
- 已确认的职责、指标、项目时间和公开链接。

### 完整生成会得到

1. JD 岗位画像；
2. Direct/Transferable/Adjacent/Gap 证据矩阵；
3. 项目、实习、技能和自我评价文案；
4. 重要改写的前后对比及真实性说明；
5. 未覆盖要求和面试追问；
6. RenderCV YAML、PDF 和一页版式校验结果。

只改几句话时走快速模式，不重复跑项目测试和 PDF 渲染；只有项目事实、JD 或版式发生变化时才做完整校验。

## 真实性和隐私边界

- 不把设计方案写成已经上线的功能；
- 不把固定测试集通过率写成通用模型成功率；
- 不补写没有来源的准确率、用户数和性能收益；
- 不把团队结果全部写成个人贡献；
- 不上传客户敏感信息、个人联系方式、令牌或私人证据库；
- 不照搬他人的简历经历，只借鉴表达结构。

## 参考

- [MIT Resume Writing](https://capd.mit.edu/resources/resumes-writing-about-your-skills/)
- [AgentGuide Resume Guide](https://github.com/adongwanai/AgentGuide/blob/main/docs/04-interview/12-resume-guide.md)
- [ATS Resume Agent](https://github.com/NullSpace-BitCradle/ats-resume-agent)
- [Resume Tailoring Skill](https://github.com/amit-t/skills/tree/main/resume-tailoring)
- [Resume Agent Skills](https://github.com/vignzpie/resume-agent-skills)

这些项目提供了不少好的工程化思路；本 Skill 只借鉴工作流和表达方式，不复制他人的经历或数据。
