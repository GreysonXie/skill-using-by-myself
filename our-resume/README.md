# our-resume · 我们的简历工作室

面向应用统计 / 统计学方向的实习、校招与转岗：把真实经历整理为目标岗位的**能力证据**，输出可编辑 HTML 与可打印 PDF，也可单独生成七段经历提炼报告。

v2 在原有五套模板与导出脚本之上，加了四类判断能力：

1. **投前判断**：三道硬门槛（资格 / 语言 / 到岗）+ 五维打分 + 证据矩阵，决定这个岗值不值得为它改简历。
2. **可判定写作规则**：弱开头、中文套话、加粗密度、量化口径、事实保真、在读状态，都有明确判定标准。
3. **方向适配**：数据分析、风控建模、BI/数据开发、业务算法、AI 产品与交付、市场研究、政府统计、医药统计 8 个方向的考察点与条目模板。
4. **双层自检脚本**：内容规则（`check_resume.py`）与 PDF/ATS（`check_pdf.py`），输出 HARD / SOFT / INFO 与 0–100 分。

## 安装

克隆本仓库，将整个 `our-resume` 文件夹复制到你的 Codex skills 目录：设置了 `CODEX_HOME` 时为其下的 `skills/`，否则为用户目录下的 `.codex/skills/`。不要只复制 `SKILL.md`；同名目录已存在时先备份。

```bash
git clone https://github.com/GreysonXie/skill-using-by-myself.git
```

完成后在支持 skill 的客户端选择 `our-resume`。未立即出现时重新打开会话。其他支持 `SKILL.md` 的工具可按各自的安装规则复制同一目录；未逐个平台测试兼容性。

仅做文字提炼不需要 Python。自动导出与自检需要 Python 3.10+、Google Chrome（或 Edge），以及以下依赖（建议在虚拟环境中安装）：

```bash
python -m pip install -r requirements.txt
```

> v2 修复了一处 Windows 上的导出问题：Chrome 默认装在 `%LOCALAPPDATA%\Google\Chrome\Application\`，原脚本只查 `ProgramFiles` 与 PATH 会报 "Chrome not found"。现在会自动识别用户级 Chrome 与 Edge；仍识别不到时可传 `--chrome` 指定路径。

## 使用

```text
用 $our-resume，结合我的旧简历和下面这份 JD 改简历，保留现有风格。
（粘贴 JD）
```

```text
用 $our-resume，先按这份 JD 判断值不值得投，再做证据矩阵。
```

```text
用 $our-resume，帮我把这段实习整理成七段提炼报告。
目标岗位：数据分析。实际工作：……
```

```text
用 $our-resume，以极简纯白模板制作简历。以下是我的真实经历：……
```

有 JD 就提供 JD；没有时可先做目标岗位通用稿，并在交付说明里标明"尚未针对具体 JD"。未知指标会进入待核实清单，不会自动编造成果。

## 目录

```
our-resume/
├── SKILL.md                         # 九步主流程 + 完成标准 + 边界
├── references/
│   ├── content-layout.md            # 写什么、放哪里：证据底稿、模块写法、版面比例
│   ├── writing-rules-zh.md          # 中文写作规则：句式、弱开头、套话、加粗、量化、事实保真
│   ├── jd-scoring.md                # 三道门槛 + 五维打分 + 证据矩阵 + 隐性能力词典
│   ├── field-playbook.md            # 应用统计 8 个方向的考察点与条目模板
│   ├── ats-and-layout.md            # 页数与删减、文本层要求、验收流程、故障表
│   ├── delivery-and-tracker.md      # 三版本、投递记录、跟进话术、内推推荐语
│   ├── experience-report.md         # 七段提炼报告 + 六问最小提问集
│   └── source-decisions.md          # 来源清单、规则冲突取舍、版本变更
├── scripts/
│   ├── render_pdf.py                # HTML → PDF（Chrome/Edge headless）
│   ├── check_resume.py              # 内容规则自检
│   ├── check_pdf.py                 # PDF / ATS 自检
│   ├── pdf_page_count.py            # 页数
│   └── pdf_to_images.py             # 逐页 PNG
└── assets/
    ├── template_refs/               # 五套 HTML / PDF / PNG 模板
    └── examples/                    # JD 示例、证据矩阵模板、投递记录 CSV
```

## 脚本

```bash
# 内容自检（HTML / Markdown / 纯文本均可）
python scripts/check_resume.py resume.html --jd jd.txt

