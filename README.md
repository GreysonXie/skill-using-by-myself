# skill-using-by-myself

我自己搜集和改造的 AI skills，用于学习与工作，也欢迎试用并提出改进建议。

| Skill | 用途 | 使用说明 |
| --- | --- | --- |
| [our-resume](our-resume/SKILL.md) | 师门简历工作室：JD 门槛判断与五维打分、中文写作规则、8 个统计方向图谱、三版本投递，五套模板 + 内容/ATS 双层自检脚本 | [安装与使用](our-resume/README.md) |

## 外部 Skill 目录

以下 skill 来自外部项目、社区仓库或 Codex 内置能力，经过本机收集、安装或适配后归档到本仓库；它们不是本仓库自创内容。完整来源说明见 [`SKILLS_INDEX.md`](SKILLS_INDEX.md)。

### 工作流与工程协作

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| ask-matt | 向 Matt 风格的工程工作流提问 | [目录](skills/01-workflow/ask-matt) |
| code-review | 按规范和需求审查代码 | [目录](skills/01-workflow/code-review) |
| codebase-design | 设计更清晰的模块接口 | [目录](skills/01-workflow/codebase-design) |
| diagnosing-bugs | 系统诊断 bug 和性能回归 | [目录](skills/01-workflow/diagnosing-bugs) |
| domain-modeling | 建立术语表、领域模型和 ADR | [目录](skills/01-workflow/domain-modeling) |
| grill-me | 对计划进行温和追问 | [目录](skills/01-workflow/grill-me) |
| grill-with-docs | 结合文档进行结构化追问 | [目录](skills/01-workflow/grill-with-docs) |
| grilling | 压力测试方案和决策 | [目录](skills/01-workflow/grilling) |
| handoff | 整理可交接的工作上下文 | [目录](skills/01-workflow/handoff) |
| implement | 按规格推进实现 | [目录](skills/01-workflow/implement) |
| implement-spec | 编排 agent 完成完整 spec | [目录](skills/01-workflow/implement-spec) |
| improve-codebase-architecture | 改善代码库架构 | [目录](skills/01-workflow/improve-codebase-architecture) |
| pr | 生成便于人工审查的 PR 描述 | [目录](skills/01-workflow/pr) |
| prototype | 快速验证设计或状态模型 | [目录](skills/01-workflow/prototype) |
| retro | 回看 coding 会话并提出改进建议 | [目录](skills/01-workflow/retro) |
| setup-matt-pocock-skills | 配置 Matt Pocock skill 工作流 | [目录](skills/01-workflow/setup-matt-pocock-skills) |
| tdd | 测试驱动开发 | [目录](skills/01-workflow/tdd) |
| to-questionnaire | 把想法转成访谈问题 | [目录](skills/01-workflow/to-questionnaire) |
| to-spec | 把需求整理成实现规格 | [目录](skills/01-workflow/to-spec) |
| to-tickets | 把规格拆成可执行 ticket | [目录](skills/01-workflow/to-tickets) |
| triage | 分类和排序问题或任务 | [目录](skills/01-workflow/triage) |
| wait-what | 在动手前澄清不确定事项 | [目录](skills/01-workflow/wait-what) |
| wayfinder | 在陌生代码库中定位入口 | [目录](skills/01-workflow/wayfinder) |
| wizard | 生成环境操作向导 | [目录](skills/01-workflow/wizard) |
| writing-for-agents | 编写 agent 可执行的文档和指令 | [目录](skills/01-workflow/writing-for-agents) |

### 学习与研究

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| dbs-learning | 把主题拆成连续学习文章 | [目录](skills/02-learning-research/dbs-learning) |
| research | 基于高可信来源开展可追溯研究 | [目录](skills/02-learning-research/research) |
| crawl4ai-research | 用 Crawl4AI 抓取和清洗网页 | [目录](skills/02-learning-research/crawl4ai-research) |
| teach | 用教学式步骤解释复杂主题 | [目录](skills/02-learning-research/teach) |

### 前端与界面

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| frontend-animation-patterns | 选择和实现 UI 动效模式 | [目录](skills/03-frontend-ui/frontend-animation-patterns) |
| ui-ux-pro-max | 设计和评审 Web、移动端、桌面端界面 | [目录](skills/03-frontend-ui/ui-ux-pro-max) |

### 文档与媒体

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| codex-ppt | 从文章、报告或提纲生成 PPT/PPTX | [目录](skills/04-documents-media/codex-ppt) |
| pdf | 阅读、创建、渲染和校验 PDF | [目录](skills/04-documents-media/pdf) |
| playwright | 使用真实浏览器自动化网页流程 | [目录](skills/04-documents-media/playwright) |

### 求职与简历

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| resume-master | 编写 HTML 简历并导出 PDF | [目录](skills/05-career-resume/resume-master) |
| resumify | 把经历改写成简历和面试表达 | [目录](skills/05-career-resume/resumify) |

### 数学建模

| Skill | 用途 | 本仓库路径 |
| --- | --- | --- |
| math-modeling-skill | 覆盖建模分析、代码、可视化和论文交付 | [目录](skills/06-math-modeling/math-modeling-skill) |

已将本机此前收集的 38 个 skill 按用途归档到 [`skills/`](skills/)，完整目录、来源和使用场景见 [`SKILLS_INDEX.md`](SKILLS_INDEX.md)。

归档原则：保留每个 skill 的 `SKILL.md` 及其配套资源；不纳入 Codex 内置 `.system` 技能；`our-resume` 保留在原有根目录以兼容已有资料。

每个 skill 使用独立目录，入口为带 YAML 元数据的 `SKILL.md`，配套资源按 `references/`、`assets/`、`scripts/` 组织。

请通过 [Issues](https://github.com/GreysonXie/skill-using-by-myself/issues) 反馈。分享案例前请移除姓名、电话、邮箱以及企业保密信息。各 skill 的来源与许可范围见其目录内说明。
