# 来源与规则取舍

本 skill 的方法来自三处：课程/讲座的权威意见、两个开源简历项目的可复用机制、以及师门自己的实践沉淀。运行时不依赖任何外部目录，必要方法已落在本仓库。

## 一、来源清单

| 来源 | 采纳内容 | 落地位置 |
| --- | --- | --- |
| 《简历实战写法》PDF（41 页，周凡吟课程）第 9–12、15–21 页 | 岗位准入 / 关键技能 / 隐性要求三层拆解；易读排版、项目至少三分之一、教育倒序、GPA 与核心课程 | `jd-scoring.md`、`content-layout.md` |
| 同 PDF 第 22–27、28–36 页 | 以能力为目标挖掘经历；问题—条件—方法—成效；案例对比、技能具体化、2–3 个岗位关键词、四字提炼 | `writing-rules-zh.md`、`field-playbook.md` |
| 同 PDF 第 37–41 页 | 内推准备、推荐语、信息收集与反馈闭环 | `delivery-and-tracker.md` |
| 求职认知与简历撰写讲座纪要 | 标准模块顺序；项目占至少三分之一；加粗引导；能力趋势而非流水账；求职是匹配不是择优 | `content-layout.md` |
| 第一次简历课个人笔记 | 行动 / 结果导向；写完成度；算法名称准确；AI 项目从用户视角拆解；不突出条数 | `writing-rules-zh.md` |
| 思特奇 HR 简历诊断与求职教学纪要 | **精准投递版 / 海投通用版双轨**；一页 A4、倒序、去自我评价、基本信息完整、避免花哨配色、PDF 投递；文件名规范、3–5 天跟进；AI 交付与 AI 产品等新兴岗位 | `delivery-and-tracker.md`、`field-playbook.md` |
| 银行数据板块负责人分享 | 银行岗位体系与考察点（表达能力、简历真实性、背调）；风控建模的可解释性与指标口径 | `field-playbook.md` |
| Resume-Matcher（srbhr） | 五套 HTML/PDF 模板与三个导出脚本（原样沿用）；**写作 rubric 与确定性检查**（弱开头、破折号、AI 套话、指标缺失、重复开头）；**ATS 五维打分**（关键词 / 技能覆盖 / 标题匹配 / 模块完整 / 日期一致）；改写事实保真校验；页数上限与"两轮写作打磨" | `assets/`、`scripts/check_resume.py`、`scripts/check_pdf.py`、`references/ats-and-layout.md` |
| ai-job-search（ai-job-search-dev） | **准入门槛 / 语言门槛先于打分**；**相关性加权删减**（相关性 / 不重复 / 叙事负荷三维）；页预算表；**进行中学位必须写明**；ATS 文本层检查（日期 ASCII 区间、乱码、阅读顺序、关键词覆盖）；面试回溯测试（stretch 措辞降档）；投递记录与跟进 | `jd-scoring.md`、`ats-and-layout.md`、`delivery-and-tracker.md` |

两个开源项目只借鉴**机制与规则**，代码为按中文简历语境重写，未直接复制其源码文件（模板与导出脚本沿用原有的 resume-master 资源，见文末）。

## 二、课程原始资料位置（仅供追溯）

- `D:/2.临时消息文件/研一/2.实务课纪要和求职经验/写简历的经验与指导/`（PDF、两份 Markdown 纪要）
- `.../思特奇求职教学PPT/会议纪要/`（HR 简历意见、应用统计专业求职指导）
- `.../银行招聘策略、职业发展路径及统计学应用分享/`
- `.../大厂算法面试策略与AI时代职业发展分享/`

PDF 为扫描图片，按页渲染后浏览，关键规则页放大核对。会议实时纪要含助手评论，**不能把评论当作讲师原话**。示例简历中的姓名、联系方式、业绩不作为用户素材。

## 三、规则冲突与取舍

| 冲突 | 取舍 |
| --- | --- |
| 数据规模：教材强调展示规模，个人笔记强调不要突出条数 | 条件规则：能说明复杂度或方法选择时保留，行动与结果优先；不重复出现 |
| 项目占比：教材写"实习/项目合计≥1/3"，纪要有"项目单独 1/3" | 合计为默认下限；项目是主证据时为其单独预留 |
| 别人的工作：笔记写"理解透彻可以写" | 不据此冒领贡献，改写为"复现"或"能解释"，与本人产出分开 |
| 技能：是否删掉 Office | 不机械删也不默认列；由 JD、具体能力与证据决定 |
| 标准顺序 vs 亮点前移 | 默认标准顺序，靠模块内排序与加粗前移亮点；有充分理由才调整模块并写进修改说明 |
| 一页 vs 两页 | 默认一页；有强相关证据且第二页能填满 35% 时才两页；绝不用压字号换页数 |
| 自我评价 | 默认删；银行/国企 JD 明确要求"综合素质"且能写出证据时保留两句 |
| 破折号与日期分隔符 | 正文破折号允许（中文语境），但日期区间统一用 ASCII `-`，避免 ATS 解析失败；`check_resume.py` 会提示 |
| 模拟打分 vs 录取概率 | 五维打分只用于决定"要不要为这岗改简历"，不解释为录取概率，也不对外承诺 |
| AI 自动投递 | **不采用**。ai-job-search 的自动投递/批量抓取不适合本场景：校招平台账号风控严，误投有实际代价。只借其评估与记录机制 |
| AI 生成内容 | 允许 AI 辅助改写，但事实必须可回溯；AI 工具使用本身是加分信息，需能讲清分工 |

