# our-resume · 我们的简历工作室

面向实习、校招和转岗：把真实经历整理为目标岗位的能力证据，输出可编辑 HTML、可打印 PDF，或单独生成七段经历提炼报告。

## 安装

克隆本仓库，将整个 `our-resume` 文件夹复制到你的 Codex skills 目录：设置了 `CODEX_HOME` 时为其下的 `skills/`，否则为用户目录下的 `.codex/skills/`。不要只复制 `SKILL.md`；同名目录已存在时先备份。

```bash
git clone https://github.com/GreysonXie/skill-using-by-myself.git
```

完成后在支持 skill 的客户端选择 `our-resume`。未立即出现时重新打开会话。其他支持 SKILL.md 的工具可按照各自的 skill 安装规则复制同一目录；未逐个平台测试兼容性。

仅做文字提炼不需要 Python。自动导出和检查 PDF 时，需要 Python 3.10+、Google Chrome，以及以下依赖（建议在虚拟环境中安装）：

```bash
python -m pip install -r requirements.txt
```

以上命令在 `our-resume` 目录执行。Chrome 不能自动识别时，给导出脚本传入 `--chrome` 可执行文件路径。

## 使用

```text
用 $our-resume，结合我的旧简历和以下 JD 修改简历，保留现有风格。
```

```text
用 $our-resume，帮我把这段实习整理成七段提炼报告。
目标岗位：数据分析。实际工作：……
```

```text
用 $our-resume，以极简纯白模板制作简历。以下是我的真实经历：……
```

有 JD 就提供 JD；没有时可先制作目标岗位通用稿。未知指标会进入待核实清单，不会自动编造成果。

## 五套模板

模板源文件、PDF 和图片全部保留在 `assets/template_refs/`。内容顺序与篇幅依据经历和岗位调整，模板示例不是用户事实。

| 模板 | 预览 | PDF |
| --- | --- | --- |
| 典雅酒红 | [图片](assets/template_refs/images/典雅酒红.png) | [PDF](assets/template_refs/pdf/典雅酒红.pdf) |
| 极客风尚 | [图片](assets/template_refs/images/极客风尚.png) | [PDF](assets/template_refs/pdf/极客风尚.pdf) |
| 极简纯白 | [图片](assets/template_refs/images/极简纯白.png) | [PDF](assets/template_refs/pdf/极简纯白.pdf) |
| 沉稳双栏 | [图片](assets/template_refs/images/沉稳双栏.png) | [PDF](assets/template_refs/pdf/沉稳双栏.pdf) |
| 清新蓝灰 | [图片](assets/template_refs/images/清新蓝灰.png) | [PDF](assets/template_refs/pdf/清新蓝灰.pdf) |

## 工作方式

1. 提取 JD 的准入要求、关键技能和隐性能力，建立证据映射。
2. 挖掘本人行动、方法选择、产出与完成度，选取最相关经历。
3. 按标准板块组织，实习/项目合计至少约三分之一版面。
4. 保留视觉风格，生成 HTML/PDF 并逐页检查。

默认一页，但不会为了凑页数编造经历或压缩到难以阅读。没有量化结果时可写真实交付物与验证状态。

七段报告保留：核心定位、简历版、面试口述版、STAR 亮点、核心亮点提炼、岗位适配建议、诚实警告。

## 手动导出

在 skill 目录运行（将文件名替换成实际路径）：

```bash
python scripts/render_pdf.py --in resume.html --out resume.pdf --paper A4
python scripts/pdf_page_count.py --in resume.pdf
python scripts/pdf_to_images.py --in resume.pdf --outdir preview
```

导出失败时可用浏览器打开 HTML 并打印为 PDF。检查输出是否裁切、乱码或产生空白尾页。

## 反馈与迭代

请到 [Issues](https://github.com/GreysonXie/skill-using-by-myself/issues/new) 提交：

- 目标岗位、使用的 AI 工具及模板；
- 脱敏后的原始材料与使用提示词；
- 实际输出、期望效果和具体问题；
- 如为排版问题，附脱敏截图与导出环境。

当前已检查 skill 结构、内部引用和原模板/脚本一致性；尚未完成跨平台及所有模板的端到端导出测试。欢迎使用反馈后继续改进。

## 来源

本 skill 改编自 resume-master、resumify，并结合简历课程方法。详见 [第三方声明](THIRD_PARTY_NOTICES.md) 和 [来源与规则取舍](references/source-decisions.md)。
