#!/usr/bin/env python3
"""简历内容规则自检：把 references 里能机械判定的规则跑一遍。

用法：
    python scripts/check_resume.py <resume.html|resume.md|resume.txt>
    python scripts/check_resume.py <file> --jd assets/examples/jd.example.txt
    python scripts/check_resume.py <file> --against 旧稿.html
    python scripts/check_resume.py <file> --json

输出三档问题：
    HARD  必须改，否则不能交付（占位残留、破折号、禁用弱开头、术语错拼、缺联系方式）
    SOFT  建议改（套话、第一人称、单条过长、无数字、日期格式混用、结构占比失衡）
    INFO  供参考（中英混排空格、加粗过密）

退出码：0 正常；1 存在 HARD 问题（配合 --strict 在流水线里卡关）。

规则来源见 references/writing-rules-zh.md 与 references/content-layout.md。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# ---------------------------------------------------------------- 词表

# 弱开头：描述"离工作很近"，不描述工作本身（见 writing-rules-zh.md 第 2 节）
WEAK_OPENERS = (
    "负责", "参与", "协助", "配合", "帮助", "支持", "跟进", "了解", "接触",
    "学习", "完成日常", "从事", "开展工作", "进行",
)
# "负责" 在这些组合里承担责任界定，不算弱开头
WEAK_OPENER_ALLOW = ("独立负责", "本人负责", "全权负责")

# 中文套话（hard 程度较低，但出现即建议删）
CLICHES_ZH = (
    "赋能", "抓手", "闭环", "沉淀", "打法", "颗粒度", "助力", "深耕", "全方位",
    "打造", "丰富的经验", "较强的沟通能力", "沟通能力强", "学习能力强",
    "抗压能力强", "团队合作精神", "吃苦耐劳", "精通", "熟悉掌握", "熟练运用",
    "综合素质", "自我评价", "本人性格", "积极主动", "责任心强",
)
CLICHES_EN = (
    "spearheaded", "leveraged", "orchestrated", "utilized", "facilitated",
    "synergy", "cutting-edge", "results-driven", "holistic", "robust",
    "stakeholder", "responsible for", "assisted with", "worked on",
)

# 常见术语错拼 → 正确写法
TERM_TYPOS = {
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "light gbm": "LightGBM",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "sklearn": "scikit-learn（或写 sklearn，但全篇统一）",
    "scikit learn": "scikit-learn",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "tableau": "Tableau",
    "powerbi": "Power BI",
    "power bi": "Power BI",
    "langchain": "LangChain",
    "lang graph": "LangGraph",
    "tf-idf": "TF-IDF",
    "tfidf": "TF-IDF",
    "bert": "BERT",
    "bge": "BGE",
    "shap": "SHAP",
    "auc": "AUC",
    "roc": "ROC",
    "sas": "SAS",
    "spss": "SPSS",
    "stata": "Stata",
    "neo4j": "Neo4j",
    "streamlit": "Streamlit",
    "dify": "Dify",
    "coze": "Coze",
    "chatgpt": "ChatGPT",
}

# JD / 简历通用方法论与技术词库，用于关键词覆盖检查
TERM_LEXICON = (
    # 工具
    "Python", "SQL", "R 语言", "SAS", "SPSS", "Stata", "MATLAB", "Spark",
    "PySpark", "Hive", "Hadoop", "Tableau", "Power BI", "Excel", "Kettle",
    "Git", "Linux", "Docker", "Streamlit", "Neo4j", "LangChain", "Dify", "Coze",
    # 方法
    "逻辑回归", "线性回归", "岭回归", "Lasso", "XGBoost", "LightGBM", "随机森林",
    "决策树", "支持向量机", "聚类", "K-Means", "主成分分析", "因子分析",
    "时间序列", "ARIMA", "GARCH", "因果推断", "DID", "双重差分", "PSM", "倾向得分",
    "工具变量", "断点回归", "A/B 实验", "A/B 检验", "AB 实验", "假设检验",
    "显著性检验", "卡方检验", "方差分析", "抽样", "分层抽样", "样本量",
    "置信区间", "多重检验", "FDR", "生存分析", "贝叶斯", "机器学习", "深度学习",
    "自然语言处理", "TF-IDF", "向量检索", "BGE", "BERT", "命名实体识别",
    "知识图谱", "SHAP", "特征工程", "变量筛选", "WOE", "IV",
    # 指标
    "AUC", "KS", "PSI", "ROC", "准确率", "召回率", "F1", "MAE", "RMSE", "R²",
    "转化率", "留存率", "逾期率", "响应率", "ROI", "LTV", "GMV", "DAU", "MAU",
    # 业务
    "风控", "信用评分", "反欺诈", "精准营销", "用户画像", "用户增长",
    "经营分析", "指标体系", "指标口径", "数据治理", "数据质量", "数据看板",
    "报表", "数据仓库", "ETL", "贷后管理", "授信", "供应链", "定价",
    "市场研究", "用户研究", "问卷", "满意度", "政府统计", "数据要素",
    # 资质与软技能
    "CET-6", "CET-4", "CPA", "CFA", "FRM", "雅思", "托福",
    "跨部门", "沟通协调", "项目推进", "汇报",
)

# 同义词归并：命中任一即视为命中
TERM_ALIASES = {
    "A/B 实验": ("A/B 实验", "A/B 检验", "AB 实验", "AB 检验", "A/B test", "ABTest"),
    "AB 实验": ("A/B 实验", "A/B 检验", "AB 实验", "AB 检验", "A/B test", "ABTest"),
    "TF-IDF": ("TF-IDF", "TFIDF", "tf-idf", "tfidf"),
    "Power BI": ("Power BI", "PowerBI", "power bi"),
    "R 语言": ("R 语言", "R语言", "RStudio"),
    "数据看板": ("数据看板", "看板", "Dashboard", "dashboard"),
    "指标口径": ("指标口径", "口径"),
    "分层抽样": ("分层抽样", "抽样"),
    "逻辑回归": ("逻辑回归", "Logistic", "logistic"),
}

# 模板示例数据 / 占位符（来自 assets/template_refs 的示例人物）
PLACEHOLDERS = (
    "李明轩", "limingxuan", "example.com", "13812345678", "13800000000",
    "19900000000", "你的姓名", "你的邮箱", "XXX", "xxx", "XXXX", "待补",
    "TODO", "占位", "Lorem", "北京理工大学（985） 计算机科学与技术 2021.09",
)

DATE_STYLE_PATTERNS = (
    ("YYYY.MM", re.compile(r"(?:19|20)\d{2}\s*\.\s*\d{1,2}")),
    ("YYYY-MM", re.compile(r"(?:19|20)\d{2}\s*-\s*\d{1,2}(?!\d)")),
    ("YYYY/MM", re.compile(r"(?:19|20)\d{2}\s*/\s*\d{1,2}")),
    ("YYYY年MM月", re.compile(r"(?:19|20)\d{2}\s*年\s*\d{1,2}\s*月")),
    ("YYYY.MM月", re.compile(r"(?:19|20)\d{2}\s*\.\s*\d{1,2}\s*月")),
)
NON_ASCII_DASH = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
_DATE_TOKEN = r"(?:(?:19|20)\d{2}(?:\s*[.\-/年]\s*\d{1,2}\s*月?)?|\d{1,2}\s*月|至今|今|Present|present)"
YEAR_DASH_RE = re.compile(rf"{_DATE_TOKEN}\s*[{NON_ASCII_DASH}]\s*{_DATE_TOKEN}")
EM_DASH_RE = re.compile(r"—|\u2014|(?<![\w-])-{3,}(?![\w-])")
STUDY_STATUS_RE = re.compile(r"在读|预计|至今|应届|毕业生")
FIRST_PERSON_RE = re.compile(r"我(?!们)|本人(?!独立|负责|全权)")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
DIGIT_RE = re.compile(r"\d")
SPACE_AROUND_LATIN_RE = re.compile(r"[\u4e00-\u9fff][A-Za-z]|[A-Za-z][\u4e00-\u9fff]")

SECTION_KEYWORDS = {
    "education": ("教育", "学历", "education"),
    "project": ("项目", "实习", "经历", "实践", "科研", "project", "experience"),
    "honor": ("荣誉", "奖项", "获奖", "honor", "award"),
    "skills": ("技能", "专业能力", "skills"),
    "self": ("自我评价", "个人简介", "求职意向", "自我介绍"),
}

BULLET_HINTS = re.compile(r"^\s*(?:[-*•·]|\d+[.、)]|[（(]\d+[)）])\s+")


# ---------------------------------------------------------------- 抽取

@dataclass
class Block:
    text: str
    kind: str = "text"      # section | title | bullet | text
    section: str = "其他"
    line: int = 0


class _HtmlBlocks(HTMLParser):
    """把简历 HTML 拆成「分区 + 行」结构，不依赖具体模板的 class 名。"""

    SKIP_TAGS = {"style", "script", "head"}
    BLOCK_TAGS = {"li", "p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "span", "td"}
    SECTION_TAGS = {"h2"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self._buf: list[str] = []
        self._stack: list[tuple[str, str]] = []  # (tag, class)
        self._skip = 0
        self._section = "其他"
        self._strong_depth = 0
        self.bold_chars = 0
        self.text_chars = 0

    # -- 内部
    def _active_kind(self) -> str:
        for tag, cls in reversed(self._stack):
            if tag == "h2":
                return "section"
            if tag in ("h1",):
                return "name"
            if tag in ("li",):
                return "bullet"
            if tag in ("p", "h3", "h4"):
                return "text"
            if tag == "div" and any(
                k in (cls or "") for k in ("title", "entry-header", "item-header", "item-date")
            ):
                return "title"
        return "text"

    def _flush(self) -> None:
        raw = "".join(self._buf)
        self._buf.clear()
        text = re.sub(r"\s+", " ", raw).strip()
        if not text:
            return
        kind = self._active_kind()
        if kind == "section":
            self._section = text
        elif kind == "title" and len(text) <= 20 and section_of(text) and not DIGIT_RE.search(text):
            # 有些模板把模块标题写成 div.section-title，不是 h2
            kind = "section"
            self._section = text
        self.blocks.append(Block(text=text, kind=kind, section=self._section, line=self.getpos()[0]))

    # -- HTMLParser 回调
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        cls = dict(attrs).get("class", "") or ""
        if tag == "strong" or tag == "b":
            self._strong_depth += 1
            return
        if tag == "br":
            self._buf.append(" ")
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._stack.append((tag, cls))

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "strong" or tag == "b":
            self._strong_depth = max(0, self._strong_depth - 1)
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
            for i in range(len(self._stack) - 1, -1, -1):
                if self._stack[i][0] == tag:
                    del self._stack[i:]
                    break

    def handle_data(self, data):
        if self._skip:
            return
        if "data:image" in data or data.strip().startswith("base64"):
            return
        self.text_chars += len(data.strip())
        if self._strong_depth:
            self.bold_chars += len(data.strip())
        self._buf.append(data)

    def close(self):
        self._flush()
        super().close()


def extract_html(path: Path) -> list[Block]:
    parser = _HtmlBlocks()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    parser.html_stats = {  # type: ignore[attr-defined]
        "bold_chars": parser.bold_chars,
        "text_chars": parser.text_chars,
    }
    globals()["_LAST_HTML_STATS"] = parser.html_stats
    return parser.blocks


def extract_text(path: Path) -> list[Block]:
    globals()["_LAST_HTML_STATS"] = None
    blocks: list[Block] = []
    section = "其他"
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        if text.startswith("#"):
            section = text.lstrip("#").strip()
            blocks.append(Block(text=section, kind="section", section=section, line=i))
            continue
        kind = "bullet" if BULLET_HINTS.match(text) else "text"
        blocks.append(Block(text=BULLET_HINTS.sub("", text).strip(), kind=kind, section=section, line=i))
    return blocks


def load_blocks(path: Path) -> list[Block]:
    suffix = path.suffix.lower()
    if suffix in (".html", ".htm"):
        return extract_html(path)
    return extract_text(path)


# ---------------------------------------------------------------- 规则

@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    excerpt: str = ""
    line: int = 0


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add(self, rule: str, severity: str, message: str, excerpt: str = "", line: int = 0) -> None:
        self.findings.append(Finding(rule, severity, message, excerpt[:80], line))

    @property
    def hard(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "hard"]

    @property
    def soft(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "soft"]

    @property
    def info(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "info"]

    def score(self) -> int:
        penalty = 8.0 * len(self.hard) + 3.0 * len(self.soft) + 0.5 * len(self.info)
        return max(0, round(100 - penalty))


def section_of(text: str) -> str | None:
    for key, words in SECTION_KEYWORDS.items():
        if any(w in text for w in words):
            return key
    return None


def check_placeholders(blocks: list[Block], report: Report) -> None:
    hits: list[tuple[str, Block]] = []
    for b in blocks:
        low = b.text.lower()
        for p in PLACEHOLDERS:
            if p.lower() in low:
                hits.append((p, b))
                break
    if not hits:
        return
    names = ", ".join(sorted({p for p, _ in hits}))
    sample = "；".join(f"L{b.line} {b.text[:30]}" for _, b in hits[:4])
    report.add(
        "placeholder",
        "hard",
        f"{len(hits)} 处疑似模板占位或示例内容（{names}）：正式稿必须全部替换",
        sample,
        hits[0][1].line,
    )


def check_punctuation(blocks: list[Block], report: Report) -> None:
    date_hits: list[Block] = []
    dash_hits: list[Block] = []
    for b in blocks:
        if YEAR_DASH_RE.search(b.text):
            date_hits.append(b)
        elif EM_DASH_RE.search(b.text):
            dash_hits.append(b)
    if date_hits:
        sample = "；".join(f"L{b.line} {b.text[:40]}" for b in date_hits[:3])
        report.add(
            "date_dash",
            "soft",
            f"{len(date_hits)} 处日期区间用了非 ASCII 破折号（–/—/－）；部分 ATS 只按 - 切分，建议统一为 2026.09-2028.06",
            sample,
            date_hits[0].line,
        )
    if dash_hits:
        sample = "；".join(f"L{b.line} {b.text[:30]}" for b in dash_hits[:3])
        report.add(
            "em_dash",
            "info",
            f"{len(dash_hits)} 处正文破折号，中文可用；同篇务必与 - 分开使用、不要混用",
            sample,
            dash_hits[0].line,
        )


def check_bullets(blocks: list[Block], report: Report, max_len: int) -> None:
    bullets = [b for b in blocks if b.kind == "bullet"]
    no_number = 0
    spacing_hits: list[Block] = []
    for b in bullets:
        text = b.text
        head = text[:12]
        if any(a in head for a in WEAK_OPENER_ALLOW):
            pass
        else:
            for w in WEAK_OPENERS:
                if text.startswith(w):
                    report.add("weak_opener", "hard", f"弱开头「{w}」：改成动作/方法/结果开头", text, b.line)
                    break
        stripped = re.sub(r"\*\*|<[^>]+>", "", text)
        cjk = len(CJK_RE.findall(stripped))
        if cjk > max_len:
            report.add("long_bullet", "soft", f"单条约 {cjk} 字，超过 {max_len} 字建议拆或删", text, b.line)
        if not DIGIT_RE.search(stripped):
            no_number += 1
        for c in CLICHES_ZH:
            if c in stripped:
                report.add("cliche", "soft", f"套话「{c}」，换成具体事实", text, b.line)
                break
        low = stripped.lower()
        for c in CLICHES_EN:
            if c in low:
                report.add("cliche", "soft", f"英文套话「{c}」", text, b.line)
                break
        if FIRST_PERSON_RE.search(stripped):
            report.add("first_person", "soft", "简历正文不写「我/本人」", text, b.line)
        if SPACE_AROUND_LATIN_RE.search(stripped):
            spacing_hits.append(b)
    if spacing_hits:
        sample = "；".join(f"L{b.line} {b.text[:24]}" for b in spacing_hits[:3])
        report.add(
            "mixed_spacing",
            "info",
            f"{len(spacing_hits)} 条中英文之间没留空格（排版建议，不影响事实）",
            sample,
            spacing_hits[0].line,
        )
    if bullets:
        report.stats["bullets"] = len(bullets)
        report.stats["bullets_without_number"] = no_number
        if no_number and no_number / len(bullets) > 0.8:
            report.add(
                "no_metric_ratio",
                "info",
                f"{no_number}/{len(bullets)} 条没有数字；没有数字时用范围、使用方或完成度表达结果，不要硬凑比例",
            )


def check_terms(blocks: list[Block], report: Report) -> None:
    joined = "\n".join(b.text for b in blocks)
    for wrong, right in TERM_TYPOS.items():
        if not re.search(rf"(?<![A-Za-z0-9]){re.escape(wrong)}(?![A-Za-z0-9])", joined):
            continue  # 大小写敏感：只有原文确实这样写才算错
        if right.split("（")[0] in joined:
            continue  # 既有正确写法又有小写写法，说明只是引用，不追究
        report.add("term_typo", "hard", f"术语写法不规范：「{wrong}」应写作「{right}」")


def check_dates(blocks: list[Block], report: Report) -> None:
    joined = "\n".join(b.text for b in blocks)
    styles = sorted({name for name, pat in DATE_STYLE_PATTERNS if pat.search(joined)})
    report.stats["date_styles"] = styles
    if len(styles) > 1:
        report.add("date_style", "soft", "日期格式混用：" + "、".join(styles) + "；全篇只用一种")
    if re.search(r"(?:19|20)\d{2}\s*[.\-/]\s*\d{1,2}", joined) and "至今" not in joined and "Present" not in joined:
        report.add("date_open", "info", "未出现「至今」：若有进行中的经历，写 2026.11–至今")
    if re.search(r"(?:19|20)\d{2}\s*[.\-/]\s*\d{1,2}[^\n]{0,12}(?:19|20)\d{2}", joined) and not STUDY_STATUS_RE.search(joined):
        report.add("study_status", "soft", "出现学位时间区间但未标注「在读 / 预计 X 年 X 月毕业」")


def check_structure(blocks: list[Block], report: Report, skip_contact: bool = False) -> None:
    joined = "\n".join(b.text for b in blocks)
    if not skip_contact:
        if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", joined):
            report.add("contact_email", "hard", "未检测到邮箱：网申系统需要可复制的邮箱文本")
        if not re.search(r"1[3-9]\d{9}", joined):
            report.add("contact_phone", "info", "未检测到大陆手机号，若投国内岗位请补上")
    has_self = any(section_of(b.text) == "self" for b in blocks if b.kind in ("section", "title"))
    if has_self:
        report.add("self_evaluation", "soft", "存在「自我评价/个人简介」模块：无证据时建议删")

    per_section: dict[str, int] = {}
    current = "其他"
    for b in blocks:
        key = section_of(b.text) if b.kind == "section" else None
        if key:
            current = key
        per_section[current] = per_section.get(current, 0) + len(CJK_RE.findall(b.text))
    report.stats["section_chars"] = per_section
    total = sum(per_section.values())
    project_chars = per_section.get("project", 0)
    if total >= 500:
        share = project_chars / total
        report.stats["project_share"] = round(share, 3)
        if share < 0.33:
            report.add(
                "project_share",
                "soft",
                f"检测到项目/实习类文字占比约 {share:.0%}，课程要求至少 1/3",
            )


def check_bold(report: Report) -> None:
    stats = globals().get("_LAST_HTML_STATS")
    if not stats or not stats.get("text_chars"):
        return
    ratio = stats["bold_chars"] / stats["text_chars"]
    report.stats["bold_ratio"] = round(ratio, 3)
    if ratio > 0.25:
        report.add("bold_density", "soft", f"加粗占正文 {ratio:.0%}，超过 25% 会削弱重点")
    elif ratio < 0.03:
        report.add("bold_density", "soft", f"加粗仅占正文 {ratio:.0%}，建议给能力短语加粗引导阅读")


def check_jd(blocks: list[Block], jd_text: str, report: Report) -> None:
    resume_text = "\n".join(b.text for b in blocks)
    jd_low = jd_text.lower()
    wanted: list[str] = []
    for term in TERM_LEXICON:
        candidates = TERM_ALIASES.get(term, (term,))
        if any(c.lower() in jd_low for c in candidates):
            if term not in wanted:
                wanted.append(term)
    # 英文技术词（JD 里出现且不在词库里的）
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{1,}", jd_text):
        token = token.strip(".-/")
        if len(token) < 3 or token.lower() in {"the", "and", "for", "with", "you", "our", "are", "will", "able", "work", "team", "data", "and/or"}:
            continue
        wanted_low = {w.lower() for w in wanted}
        if token.lower() in wanted_low:
            continue
        # 已在词库项内部的子串不重复计（"Power BI" 里的 Power、pandas 之外的框架名等）
        if any(token.lower() in w or w in token.lower() for w in wanted_low):
            continue
        wanted.append(token)

    resume_low = resume_text.lower()
    hit, miss = [], []
    for term in wanted:
        candidates = TERM_ALIASES.get(term, (term,))
        if any(c.lower() in resume_low for c in candidates):
            hit.append(term)
        else:
            miss.append(term)
    report.stats["jd_terms"] = {"wanted": len(wanted), "hit": hit, "miss": miss}
    if wanted:
        coverage = len(hit) / len(wanted)
        report.stats["jd_coverage"] = round(coverage, 3)
        if coverage < 0.5:
            report.add(
                "jd_coverage",
                "soft",
                f"JD 关键词覆盖 {coverage:.0%}：缺失 {', '.join(miss[:12])}（只补有证据的）",
            )


def check_against(blocks: list[Block], old_text: str, report: Report) -> None:
    new_text = "\n".join(b.text for b in blocks)

    def numbers(text: str) -> set[str]:
        # 日期整体当一个 token，避免 2026.09 被拆成 2026 与 09 造成假差异
        text = re.sub(r"(?:19|20)\d{2}\s*[.\-/年]\s*\d{1,2}\s*月?", "#DATE", text)
        return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?%?", text))

    def terms(text: str) -> set[str]:
        return {
            t.lower().strip(".-/")
            for t in re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{2,}", text)
            if not t.islower() or len(t) > 3
        }

    added = numbers(new_text) - numbers(old_text)
    dropped = numbers(old_text) - numbers(new_text)
    added_terms = terms(new_text) - terms(old_text)
    dropped_terms = terms(old_text) - terms(new_text)
    if added:
        report.add("fact_added_number", "hard", f"改写新增了数字：{', '.join(sorted(added))}")
    if dropped:
        report.add("fact_dropped_number", "soft", f"改写丢了原来的数字：{', '.join(sorted(dropped))}")
    if added_terms:
        report.add("fact_added_term", "soft", f"改写新增了术语/名词：{', '.join(sorted(added_terms)[:15])}")
    if dropped_terms:
        report.add("fact_dropped_term", "info", f"改写丢掉了原术语：{', '.join(sorted(dropped_terms)[:15])}")


# ---------------------------------------------------------------- 输出

SEV_LABEL = {"hard": "HARD", "soft": "SOFT", "info": "INFO"}


def print_report(path: Path, report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps(
            {
                "file": str(path),
                "score": report.score(),
                "stats": report.stats,
                "findings": [f.__dict__ for f in report.findings],
            },
            ensure_ascii=False,
            indent=2,
        ))
        return

    print(f"简历自检：{path.name}")
    print(f"综合评分：{report.score()}/100（HARD {len(report.hard)}｜SOFT {len(report.soft)}｜INFO {len(report.info)}）")
    if report.stats:
        bits = []
        if "bullets" in report.stats:
            bits.append(f"条目 {report.stats['bullets']} 条，其中无数字 {report.stats.get('bullets_without_number', 0)} 条")
        if report.stats.get("project_share") is not None:
            bits.append(f"项目/实习文字占比 {report.stats['project_share']:.0%}")
        if report.stats.get("bold_ratio") is not None:
            bits.append(f"加粗占比 {report.stats['bold_ratio']:.0%}")
        if report.stats.get("jd_coverage") is not None:
            bits.append(f"JD 关键词覆盖 {report.stats['jd_coverage']:.0%}")
        if bits:
            print("统计：" + "｜".join(bits))
    print()

    for sev in ("hard", "soft", "info"):
        items = [f for f in report.findings if f.severity == sev]
        if not items:
            continue
        print(f"[{SEV_LABEL[sev]}] {len(items)} 项")
        for f in items:
            loc = f" L{f.line}" if f.line else ""
            print(f"  - {f.message}{loc}")
            if f.excerpt:
                print(f"    › {f.excerpt}")
        print()

    jd = report.stats.get("jd_terms")
    if jd:
        print("JD 命中：" + ("、".join(jd["hit"]) if jd["hit"] else "无"))
        if jd["miss"]:
            print("JD 缺失（只补有证据的）：" + "、".join(jd["miss"][:20]))
        print()

    if not report.findings:
        print("未发现规则问题。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="简历内容规则自检")
    parser.add_argument("file", type=Path, help="HTML / Markdown / 纯文本简历")
    parser.add_argument("--jd", type=Path, help="JD 文本文件，用于关键词覆盖检查")
    parser.add_argument("--against", type=Path, help="旧稿文件，用于事实保真对比")
    parser.add_argument("--max-len", type=int, default=90, help="单条中文字数上限（约两行），默认 90")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--skip-contact", action="store_true", help="只检查经历片段时跳过联系信息检查")
    parser.add_argument("--strict", action="store_true", help="存在 HARD 问题时退出码 1")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.file.exists():
        print(f"找不到文件：{args.file}", file=sys.stderr)
        return 2

    blocks = load_blocks(args.file)
    report = Report()
    check_placeholders(blocks, report)
    check_punctuation(blocks, report)
    check_bullets(blocks, report, args.max_len)
    check_terms(blocks, report)
    check_dates(blocks, report)
    check_structure(blocks, report, skip_contact=args.skip_contact)
    check_bold(report)
    if args.jd:
        if not args.jd.exists():
            print(f"找不到 JD 文件：{args.jd}", file=sys.stderr)
            return 2
        check_jd(blocks, args.jd.read_text(encoding="utf-8", errors="replace"), report)
    if args.against:
        if not args.against.exists():
            print(f"找不到对比稿：{args.against}", file=sys.stderr)
            return 2
        check_against(blocks, "\n".join(b.text for b in load_blocks(args.against)), report)

    print_report(args.file, report, args.json)
    return 1 if (args.strict and report.hard) else 0


if __name__ == "__main__":
    raise SystemExit(main())
