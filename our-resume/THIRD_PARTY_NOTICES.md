# 来源与第三方声明

- `resume-master`：本地版本标注作者 Wonderful王。五套模板及三个 Python 脚本原样沿用；取得的本地副本未包含许可证，本项目不对这些资源另行授予 MIT 等许可。
- [resumify](https://github.com/breaker505/resumify)：七段经历提炼结构参考该项目，保留其 MIT 声明于 [licenses/resumify-MIT.txt](licenses/resumify-MIT.txt)。
- 内容方法结合维护者提供的简历课程资料整理，来源及取舍见 [references/source-decisions.md](references/source-decisions.md)。课程原件未包含在此仓库。

## 参考的开源项目（仅借鉴机制，未复制代码）

- [Resume-Matcher](https://github.com/srbhr/Resume-Matcher)（Apache-2.0）：借鉴其"评分与写作检查全部由代码完成、不调用模型"的思路，包括 ATS 五维打分权重、写作 rubric 的可判定项（弱开头、破折号、第一人称、套话、单条过长、无指标、重复开头）、改写的数字与术语保真校验、页数优先于视觉压缩。`scripts/check_resume.py` 与 `scripts/check_pdf.py` 的规则与代码为本项目按中文简历语境重新实现，未复制其源文件。
- [ai-job-search](https://github.com/ai-job-search-dev/ai-job-search)（MIT）：借鉴其门槛先于打分的评估顺序（资格 / 语言 / 地点物流）、相关性加权删减（相关性 / 是否重复 / 叙事负荷）、页预算与"进行中学位必须标注"、ATS 文本层检查细则（日期 ASCII 区间、联系方式须在文本层、乱码与阅读顺序）、交付自检脚本的检查项与阈值思路、面试回溯测试与投递跟进流程。相关规则以中文重写，未复制其源文件。

不同来源文件的权利归原作者；此说明不代表原作者为本改编背书。仓库没有对全部混合来源内容统一授予开源许可证。