# 导出 PDF
python scripts/render_pdf.py --in resume.html --out resume.pdf --paper A4

# 交付自检：页数 / 乱码 / 文本层联系信息 / 日期破折号 / 末页填充 / 版心空洞 / 孤立标题
python scripts/check_pdf.py resume.pdf --expect-pages 1 --jd jd.txt

# 逐页看图
python scripts/pdf_to_images.py --in resume.pdf --outdir preview

# 改写前后对比，检查数字与术语是否漂移
python scripts/check_resume.py new.html --against old.html
```

`check_resume.py` 会检查：模板占位残留、弱开头（负责/参与/协助…）、中文套话、术语错拼（`xgboost`/`tableau`…）、日期格式混用、项目经历文字占比、加粗密度、JD 关键词覆盖、改写前后的事实增删。`--skip-contact` 用于只检查经历片段，`--json` 供程序消费，`--strict` 在有 HARD 问题时返回非零退出码。

`check_pdf.py` 的版心空洞、末页填充、孤立标题检测依赖 PyMuPDF；未安装时自动跳过几何检查。

## 五套模板

模板源文件、PDF 与预览图全部保留在 `assets/template_refs/`。内容顺序与篇幅依据经历和岗位调整，模板示例人物与数字**不是**用户事实。

| 模板 | 预览 | PDF |
| --- | --- | --- |
| 典雅酒红 | [图片](assets/template_refs/images/典雅酒红.png) | [PDF](assets/template_refs/pdf/典雅酒红.pdf) |
| 极客风尚 | [图片](assets/template_refs/images/极客风尚.png) | [PDF](assets/template_refs/pdf/极客风尚.pdf) |
| 极简纯白 | [图片](assets/template_refs/images/极简纯白.png) | [PDF](assets/template_refs/pdf/极简纯白.pdf) |
| 沉稳双栏 | [图片](assets/template_refs/images/沉稳双栏.png) | [PDF](assets/template_refs/pdf/沉稳双栏.pdf) |
| 清新蓝灰 | [图片](assets/template_refs/images/清新蓝灰.png) | [PDF](assets/template_refs/pdf/清新蓝灰.pdf) |

## 工作方式

1. 建事实底稿：已知 / 待核实 / 缺口三栏，只有前两档进正式稿。
2. 定版本：通用版 / 精准版 / 银行国企版。
3. 过门槛、打分：不过门槛不改简历；打分 < 15 建议用通用版。
4. 填证据矩阵：每条 JD 要求对到证据与位置，缺口单列。
5. 访谈挖细节：每轮 1–3 个关键问题，问到能答三层（事实 / 方法 / 结果）。
6. 出文字初稿，再进 HTML；保留模板视觉，按内容规则重排模块与篇幅。
7. 导出 + 双层自检 + 逐页看图。
8. 换两个视角复核（HR 8 秒 / 技术面试官三层追问）。
9. 交付 HTML、PDF、修改说明与待补清单；需要时给投递记录与跟进话术。

默认一页；有强相关证据且第二页能填满 35% 时才两页。不会为凑页数编造经历，也不会压缩到难以阅读。没有量化结果时写真实交付物、使用方与完成度。

## 验证情况

| 检查 | 结果 |
| --- | --- |
| 合格样本（一页数据分析版） | 96/100，HARD 0，项目文字占比 67%，加粗 12% |
| 同一样本重新导出并自检 | 1 页，末页填充 92%，文本层无乱码，JD 覆盖 40% |
| 两页样本 | 96/100，2 页，末页填充 94% |
| 构造的问题样本 | 14/100，HARD 8（占位、弱开头 ×2、术语错拼 ×5），SOFT 7 全部命中 |

## 反馈与迭代

请到 [Issues](https://github.com/GreysonXie/skill-using-by-myself/issues/new) 提交：

- 目标岗位、使用的 AI 工具及模板；
- 脱敏后的原始材料与提示词；
- 实际输出、期望效果与具体问题；
- 排版问题请附脱敏截图与导出环境。

欢迎指出规则过严或漏判的例子——脚本里的词表与阈值都在 `scripts/` 顶部，可直接改。

## 来源

本 skill 的模板与导出脚本改编自 resume-master，七段提炼结构参考 resumify，规则结合课程方法、Resume-Matcher 与 ai-job-search 的公开机制重写。详见 [第三方声明](THIRD_PARTY_NOTICES.md) 与 [来源与规则取舍](references/source-decisions.md)。