## 四、v2 相对 v1 的改动

1. 新增 `references/writing-rules-zh.md`：中文语境的可判定写作规则（弱开头、套话、加粗、量化口径、事实保真、时间状态）。
2. 新增 `references/jd-scoring.md`：三道门槛 + 五维打分 + 证据矩阵 + 隐性能力词典 + 关键词六类。
3. 新增 `references/field-playbook.md`：应用统计/统计学 8 个方向的考察点、条目模板、常见误写、追问题。
4. 新增 `references/ats-and-layout.md`：页数与溢出处理、相关性加权删减、文本层要求、验收流程与故障表。
5. 新增 `references/delivery-and-tracker.md`：精准/通用/银行三版本对照、投递记录、跟进话术、内推推荐语、三层追问链。
6. 重写 `references/content-layout.md`：并入证据底稿表与各模块写法，去掉与其他文件的重复。
7. 升级 `references/experience-report.md`：七段结构保留，补"合格线"与六问最小提问集。
8. 新增 `scripts/check_resume.py`、`scripts/check_pdf.py`：把可机械判定的规则做成可执行检查（占位残留、弱开头、套话、术语错拼、日期格式、项目占比、加粗密度、JD 覆盖、PDF 页数 / 乱码 / 末页填充 / 版心空洞 / 孤立标题）。
9. 新增示例：数据分析与银行风控两份 JD、证据矩阵模板、投递记录 CSV。
10. 五套视觉模板保持不变——现有版式已通过用户验收，不重做设计。
11. 修复 `scripts/render_pdf.py` 的 Chrome 定位：原实现只查 `ProgramFiles` 与 PATH，Chrome 装在用户目录（`%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`，Windows 默认位置）时会直接报 "Chrome not found"。v2 增加了用户级 Chrome 与 Edge 两个候选路径。

## 五、附录：两个上游项目的拆解要点

维护脚本里的词表、阈值或权重时，先看这一节，避免改回已被验证过的问题。

### Resume-Matcher（srbhr，FastAPI + Next.js + SQLite 自托管应用）

| 机制 | 上游位置 | 我们怎么用 |
| --- | --- | --- |
| ATS 五维打分（纯代码，不调模型） | `apps/backend/app/services/ats.py` | 关键词 40% / 技能覆盖 20% / 标题匹配 15% / 模块完整 15% / 日期一致 10%，不可评估维度权重重分配 → 我们只取"关键词覆盖 + 文档完整"两项落进 `check_resume.py`，不对外报"ATS 分" |
| 写作规则可判定化 | `services/writing_quality.py` | 弱开头（HARD −40）、破折号、第一人称、AI 套话、单条过长、无指标（−5）、重复开头（−10）→ `check_resume.py` 的 HARD/SOFT 分级与扣分权重 |
| 改写事实保真 | 同文件 `fact_violations()` | 改写前后对比数字、术语、技能集合，禁止新增或丢失 → `--against` |
| 两轮写作打磨 | `.claude/skills/resume-matcher/SKILL.md` 第 6 步 | 先按 rubric 批判，再只改违规句，评分必须上升 → 主流程第 8 步 |
| ATS 解析回环 | `services/ats_parse/` | 用 pdfminer 把 PDF 读回来查阅读顺序与字段丢失 → `check_pdf.py` 的文本层检查 |
| 页数优先于视觉 | `services/page_fit.py` | 超页压内容不压字号 → `ats-and-layout.md` 的页数策略 |

### ai-job-search（ai-job-search-dev，Claude Code 求职框架）

| 机制 | 上游位置 | 我们怎么用 |
| --- | --- | --- |
| 门槛先于打分 | `.claude/skills/job-application-assistant/04-job-evaluation.md` | 资格 / 语言 / 地点物流为硬门槛，不过不打分不写材料 → `jd-scoring.md` 三道门槛 |
| 相关性加权删减 | `05-cv-templates.md`「Relevance-weighted cutting」 | 按相关性 / 是否重复 / 叙事负荷给每行打分，先砍最低分 → `ats-and-layout.md` |
| 页预算与进行中学位 | 同文件「Page Budget」「In-progress qualifications」 | 各模块条目上限；在读学位必须写明，否则被读成已毕业 → 写作规则第 7 节 |
| ATS 日期 ASCII 区间 | 同文件「Date fields must be ASCII ranges」 | `2016–2024` 会被部分解析器忽略 → `check_resume.py` / `check_pdf.py` 的日期破折号检查 |
| 交付自检阈值 | `tools/verify_layout.py`、`tools/verify_pdf.py` | 版心空洞上限、末页过薄、页底孤立标题的判定方式 → `check_pdf.py` 的 `MAX_GAP_PT=100`、`LAST_PAGE_MIN_FILL=0.60`、页脚带过滤 |
| 面试回溯测试 | `03-writing-style.md`「interview backtrack test」 | 「能否被追问三层而不改口」作为美化与造假的分界 → 写作规则第 10 节 + `delivery-and-tracker.md` 三层追问 |

上游未采纳的部分：Resume-Matcher 的 Web 应用 / 数据库 / MCP server / 模型调用；ai-job-search 的招聘站抓取、批量代投、Gmail/Notion 同步、LaTeX 模板、丹麦站点 CLI。校招平台的账号风控与误投代价决定了这两类能力不适合移植。

