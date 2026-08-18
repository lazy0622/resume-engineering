# 证据台账与写作参考

这份参考只在需要维护素材库、核对指标或改写项目 bullet 时读取。它把“我做过什么”与“简历应该怎么写”分开，避免同一项目在不同 JD 中出现互相矛盾的版本。

## 目录

1. [证据台账字段](#1-证据台账字段)
2. STAR/PAR+Tech、XYZ 与设计取舍
3. [指标口径](#3-指标口径)
4. [Agent 能力分层](#4-agent-能力分层)
5. [项目素材索引](#5-项目素材索引)
6. [JD → 素材匹配示例](#6-jd--素材匹配示例)
7. [双轮审阅](#7-双轮审阅)
8. [参考来源与使用边界](#8-参考来源与使用边界)

## 1. 证据台账字段

每条可写主张至少记录：

```yaml
- project: Repo Coding Runtime
  claim: "RepoRuntimeBench 固定任务 24/24 通过"
  category: result                 # architecture | mechanism | result | scope | collaboration
  status: verified                 # verified | historical | proposed | unknown
  source: "benchmarks/reporuntimebench/results/v3-evaluation-summary.md"
  verification: "pytest/报告命令、提交或日期"
  metric:
    value: "24/24"
    baseline: null
    unit: "固定回归任务"
    environment: "固定夹具/本地"
  interview_followups:
    - "为什么不是通用模型成功率？"
    - "失败任务如何恢复？"
  allowed_phrasing: "固定回归任务 24/24 通过"
  forbidden_phrasing: "Coding Agent 通用成功率 100%"
```

推荐将事实分为五类：

1. **架构**：模块边界、状态机、数据流和职责。
2. **机制**：为什么选择某种实现，解决了什么失败模式或成本。
3. **工程质量**：幂等、重试、超时、隔离、鉴权、审计、可观测。
4. **结果**：测试数、前后对比、数据集协议、延迟、拦截/泄漏等。
5. **范围与限制**：本地、固定夹具、官方 preflight、历史实验、未覆盖项。

### 长期职业证据库

将简历母版视为展示文件，将证据库视为长期 source of truth。证据库可以是 YAML/Markdown，至少保留以下分区：

```text
定位与目标岗位
教育/论文/奖项/公开作品
实习与项目卡片
成就与指标池
技术能力与熟练边界
已知缺口（Known Gaps）
已批准的保守表述（Approved Framings）
面试追问与回答证据
版本/日期/来源
```

每次新增功能、测试结果或论文实验时，先更新证据库，再生成定向简历。不要把个人联系方式、未脱敏客户信息或令牌写进公共仓库；私密台账放在用户指定的本地路径。

## 2. STAR/PAR+Tech、XYZ 与设计取舍

不要在简历中完整讲故事，而要把故事压缩到一条能被追问的工程事实：

```text
项目简介 = 使用场景 + 业务/工程痛点 + 系统闭环
核心 bullet = 动作 + 机制/取舍 + 结果/边界
```

### 弱写法与强写法

| 弱写法 | 强写法 |
|---|---|
| 熟悉 LangGraph、Qdrant、RAG | 基于 LangGraph 编排 claim 拆分、证据分级与报告生成，持久化 sources/evidence_items 以支持调研复盘 |
| 实现了一个 Coding Agent | 实现 AgentLoop、Supervisor/TaskGraph 和 Checkpoint/Resume，打通任务规划、工具调用、验证和失败恢复 |
| 提升了检索准确率 | 在固定 QA 集和指定 Retrieval Matrix 下对比 Recall/MRR；未产生真实结果时只写“支持评测与 Bad Case 分析” |
| 系统已生产上线，服务很多用户 | 基于 FastAPI 构建可恢复异步 ingestion；若没有部署与用户证据，不使用“生产/用户数” |

### XYZ 结果句式

当已有可靠指标时，用下面的压缩方式强化结果：

```text
完成/改善 X，结果达到 Y，通过 Z 实现。
```

示例：

- `将固定回归通过率由 23/24 提升至 24/24，通过 ExecutionPolicy 限制高风险工具调用并补齐失败恢复路径。`
- `在 NTU RGB+D 60 的 X-Sub 协议上由 89.71% 提升至 90.96%，通过轻量时序交互与语义引导判别增强改善细粒度类别边界。`

没有基线、样本或环境时，不写“提升百分比”；改写为“支持评测”“覆盖某类状态”“接入某项 preflight”。不要把 XYZ 当作制造数字的模板。

### 句式模板

- `面向【场景】中的【问题】，设计/实现【系统或模块】，通过【关键机制】完成【闭环】，在【环境/口径】下达到【结果】。`
- `构建【组件】，支持【能力 A/B/C】；用【幂等/重试/隔离/审计机制】处理【失败模式】，并以【测试/报告/指标】验证。`
- `将【输入】经过【解析/检索/决策】流转到【输出】，保留【证据/Trace/版本】以支持【复盘、回滚或评测】。`

### 设计取舍与失败模式

Agent、RAG 和后端项目至少挑一条 bullet 说明一个真实取舍：

- 为什么选择 Hybrid Search 而不是只做向量检索；
- 为什么采用 SQLite WAL、任务租约、幂等键或原子替换；
- 为什么使用 Checkpoint、Worktree、Docker 沙盒或人工审批；
- 哪种失败会触发重试、回滚、降级或人工介入。

只写能由代码、测试或设计文档解释的取舍；没有证据时写“支持/设计”，不要写成已验证的性能收益。

### 匹配置信度

对每项 JD 要求使用四级匹配，避免用一个总分掩盖缺口：

| 标签 | 含义 | 简历处理 |
|---|---|---|
| Direct | 直接做过且有来源 | 放入核心 bullet，可使用已验证结果 |
| Transferable | 机制相同、场景不同 | 用迁移能力表述，避免写成同一业务经验 |
| Adjacent | 只覆盖相邻知识或部分实现 | 放技能/补充经历，必要时加边界 |
| Gap | 没有证据或只有计划 | 不写成掌握，列入学习/面试补强 |

同时记录 `confidence: high/medium/low`。低置信度要求优先追问，用户未补证据时保守输出。

## 3. 指标口径

按可信度使用指标：

1. 当前代码和自动化测试可复现的固定结果。
2. 当前仓库报告中写明环境、样本、命令和日期的实验结果。
3. 用户明确提供且能解释口径的历史项目结果。
4. 仅有设计目标或推测的结果：不写成成绩，改为“支持/设计/计划验证”。

常见限定词：`固定夹具下`、`本地测试集`、`官方 preflight`、`NTU RGB+D X-Sub 协议`、`历史实验结果`。把限定词放在数字附近，避免读者误解为线上或通用指标。

禁止把以下不同概念混写：

- Harness 固定任务通过率 ≠ 通用模型成功率 ≠ SWE-bench solve rate。
- 安全场景拦截率 ≠ 完整渗透测试结论。
- 单元测试通过 ≠ 生产部署成功。
- 论文数据集 Top-1 ≠ 线上业务准确率。
- 已实现代码 ≠ 设计文档中的计划功能。

## 4. Agent 能力分层

将素材按能力层级整理，避免项目只停留在框架名：

| 层级 | 面试官想确认什么 | 当前候选人可用证据 |
|---|---|---|
| 基础调用 | 是否理解 Tool、RAG、API 和 Prompt | Tool Calling、Hybrid Search、模型 API |
| 系统实现 | 是否能设计 Agent 状态和工作流 | AgentLoop、TaskState、Supervisor/TaskGraph、LangGraph |
| 高级机制 | 是否处理上下文、检索和复杂任务 | Checkpoint、Query Rewrite、Rerank、证据分级、RepoIndex |
| 生产工程 | 是否能稳定、安全、可评测地运行 | 重试、幂等、沙盒、权限、审计、Trace、评测集 |

Agent/Harness 简历至少覆盖“系统实现 + 生产工程”；RAG 简历至少覆盖“检索链路 + 入库/评测”；CV/深度学习简历至少覆盖“方法 + 数据集 + 消融”。

## 5. 项目素材索引（当前候选人）

### Repo Coding Runtime

将以下内容按 Harness/Agent/后端 JD 重新组合，而不是每次全部照抄：

- Runtime：AgentLoop、TaskState、ExecutionPolicy、Supervisor/TaskGraph、状态迁移、事件。
- Repo：RepoIndex v3、AST/符号/引用/依赖、Python CallRecord、related tests、confidence/diagnostics。
- 修改闭环：研究、证据汇总、Patch 预览、严格 Diff、文件指纹、测试验证、冲突感知回滚。
- 治理与安全：ToolRegistry/ToolGateway、Schema、风险分级、人工审批、脱敏、Trace、Git Worktree、MCP stdio。
- 执行与评测：Host/Docker 沙盒、无网络、非 root、只读根、allowlist、资源/超时清理、RepoRuntimeBench、隐藏 Verifier、CI。
- 可写结果：固定回归 `24/24`；策略消融 `23/24 → 24/24`；固定安全集拦截 `100%`、误拦截 `0%`、泄漏 `0%`。SWE-bench 没有 solve rate 时只写“接入官方 Docker preflight”。

### PaperTrail

- 数据链路：PDF/DOCX/Markdown/TXT，按页 chunk，document_title/section 元数据，contextual embedding。
- 检索链路：OpenAI-compatible Chat/Embedding，Qdrant dense+sparse/IDF，RRF，关键词规则重排，可选 Cross-Encoder，兼容旧 dense 索引。
- 可靠入库：FastAPI 异步 job，queued/running/retrying/succeeded/failed，SQLite WAL、atomic claim、worker lease、retry/restart recovery、content_hash/index_version、索引原子替换。
- 研究 Agent：Query Rewrite、LangGraph 规划、claim 拆分、证据分级、摘要、方法对比、overclaim check、Markdown 报告、tool_calls/sources/evidence_items。
- 评测：20 条 QA、Ground Truth、五档 Retrieval Matrix、Precision/Recall/MRR/Token F1/P95 的评测接口、Rule/Cross-Encoder A/B、Bad Case、run manifest、Trace、可选 Semantic Judge；本地测试数字以当前报告为准（已确认过的版本为 37 项通过）。

### Hongyang 实习

- 企业场景：高安全等级企业的本地化部署与权限隔离。
- 平台能力：统一认证/组织同步、用户/部门/角色/自定义组、用户与文件密级、知识库读写/管理/检索过滤、助理门户与发布、操作/召回/向量化/智能链/API 审计、裸机服务与 systemd。
- Agent 相关：AgentRuntimeContext、ToolPolicy、Tool Gateway、密级路由、审批/恢复等仅在代码和测试已确认时写“实现/负责”；只有方案时写“设计/规划”。

### LTE-SGDE 论文

- 主题：细粒度骨架动作识别、轻量时序建模、语义引导判别增强、NTU RGB+D 60/120。
- 真实结果：NTU60 X-Sub `89.71→90.96`、X-View `95.29→95.66`；NTU120 X-Sub `85.88→86.26`、X-Set `87.04→87.46`。
- 只在 CV/深度学习/时序 JD 中使用；将结果标记为论文实验，不改写为产品指标。

## 6. JD → 素材匹配示例

| JD重点 | 首选项目 | 取用素材 |
|---|---|---|
| Agent Runtime/Harness、失败恢复、工具治理 | Repo | Loop/State、TaskGraph、Checkpoint、ToolGateway、沙盒、Trace、24/24 |
| RAG、论文问答、评测、引用 | PaperTrail | 解析、Hybrid Search、Rerank、引用、入库恢复、20 QA/Matrix |
| AI 平台、模型网关、后端工程 | Hongyang + PaperTrail | 权限/密级/审计/部署 + FastAPI/异步/重试/模型 API |
| Python 后端 | PaperTrail + Repo | FastAPI、SQLite WAL、任务状态、重试、Docker、pytest |
| CV/深度学习/时序 | LTE-SGDE + 相关 Agent 项目 | 模块、实验协议、消融和 NTU 指标；Agent 项目只作工程补充 |

## 7. 双轮审阅

### HR/ATS 轮

- 岗位标题是否与 JD 完全一致；
- 首屏是否能看到目标方向、核心项目和关键技术；
- P0 职责与 P1 技术是否在项目上下文中出现；
- 是否存在关键词堆砌、过长句子、无关项目或重复内容。

### 技术面试轮

- 每条主张能否追问出架构、数据流和个人边界；
- 能否解释关键设计取舍和失败处理；
- 每个指标是否能说明基线、样本、环境和验证命令；
- 是否明确区分已实现、历史实验、设计方案和未覆盖项。

只有两轮都通过，才把文案放进正式 PDF；否则把问题加入“待补证据/面试补强清单”。

## 7.1 输出契约与常用触发

完整定向生成至少输出：

1. JD 岗位画像和共同/独有要求；
2. Direct/Transferable/Adjacent/Gap 证据矩阵及置信度；
3. 最终项目、经历、技能和自我评价文案；
4. 关键改写的 before/after 与真实性说明；
5. 未覆盖要求、面试追问、生成文件和版式校验结果。

常用触发句：

```text
根据这个 JD 生成一页 Agent/RAG/Python 后端简历
只优化 Repo/PaperTrail 项目描述，不生成 PDF
把新的测试结果加入简历证据库
检查这份 RenderCV 简历的 ATS 和技术面试风险
```

单个 JD 走快速匹配；多个 JD 先抽取共同要求，再分别生成版本，必要时共用一次补证据访谈。

## 8. 参考来源与使用边界

把公开资源用于学习结构和表达，不复制他人的经历或数字：

- [MIT Career Toolkit](https://capd.mit.edu/resources/career-toolkit-crafting-an-effective-resume/)：相关性、行动动词、结果和简洁表达。
- [LLM-Resume-Template](https://github.com/adongwanai/LLM-Resume-Template)：背景/痛点 → 技术方案 → 结果的项目结构。
- [AgentGuide](https://github.com/adongwanai/AgentGuide)：Agent 的 Tool、Controller、Memory/Context、评测和面试追问维度。
- [ATS-optimized-resume-agent-skill](https://github.com/SankaiAI/ats-optimized-resume-agent-skill)：master profile/evidence → JD 匹配 → 定向草稿 → ATS/渲染校验。
- [ats-resume-agent](https://github.com/NullSpace-BitCradle/ats-resume-agent)：Master Career Document、引导式经历访谈、按 JD 选取证据和零编造约束。
- [resume-tailoring](https://github.com/amit-t/skills/tree/main/resume-tailoring)：canonical trigger、Direct/Transferable/Adjacent/Impact 匹配、coverage report 和 before/after 真实性说明。
- [resume-agent-skills](https://github.com/vignzpie/resume-agent-skills)：长期 career profile、Known Gaps、Approved Framings 以及“profile 是资产、简历是衍生物”的工作流。
- [Awesome-CV](https://github.com/posquit0/Awesome-CV)：只借鉴版式，不照搬内容。
- 牛客、抖音、小红书的 Agent 简历分享：用于观察面试追问和关键词表达；优先以代码、测试、论文和官方 JD 验证事实。
