# 项目状态与使用入口

更新日期：2026-09-16。可以直接打开的工具有两项：**[预测审阅](https://forecast-review-zheyuliu.mystic-pear-2111.chatgpt.site)** 和 **[表格对账](https://table-check-zheyuliu.mystic-pear-2111.chatgpt.site)**。无需安装或注册，选择文件后在浏览器内计算；没有文件时可以先运行虚构示例。

## 直接在线使用

| 工具 | 适合解决什么问题 | 带什么文件 | 获得什么 |
| --- | --- | --- | --- |
| [预测审阅 / Forecast Review Workbench](https://forecast-review-zheyuliu.mystic-pear-2111.chatgpt.site) | 两份预测的误差能否公平比较，哪些期间没有覆盖 | 实际值、1—5 份预测及可选基线，CSV 或 Excel | 共同样本误差、缺失记录、复核意见与离线报告；同一工具还提供月度回归实验和金融结果对账 |
| [表格对账 / Financial Control Tower](https://table-check-zheyuliu.mystic-pear-2111.chatgpt.site) | 两份表有哪些数值差异、遗漏或重复编号 | 两份 CSV 或 Excel，确认编号、数值列和单位 | 差异明细、CSV、HTML 和证据 ZIP |

预测审阅需要使用者确认比较范围、单位及共同样本；工具不会代替使用者接受缺失数据或批准模型。表格对账公开版每份文件上限为 8 MiB，同次最多 20,000 个潜在字段检查；不自动换算币种、加总重复编号或计算 Excel 公式。导出可能包含输入快照，分享前应检查内容。

[预测审阅指南](https://github.com/zheyuliu328/forecast-review-workbench/blob/main/docs/QUICKSTART.zh-CN.md) · [表格对账指南](https://github.com/zheyuliu328/financial-control-tower/blob/main/docs/table-ui.zh-CN.md)

## 其余项目怎样使用

| 项目 | 当前交付状态 | 可以做什么 | 尚未完成或尚未验证 |
| --- | --- | --- | --- |
| [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab) | 本地工具与专业实验 | 月度候选筛选、信用时间序列教学实验、FX 价格和敏感度校验；部分计算被 Workbench 复用 | 独立网页入口、季度发布延迟与稳健性扫描、极端数值范围挑战；没有生产或监管验证结论 |
| [VaR Backtesting](https://github.com/zheyuliu328/risk-var-dashboard) | 本地专业工具 | 单序列 VaR 预测与覆盖率回测 | 独立网页入口、ES 验证、例外独立性检验及组合资本模型 |
| [CreditOne](https://github.com/zheyuliu328/algorithmic-credit-risk-engine) | 研究原型，部分功能未完成 | 合成分类、评分卡组件、指标教学 | 外部模型验证尚未实现；ECL 集成、PSI 尾部、历史概率调整和可选界面仍有缺口 |
| [Risk Practice Portfolio](../README.md) | 作品入口与可复现案例库 | 本页导航、旗舰案例、16 组可执行教学示例及学习路线 | 这些练习没有全部包装成网页工具；不代表 16 个成熟产品或真实客户经验 |
| [HSTECH NLP study](https://github.com/zheyuliu328/hstech-nlp-quant-factor) | 历史研究案例 | 阅读情绪因子研究方法及保留的负面结果 | 本轮未复现历史业绩，样本与风险中性化限制仍在 |
| [RMSC6007 Group Project](https://github.com/zheyuliu328/RMSC6007-GroupProject) | 团队课程参考 | 按已注明来源阅读课程实验 | 团队贡献不能作为个人独作；不完整报告与许可状态需另行核实 |
| [Signal Foundry](https://github.com/zheyuliu328/signal-foundry) | 辅助信息工具 | 组织公开信号与证据记录 | 本次未做运行或公网发布验收；不提供自动事实认证 |
| [Resume AI Builder](https://github.com/zheyuliu328/resume-ai-builder) | 辅助工具，待单独验收 | 阅读简历版本与文档工作流 | 效率、API 与隐私行为、许可差异需单独核实 |
| [个人主页](https://github.com/zheyuliu328) | 项目导航 | 直接进入工具、案例和学习材料 | 不作为另一项风险产品统计 |

其余 [参考 forks](../reference/README.md) 保留原始来源和贡献归属，不列为自研产品。

## 这些状态能说明什么

“公开可用”表示有公开网页入口和所列操作流程；不等于已经证明好用、有人持续使用或适合生产业务。两项网页工具的**外部真人首次使用、独立完成任务和重复使用仍待验证**。自动化检查与代理操作不能替代真人观察，也没有据此填写完成时间、成功率或用户评价。

这里的交付方式与 [展示优先级](PRIORITIES.md) 分开记录。旗舰、专业案例、实验室和参考是展示位置，不是成熟度评分。9 月 15 日检查使用的固定提交、历史复算输入和验证日期保留在原记录中；本次状态更新没有重新运行所有仓库的测试。

[各项目的机器目录](projects.json) 保留 `verified_commit`、`evidence_date` 和 `evidence_basis` 作为历史检查记录，新增的 `delivery_status`、`entry_url`、`status_date` 说明本次入口与交付方式。案例的固定提交并不等于当前网站的构建版本；发布验证以各工具自己的记录为准。

[返回作品集](../README.md) · [案例验证范围](../validation/README.md)
