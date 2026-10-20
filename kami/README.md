# Kami · 紙

收录自 [tw93/Kami](https://github.com/tw93/Kami)，版本 **1.18.0**，收录日期 2026-10-20。上游 skill 内容、模板、脚本与许可证保持原样，本文件为仓库补充说明。

## 安装

将本目录整体复制到 Codex 的 skills 目录（默认 `~/.codex/skills/kami`）。已有同名目录时先备份。完整中文说明见 [上游 README_CN.md](https://github.com/tw93/Kami/blob/main/README_CN.md)。

## 使用

```text
用 $kami 把这份内容排成中文一页纸，输出 PDF。
```

支持简历、一页纸、长文档、信件、作品集、幻灯片、研报、更新日志及静态落地页。入口见 [SKILL.md](SKILL.md)。

## 环境要求

Windows 推荐 WSL（Ubuntu）。主要依赖包括 Python、WeasyPrint、pypdf、PyMuPDF；可编辑 PPTX 需要 python-pptx，数学公式需要 Node.js 与 MathJax。部分字体按上游脚本补充，不随本仓库另外打包。

先检查环境：

```bash
python scripts/build.py --doctor
```

当前收录时，本机完成 skill 安装和资源一致性核对；环境诊断提示缺少 PDF 核心依赖、PPTX/MathJax 支持及未确认的 CJK 字体，尚未验证实际渲染。安装 skill 本身不会自动配置完整渲染环境。按 [上游说明](https://github.com/tw93/Kami/blob/main/README_CN.md) 准备运行环境后使用。

## 更新、反馈与许可

这是固定版本副本，不会自动同步上游文件。更新时对照 VERSION 与上游变更，并保留 [LICENSE](LICENSE) 及资源内许可证。

问题可在 [本仓库 Issues](https://github.com/GreysonXie/skill-using-by-myself/issues) 反馈，注明 Kami 版本、运行环境、提示词和脱敏截图。
