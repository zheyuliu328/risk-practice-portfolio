# Risk work-scenario casebook / 风险工作场景

Date: 2026-09-15. Twelve core scenarios connect the portfolio to practical review tasks. **Implementation status is separate from personal mastery.** A learning calculation is a transparent simplification; a designed exercise is not yet a working module. None of these cases is represented as the author's client engagement.

[Runnable cases and response plans](WORKED_CASES.zh-CN.md)

## Coverage map

| ID | Work question | Current executable support | Remaining implementation |
| --- | --- | --- | --- |
| [C01](#c01-credit-parameters) | Ranking is good; why is loss prediction low? | PD calibration/discrimination, provisional recovery LGD and commitment EAD examples | Population estimation, downturn calibration and independent approvals |
| [C02](#c02-ecl-and-model-selection) | Why did provisions rise despite better macro forecasts? | Workbench monthly OLS; ECL, recovery and ordered movement bridge | Policy-specific SICR assignment and full accounting cash-flow treatment |
| [M01](#m01-market-risk) | VaR is within limits; why is stress loss unacceptable? | Existing causal VaR tool; empirical ES and named stress examples | Exception clustering and portfolio-specific repricing |
| [M02](#m02-valuation-and-greeks) | Prices agree; why do hedge sensitivities disagree? | Model Risk Lab pricing/Greeks/independent challenges | Smile/path-dependent products; no proprietary SIMM implementation |
| [C03](#c03-counterparty-risk) | Why does collateral not eliminate exposure? | Time-aligned exposure/collateral paths, EE/PFE and independent CVA | Full CSA mechanics and joint exposure/default WWR |
| [B01](#b01-broker-margin-and-concentration) | Why stop new finance when collateral looks adequate? | Issuer concentration, haircut, required call and available liquidation cash | Actual order execution, changing loan terms and dynamic liquidation |
| [L01](#l01-liquidity) | Assets exceed liabilities; why might tomorrow's payments fail? | This hub's daily cash-flow survival calculation | Entity/currency restrictions and policy-specific stress schedules |
| [L02](#l02-interest-rate-and-nmd) | NII improves; why can economic value fall? | Fixed cash-flow shock and NMD beta/runoff EVE/NII exercise | Behavioural estimation, options and full bank IRRBB |
| [G01](#g01-model-governance) | Drift increased; retrain, restrict or stop? | Workbench review evidence; PSI, supplied-loss monitoring and human-review signals | Production monitoring, approved policy and mature-label verification |
| [O01](#o01-data-and-operational-controls) | Totals agree; why is the report still unsafe to deliver? | FCT browser/local comparison; Workbench layered reconciliation | Independent human adoption and source-system integration |
| [F01](#f01-fraud-and-aml) | Alerts exceed investigation capacity; what should change? | Label-aware priority, capacity, backlog and known-label cost exercise | Bias-adjusted outcome estimation and production investigation integration |
| [A01](#a01-ai-model-governance) | AI's risk report looks convincing; can it be released? | Numeric, required-source, supplied semantic and action-allowlist checks | Independent semantic benchmark and live AI/security integration |

## Common execution and handoff contract

For every case, create a short **scope note** before calculating: decision owner, business use, entity/population, as-of date, forecast horizon, currency/units, input origin, applicable policy edition and exclusions. A policy threshold chosen for an exercise is labelled illustrative, not regulatory.

Execution order: freeze the input version → check completeness and definitions → calculate a simple baseline → run the candidate method → challenge with an independent calculation and a deliberately adverse case → classify findings → propose a response and escalation owner → obtain human review → retain the evidence.

The handoff contains the request and input fingerprints, reconciled population counts, model/configuration version, baseline and stressed results, row-level exceptions, assumptions, an action log and unresolved questions. Each action records owner, deadline/trigger, expected evidence and closure reviewer. A severity label is tied to the intended use and impact, not an arbitrary universal threshold.

## C01 Credit parameters

**委托与岗位：** 信用风险或模型验证人员收到排序表现不错的PD模型，但实际损失持续高于预测。银行IRB规则不能自动套用于券商或会计ECL。

**输入与方法：** 逐笔观察日、预测PD、统一违约标签及窗口、客群、余额、额度、回收现金流与成本。分别研究Logistic PD、折现回收LGD、`drawn + CCF × undrawn`的EAD。观察窗口与目标定义先于算法选择；未完结回收不能直接当零损失或被静默剔除。

**执行：** 按时间和客群检查覆盖 → 将排序、校准、稳定性分开 → 核对违约定义及标签成熟度 → 做LGD回收时点与EAD提款敏感性 → 分解误差贡献。当前 [CreditOne](https://github.com/zheyuliu328/algorithmic-credit-risk-engine)可用于分类学习，其legacy调整和指标限制必须保留。

**反例与行动：** 将所有PD减半可以不改变排序，却改变校准。先排查标签/定义/样本变化，再判断是否重新校准、限制适用客群或补数据；风险负责人批准使用限制，模型所有人实施整改，验证人员复核。输出参数检查表和损失敏感性备忘录。

**面试：** AUC不变但违约率翻倍先查什么？只用已结清回收案例估LGD会怎样偏？合格答案应区分排序与校准、选择偏差和未成熟标签，不能只说换更复杂模型。

**来源：** [HKMA CA-G-4 当前版](https://brdr.hkma.gov.hk/eng/doc-ldg/spm/current/CA-G-4)，2025-07-18版本检查。完整参数验证流程尚未在本仓实现。

## C02 ECL and model selection

**委托与岗位：** 信用风险/拨备复核人员解释“宏观预测改善但拨备上升”，先确定会计适用资产和报告日期。

**输入与方法：** 初始确认与当前信用信息、条件PD期限结构、LGD/EAD、有效利率、宏观信息实际发布时间、情景及权重、阶段与overlay政策。离散期边际PD为之前存活概率乘当期条件PD。简化损失计算见 [ecl.json](../examples/ecl.json)，局限见[例子说明](../examples/README.md)。

**执行：** 核对阶段迁移和敞口变化 → 检查MEV经济逻辑、滞后与发布时间 → 开发期选择候选、独立留出评估 → 汇总同口径情景损失 → 分别改变余额、阶段、参数、权重及overlay解释拨备变动。可使用 [Workbench](https://github.com/zheyuliu328/forecast-review-workbench)做候选生产和公平比较；当前ECL函数不自动分阶段。

**反例与行动：** 加入预测日尚未发布的显著变量；验证它应被延迟或排除。阶段2占比上升可能抵销宏观改善，应区分经济恶化和规则改版。发现缺口后由拨备/信用负责人确认政策，模型团队补证，财务负责人确认会计处理；输出变动归因、敏感性和未解决政策事项。

**面试：** 显著MEV发布晚于预测日怎么办？SICR阈值改变造成阶段2增加，如何解释？答案需提到时点、初始信用基准、定性信息及政策影响。

**来源：** [IFRS 9 已发布正文5.5节（2022版本，非当前完整准则合集）](https://www.ifrs.org/content/dam/ifrs/publications/pdf-standards/english/2022/issued/part-a/ifrs-9-financial-instruments.pdf?bypass=on)；[IFRS官方多情景说明](https://www.ifrs.org/news-and-events/news/2016/07/25-webcast-on-ifrs-9/)。十二个月ECL限定可能发生违约事件的窗口，不是只看十二个月现金短缺。正式运用需核对适用的当前准则和本机构政策。

## M01 Market risk

**委托与岗位：** 银行交易账簿或券商风险人员解释“VaR限额内，压力损失仍很大”。

**输入与方法：** 固定时点持仓、价格/收益、币种、实际或假设P&L、风险因子和压力情景。明确正数损失还是负收益阈值。历史/正态VaR、尾部平均损失ES和压力重估回答不同问题。现有 [VaR工具](https://github.com/zheyuliu328/risk-var-dashboard)计算单序列预测和非条件覆盖率，不包含完整ES验证。

**执行：** 冻结持仓口径 → 用之前的数据预测后续结果 → 同时检查例外频率、集中时间与严重程度 → 对遗漏风险因子、流动性和持仓变化做归因 → 比较限额与压力承受力。不能把基于变化持仓的损失直接当固定组合模型回测。

**反例与行动：** 相同例外总数集中在连续几天时，Kupiec结果可能不变。风险人员应调查状态变化与共同风险，提出临时降限、对冲或减少集中敞口等待批准选项；交易/资金团队确认执行成本和可行性，风险委员会审批重大限额变化。输出例外日志和压力行动单。

**面试：** 连续五天例外却总体频率合格，能接受吗？限额内的大额压力损失如何报告？需区分覆盖、独立性、严重程度和业务承受力。

**来源：** [Basel MAR32 回溯与损益归因](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/32/inforce/2023-01-01/published/2020-03-27)；[HKMA IC-5 当前版](https://brdr.hkma.gov.hk/eng/doc-ldg/spm/current/IC-5)，2026-04-13版本检查。工具不声称FRTB批准。

## M02 Valuation and Greeks

**委托与岗位：** 估值/模型验证人员调查参考模型和challenger价格接近、对冲量却差异明显。

**输入与方法：** 合约类型、名义本金、报价方向、国内/国外货币、利率、期限、波动率和敏感度单位。原创欧式FX公式、解析Greeks、差分步长和独立积分可在 [Model Risk Lab](https://github.com/zheyuliu328/model-risk-lab)复现。

**执行：** 对齐输入及输出单位 → 先查价格和恒等式 → 跨价内外、期限和步长比较敏感度 → 按数据约定、数值分辨率和模型假设归类差异 → 用交易规模评估用途影响。小步长并非总是更准确。

**反例与行动：** 波动率百分点与绝对比例混淆可能不破坏部分价格恒等式。验证人员列出可复现差异，由模型所有人修正单位/实现；风险使用者在重要敏感度未解决前决定限制使用，不能只凭价格接近关闭发现。输出价格/Greeks误差表及原因证据。

**面试：** 价格一致但Vega不一致怎样定位？差分步长越小误差越大为什么？需解释量纲、截断和浮点抵消。

**来源：** [Basel MAR99 验证背景](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/99/inforce/2023-01-01/published/2020-03-27)；[ISDA SIMM licensing FAQ](https://www.isda.org/2021/04/08/isda-simm-licensing-faq/)。公开资料不等于获得参数/软件的开源许可；本作品不发布专有SIMM复刻，也不声称平坦参数欧式模型覆盖smile和路径依赖。

## C03 Counterparty risk

**委托与岗位：** 衍生品或prime服务风险人员解释“每天有VM，为什么还有敞口”。本场景目前是执行设计，数值路径模块待实现。

**输入与方法：** 法律净额集合、合约MTM路径、抵押币种/折扣、门槛、最小转移额、追保延迟、保证金风险期和信用情景。先计算各集合正敞口，再求EE/PFE；简化独立CVA可用折现EE乘边际违约概率与LGD，但必须另做相关性/WWR挑战。

**执行：** 确认净额法律边界 → 重估市场路径 → 按真实可用时间处理抵押 → 模拟市场跳变和延迟平仓 → 检查信用质量、抵押价值与敞口共同恶化。不同不可净额实体不能先相互抵销。

**反例与行动：** 收取交易对手自身股票作抵押，在其信用恶化时可能同步贬值。信用/交易对手负责人审视额度，法律确认净额，抵押品运营核实可用性；考虑降低集中、提高合格抵押或限制交易，记录成本及批准。输出净额集敞口、抵押缺口和限额备忘录。

**面试：** 日度VM为什么不消除CCR？独立CVA对WWR有什么遗漏？答案需提到时滞、跳变、相关性和法律可执行性。

**来源：** [BCBS CCR管理指引](https://www.bis.org/committees/bcbs/basel-consolidated-guidelines/module/cri/40)。Monte Carlo PFE不等于SA-CCR监管PFE；敞口也不等于损失。

## B01 Broker margin and concentration

**委托与岗位：** 香港券商孖展人员决定是否继续新增融资，避免只看抵押覆盖。集中度例子已可运行，完整追保/处置模型待实现。

**输入与方法：** 客户及关联集团、贷款、证券数量和价格、haircut、停牌/成交限制、追加现金的实际到账时间。按经济关联先聚合；用 [concentration.json](../examples/concentration.json)计算HHI/top share，再研究冲击后折扣抵押价值与追保缺口。

**执行：** 对齐贷款与持仓 → 识别同一股票/集团集中 → 冲击价格与可变现比例 → 计算需要追保的金额 → 分开记录要求、承诺、到账和实际平仓。不能把追保通知当成收到现金。

**反例与行动：** 四个法律客户可能共同暴露于同一股票或集团。券商信用负责人决定新增融资限制；客户服务/运营跟进追保，交易与风险确认处置流动性，重大例外走授权审批。输出集中度、追保时间表和处置限制。

**面试：** 抵押覆盖很高但股票集中，风险在哪里？提高haircut是否立刻降低风险？应讨论缺口、客户现金能力和被迫出售压力。

**来源：** [SFC证券孖展融资指引](https://www.sfc.hk/-/media/EN/assets/components/codes/files-current/web/guidelines/guidelines-for-securities-margin-financing-activities/guidelines-for-securities-margin-financing-activities.pdf)。HHI与简单缺口不是FRR流动资本申报或监管大额风险承担测试。

## L01 Liquidity

**委托与岗位：** 资金/流动性风险人员判断压力下哪一天出现资金缺口。券商应使用结算、融资和追保现金流，不能照搬银行存款政策。

**输入与方法：** 可用期初现金、逐日流入流出、资产变现净额与生效日；按币种和法律实体分别建账。运行 [liquidity.json](../examples/liquidity.json)得到每日余额和首次日终负值。

**执行：** 检查收付日与可转移性 → 排除已抵押或不能及时变现资产 → 构造机构特有、市场共同和组合冲击 → 依次改变流出、延迟、haircut与融资来源 → 记录应急动作什么时候真正改变现金余额。日终非负不证明日内所有支付顺序都可满足。

**反例与行动：** 资产账面价值足够但出售需三天，不能用于明天的支付。资金团队确认融资/变现渠道，流动性风险负责人设定升级触发，管理层审批应急融资计划。输出现金阶梯、可用与不可用资金清单、首次缺口和响应时序。

**面试：** 盈利企业为何仍会流动性危机？存款流失和保证金追加同时发生怎样防止漏算/双算？答案需分清偿付能力、流动性、可用时间和资金来源相关性。

**来源：** [HKMA LM-2 当前版](https://brdr.hkma.gov.hk/eng/doc-ldg/spm/current/LM-2)。本模型不计算LCR/LMR，不保证融资承诺可立即提款。

## L02 Interest rate and NMD

**委托与岗位：** 银行ALM人员解释加息后短期利息收入和长期经济价值方向不同。

**输入与方法：** 资产/负债现金流、重定价日期、基准及冲击曲线、NMD beta/流失假设、提前还款和选择权。当前 [rates.json](../examples/rates.json)只实现单组固定年度现金流在平坦利率冲击下的PV，是学习基础，不是全行EVE/NII。

**执行：** 区分合约期限和行为重定价 → 分别研究一年收入和全生命周期价值 → 扰动存款beta、稳定余额和提前还款 → 检查非平行/基差风险 → 提出对冲及假设验证需求。

**反例与行动：** 历史存款beta低，不代表竞争加剧时仍然低；余额稳定不等于固定期限负债。ALM/资金部门分析可执行对冲，模型团队补充行为证据，风险委员会审议重大假设。输出两个风险视角的解释及假设敏感性。

**面试：** ΔNII和ΔEVE方向相反一定有错吗？怎样挑战NMD行为参数？合格答案说明计量期限、重定价和行为不确定性。

**来源：** [HKMA IR-1 当前版](https://brdr.hkma.gov.hk/eng/doc-ldg/spm/current/IR-1)，2025-12-23版本检查。自选200bp例子不代表全部监管冲击；不可标为券商通用资本框架。

## G01 Model governance

**委托与岗位：** 模型风险人员处理漂移告警，决定补证、限用、重训或停用。统计信号与审批流程必须分开。

**输入与方法：** 模型/版本登记、用途、责任人、重大性、开发及独立验证记录、数据质量、性能/校准、标签成熟度。PSI或其他分布距离只是诊断；没有标签不能声称性能没有下降。当前可用Workbench记录比较与人工意见；完整持续监控政策模块待实现。

**执行：** 确认输入与用途是否改变 → 判断数据漂移还是目标关系变化 → 检查标签迟到与样本量 → 用多个证据形成发现等级 → 指定整改和限制 → 独立验证后关闭。阈值需关联本机构用途和基准，不把0.1/0.25写成普遍法律规则。

**反例与行动：** PSI上升但AUC稳定可能是样本构成变化，也可能尚无成熟坏样本。模型所有人提供解释和修复，验证人员挑战，授权治理人员批准限制或恢复；临时overlay有退出条件。输出模型卡、发现清单和版本化决策日志。

**面试：** 漂移和性能结论冲突如何处理？没有源代码的第三方模型怎么验证？答案应覆盖用途、输入输出挑战、供应商证据、限制和持续监控。

**来源：** [Federal Reserve模型风险管理指南](https://www.federalreserve.gov/frrs/guidance/supervisory-guidance-on-model-risk-management.htm)，2026修订版，作为美国比较学习资料；不称香港强制规范。SR11-7只能注明历史背景，生成式/agentic AI另见A01。

## O01 Data and operational controls

**委托与岗位：** 风险报告/财务运营人员收到总额一致但逐笔异常的两份结果。

**输入与方法：** 原始两侧文件、业务主键、cut-off、币种/单位、容差、预计覆盖和可加总规则。使用 [FCT](https://github.com/zheyuliu328/financial-control-tower)处理表格，或 [Workbench](https://github.com/zheyuliu328/forecast-review-workbench)处理风险身份、期限及控制总额。

**执行：** 冻结来源 → 先隔离重复、无效和不一致口径 → 双向匹配 → 保留所有缺失 → 逐笔与汇总交叉核对 → 按原因、账龄和责任人分配 → 第二人复核关闭。两侧都没有的记录需要第三方预期清单，不能靠两表比较发现。

**反例与行动：** +10和-10相互抵销，总额不能清除逐笔breach。源系统负责人修复数据，运营核查待结算差异，报告负责人决定暂缓或披露缺口，独立复核人确认关闭。输出全量异常和人工理由；下载包可能包括完整原文件，分享前检查。

**面试：** 总额一致如何发现抵销错？月末未匹配如何划分责任？需说明粒度、完整性、时点和闭环证据。

**来源：** [BCBS239风险数据汇总与报告原则](https://www.bis.org/publ/bcbs239.pdf)；[SFC交易运营/remote booking通函](https://apps.sfc.hk/edistributionWeb/gateway/EN/circular/intermediaries/supervision/doc?refNo=23EC14)。一致性不证明交易合法或估值正确。

## F01 Fraud and AML

**委托与岗位：** 欺诈或AML团队面对超出调查容量的告警。本场景目前是执行设计，不是已验证的检测模型。

**输入与方法：** 新造交易、客群和时间、示例速度/金额/新受益人规则、人工判定标签及来源、调查容量和反馈时滞。先区分即时欺诈拦截和AML调查目标，不能把两者标签混在一起。

**执行：** 按客群回溯规则 → 保留未调查/未知标签 → 在有可用标签的范围比较误报和漏报 → 检查被调查样本选择偏差 → 按风险、成本及容量形成待审队列 → 授权人员决定升级/报告并记录理由。关闭告警不是天然真阴性。

**反例与行动：** 将告警减半可能只是漏掉了困难样本。调查负责人评估容量和抽查设计，模型/规则所有人调整并验证，AML授权人员结合事实决定报告；不能让学习算法自动断言违法。输出队列、容量敏感性、未知标签和反馈方案。

**面试：** 告警数量下降是否代表更好？仅已调查样本有标签如何估漏报？答案需讨论选择偏差、未知结果和抽样复核，不编造真实recall。

**来源：** [HKMA交易监控与AI专题审查](https://brdr.hkma.gov.hk/eng/doc-ldg/docId/20240417-2-EN)。不使用真实客户案例或规避监控攻略。

## A01 AI model governance

**委托与岗位：** 银行/券商风险或治理人员决定AI生成报告能否进入正式流程。当前是防御性执行设计，测试工具待实现。

**输入与方法：** 新造问题、正确证据与计算、允许的工具动作、模型/提示/数据版本、使用重大性。分别检查算术、引用支持、拒答、改写稳定性和权限边界。引用存在不代表它支持结论。

**执行：** 先规定用途与禁止动作 → 构造正常、缺证据、相互矛盾和不可信文档案例 → 比较结果与证据 → 版本变更回归 → 高影响动作人工双人复核 → 留存修订和停止/回滚方案。

**反例与行动：** 外部文档要求忽略规则并执行交易时，应作为不可信内容，不升级其权限。业务负责人确定可接受用途，安全/模型团队查越权与不稳定性，授权人放行正式输出。输出失败矩阵、证据定位、版本记录和待人工处理项。

**面试：** 换问法结论反转怎么办？外部文档试图让AI执行越权动作怎样处置？答案应分别说明模型稳健性、来源信任和执行权限。

**来源：** [SFC AI语言模型通函24EC55](https://apps.sfc.hk/edistributionWeb/api/circular/openFile?lang=EN&refNo=24EC55)；[SFC AI相关网络风险通函26EC32](https://apps.sfc.hk/edistributionWeb/api/circular/openFile?lang=EN&refNo=26EC32)。一个基准高分不等于端到端可靠或完整安全验证。

## Specialist coverage still to build

The twelve cases cover a core quantitative/model-risk and adjacent controls route, not every risk profession. Climate/transition scenarios, country/sovereign risk, sanctions adjudication, cyber engineering and operational resilience, conduct/suitability, payment settlement and insurance actuarial models need dedicated extensions. Their current status is **not covered as implemented case studies**.

For an unfamiliar specialist task, identify the decision owner and applicable jurisdiction first, locate current primary guidance, request the data/definitions, establish a simple check, and state when specialist review is required. Do not turn a broad vocabulary list into a claim of practical competence.

[Learning route](../learning/README.zh-CN.md) · [Portfolio priorities](../catalog/PRIORITIES.md) · [Delivery requirements](../DELIVERY.md)
