#!/usr/bin/env python3
"""PDF 交付自检：页数、文本层可解析性、日期破折号、关键词覆盖、末页与分页质量。

用法：
    python scripts/check_pdf.py out/resume.pdf
    python scripts/check_pdf.py out/resume.pdf --jd assets/examples/jd.example.txt
    python scripts/check_pdf.py out/resume.pdf --expect-pages 1 --strict
    python scripts/check_pdf.py out/resume.pdf --json

依赖：pypdf（必需，`pip install pypdf`）；pymupdf（可选，`pip install pymupdf`，装了才会做
页面几何检查：末页填充率、版心大空洞、页底疑似孤立标题）。

退出码：0 正常；1 存在 HARD 问题（配合 --strict 在流水线里卡关）；2 环境或参数问题。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# 与 check_resume.py 保持同一套词表/判定口径
from check_resume import TERM_ALIASES, TERM_LEXICON

NON_ASCII_DASH = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
_DATE_TOKEN = r"(?:(?:19|20)\d{2}(?:\s*[.\-/年]\s*\d{1,2}\s*月?)?|\d{1,2}\s*月|至今|今|Present|present)"
YEAR_DASH_RE = re.compile(rf"{_DATE_TOKEN}\s*[{NON_ASCII_DASH}]\s*{_DATE_TOKEN}")
GARBLE_RE = re.compile(r"\(cid:\d+\)|\ufffd|[\u25a1\u25a0]{2,}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_RE = re.compile(r"1[3-9]\d{9}")

# 首页若只剩这么点字符，基本是空页/渲染失败
MIN_CHARS_PER_PAGE = 60
# 末页正文底部不到页高的这个比例，读作"没写完"
LAST_PAGE_MIN_FILL = 0.60
# 相邻内容块之间的垂直间隙超过这个值，读作版心空洞（A4 高 842pt，约 3.5 行）
MAX_GAP_PT = 100.0
# 页底最后一块比正文中位字号大这个倍数，读作孤立标题
ORPHAN_SIZE_RATIO = 1.12


@dataclass
class Finding:
    rule: str
    severity: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add(self, rule: str, severity: str, message: str) -> None:
        self.findings.append(Finding(rule, severity, message))

    def by(self, severity: str) -> list[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def score(self) -> int:
        return max(0, round(100 - 10.0 * len(self.by("hard")) - 4.0 * len(self.by("soft")) - 0.5 * len(self.by("info"))))


def read_pages_pypdf(pdf: Path) -> list[str]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    return [(page.extract_text() or "") for page in reader.pages]


def page_geometry(pdf: Path) -> list[dict] | None:
    """用 pymupdf 拿每页的文本块几何；没装 pymupdf 就返回 None。"""
    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            return None

    doc = pymupdf.open(str(pdf))
    pages: list[dict] = []
    for page in doc:
        height = page.rect.height
        blocks = []
        sizes: list[float] = []
        for x0, y0, x1, y1, text, _no, btype in page.get_text("blocks"):
            if btype != 0 or not text.strip():
                continue
            blocks.append({"y0": y0, "y1": y1, "text": text.strip()})
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        sizes.append(span["size"])
        blocks.sort(key=lambda b: b["y0"])
        pages.append({"height": height, "blocks": blocks, "sizes": sizes})
    doc.close()
    return pages


def check_pages_geometry(pages: list[dict], report: Report) -> None:
    if not pages:
        return
    # 末页填充率
    last = pages[-1]
    if last["blocks"]:
        bottom = max(b["y1"] for b in last["blocks"])
        fill = bottom / last["height"]
        report.stats["last_page_fill"] = round(fill, 3)
        if fill < LAST_PAGE_MIN_FILL:
            report.add(
                "thin_last_page",
                "soft",
                f"末页内容只占页高 {fill:.0%}：补一条真实证据，或删减后压回一页",
            )
    # 版心空洞
    holes = 0
    worst = 0.0
    for page in pages:
        blocks = page["blocks"]
        for prev, cur in zip(blocks, blocks[1:]):
            gap = cur["y0"] - prev["y1"]
            if gap > MAX_GAP_PT:
                holes += 1
                worst = max(worst, gap)
    if holes:
        report.stats["layout_holes"] = holes
        report.add(
            "layout_hole",
            "soft",
            f"{holes} 处版心空洞（最大 {worst:.0f}pt，约 {worst / 24:.0f} 行）：调间距或补内容，别让页面显得断开",
        )
    # 页底孤立标题（非末页）
    for i, page in enumerate(pages[:-1], 1):
        height = page["height"]
        # 页脚（页码、"姓名 · 1 / 2"）落在底部边距里，不能当作正文最后一块
        blocks = [
            b for b in page["blocks"]
            if b["y0"] < height * 0.90 and not re.search(r"\d+\s*/\s*\d+", b["text"])
        ]
        if not blocks:
            continue
        tail = blocks[-1]
        if len(tail["text"]) <= 30 and tail["text"][-1:] not in "。；;.":
            report.add(
                "orphan_heading",
                "soft",
                f"第 {i} 页最后一块疑似孤立标题（「{tail['text'][:20]}」），它的条目翻到了下一页",
            )


def check_text_layer(texts: list[str], report: Report, expect_pages: int | None, jd_text: str | None) -> None:
    pages = len(texts)
    report.stats["pages"] = pages
    if expect_pages is not None and pages != expect_pages:
        report.add(
            "page_count",
            "hard" if pages > expect_pages else "soft",
            f"页数 {pages}，期望 {expect_pages}：溢出就按相关性加权删减，不要压字号压边距",
        )
    for i, text in enumerate(texts, 1):
        if len(text.strip()) < MIN_CHARS_PER_PAGE:
            report.add("empty_page", "hard", f"第 {i} 页文本层几乎为空（{len(text.strip())} 字符）：渲染失败或被图片替代")
        if GARBLE_RE.search(text):
            report.add(
                "garbled_text",
                "hard",
                f"第 {i} 页出现 (cid:xx) / 替换字符 / 方框：字体缺 Unicode 映射，ATS 读到的是乱码",
            )

    joined = "\n".join(texts)
    if not EMAIL_RE.search(joined):
        report.add("contact_email", "hard", "文本层没有邮箱：网申系统读不到，必须作为可复制文本出现")
    if not PHONE_RE.search(joined):
        report.add("contact_phone", "info", "文本层没有大陆手机号，投国内岗位请补上")

    if YEAR_DASH_RE.search(joined):
        sample = YEAR_DASH_RE.search(joined)
        report.add(
            "date_dash",
            "soft",
            f"文本层日期区间含非 ASCII 破折号（如「{sample.group(0) if sample else ''}」）；部分 ATS 解析日期失败",
        )

    if jd_text:
        jd_low = jd_text.lower()
        resume_low = joined.lower()
        wanted: list[str] = []
        for term in TERM_LEXICON:
            if any(c.lower() in jd_low for c in TERM_ALIASES.get(term, (term,))) and term not in wanted:
                wanted.append(term)
        hit = [t for t in wanted if any(c.lower() in resume_low for c in TERM_ALIASES.get(t, (t,)))]
        miss = [t for t in wanted if t not in hit]
        if wanted:
            coverage = len(hit) / len(wanted)
            report.stats["jd_coverage"] = round(coverage, 3)
            report.stats["jd_miss"] = miss
            if coverage < 0.5:
                report.add(
                    "jd_coverage",
                    "soft",
                    f"文本层 JD 关键词覆盖 {coverage:.0%}：缺 {', '.join(miss[:10])}（只补有证据的）",
                )


def print_report(pdf: Path, report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(
            {"file": str(pdf), "score": report.score(), "stats": report.stats,
             "findings": [f.__dict__ for f in report.findings]},
            ensure_ascii=False, indent=2,
        ))
        return
    print(f"PDF 自检：{pdf.name}")
    print(f"综合评分：{report.score()}/100（HARD {len(report.by('hard'))}｜SOFT {len(report.by('soft'))}｜INFO {len(report.by('info'))}）")
    st = report.stats
    bits = []
    if "pages" in st:
        bits.append(f"{st['pages']} 页")
    if "last_page_fill" in st:
        bits.append(f"末页填充 {st['last_page_fill']:.0%}")
    if "jd_coverage" in st:
        bits.append(f"JD 覆盖 {st['jd_coverage']:.0%}")
    if bits:
        print("统计：" + "｜".join(bits))
    print()
    for sev, label in (("hard", "HARD"), ("soft", "SOFT"), ("info", "INFO")):
        items = report.by(sev)
        if not items:
            continue
        print(f"[{label}] {len(items)} 项")
        for f in items:
            print(f"  - {f.message}")
        print()
    if not report.findings:
        print("未发现规则问题。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PDF 交付自检")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--jd", type=Path, help="JD 文本文件，检查文本层关键词覆盖")
    parser.add_argument("--expect-pages", type=int, help="期望页数，例如 1")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="存在 HARD 问题时退出码 1")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.pdf.exists():
        print(f"找不到 PDF：{args.pdf}", file=sys.stderr)
        return 2
    try:
        texts = read_pages_pypdf(args.pdf)
    except ImportError:
        print("缺少依赖 pypdf：pip install pypdf", file=sys.stderr)
        return 2
    except Exception as exc:  # 损坏或加密
        print(f"无法读取 PDF：{exc}", file=sys.stderr)
        return 2

    jd_text = None
    if args.jd:
        if not args.jd.exists():
            print(f"找不到 JD 文件：{args.jd}", file=sys.stderr)
            return 2
        jd_text = args.jd.read_text(encoding="utf-8", errors="replace")

    report = Report()
    check_text_layer(texts, report, args.expect_pages, jd_text)
    geometry = page_geometry(args.pdf)
    if geometry is None:
        report.add("no_geometry", "info", "未安装 pymupdf，跳过页面几何检查：pip install pymupdf")
    else:
        check_pages_geometry(geometry, report)

    print_report(args.pdf, report, args.json)
    return 1 if (args.strict and report.by("hard")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
