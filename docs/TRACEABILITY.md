# 论文—锚点—实现—证据映射

以 ISA v1.2 FINAL 为最高定义依据。原始锚点逐字保留；本表只描述有限参考实现的落点，不创建新的理论条件。

| 论文与锚点对象 | 实际实现位置 | 定向验证 | 结果位置 |
| --- | --- | --- | --- |
| S/u/Γ 与预声明适用性 | `isa-engine::context/run`、core `applicable` | E13 合法不适用；M1 非法缩减 | reference/cases、matrix |
| Formation 与六组关系 | `isa-engine::Spec/Run`，执行事件 | E00、E01、E02-S/A/E | research-only 原始事件与 Oracle |
| Action Admission 实际控制 | engine 递归 DAG 求值；checker 独立自底向上求值及有限向量遍历 | E03-S、E03-B、E12；只读取不控制的单测 | 场景报告、测试日志 |
| Path / Attr / Const | evidence-only `query_values`；research Oracle 直接从运行状态独立求值 | 三类形成失败及四个删除见证 | reference/matrix、formal FQ4 |
| φΣ 与指定 D | context `requires.*`；流式 Collector；上下文承诺 | M2-CONTRACT、M2-CHERRY | 场景证据与报告 |
| Audit 五维 | checker 分维检查；Oracle 研究层审计现实 | E04-I/N/S/P/L、E10 | report 的 audit 与 issues/lineage |
| 三种 Verdict | Checker 派生函数，不含期望标签 | 22 场景；E11-BLIND-SHADOW | reference/summary 与逐例报告 |
| Ω0 观察等价 | `isa-engine::baseline`，参考同名投影 | E00/E03-S 组成 E05 配对实验 | reference/pair.json、formal/FQ1.txt |
| Ω1 结构观察 | 合法指定依赖/绑定证据；非目标上下文保持相同 | E06 配对恢复，弱桥接负面对照 | pair.json、FQ2、FQ2-WEAK |
| 架构限制 Bridge | 有限关系构造器，不直接设置符合标签 | FQ3、非空与拒绝见证 | formal/FQ3*.txt |
| Unknown ≠ false | 缺证据时不填写 Formation 真值 | E10、E11，缺字段测试、故意错误 Checker | FQ5/FQ6、mutation-report |
| 系统级 Coverage / Mediation | `isa-checker::system`；参考独立有限图遍历 | E07、E08、E09 | system-report，FQ7/FQ8 |
| 隐藏答案隔离 | 独立 workspace / import 检查 / 子进程 | 标签洗牌、环境污染、实例重命名 | boundary-check、测试日志 |
| 模型→执行见证 | FQ1 控制程序映射，不映射预填真假值 | 独立参考进程重放 | formal/replay.json |

## 评测矩阵的尺度

Ω 是观察制度，不是 Audit 状态。`matrix.csv` 单独给出 observation；E05/E06 是配对实验，复用现有系统而不重复计数。系统级结果单独列出，不能补偿实例级形成失败。

## 有限映射，不是假装整个论文已经被软件穷尽

运行时配置限定为单实例、付款域、至多四项布尔评价、至多 32 条 DAG 指令及两项授权。Scope Coverage 使用固定六组查询与九类证据通道；并非通用 schema 充分性判定器。Authority scope 是封闭参考登记值，不是部署中的身份认证。完整映射与适用限制登记于 Delta。

形式层进一步抽象为两组评价与有限绑定字段。两组评价可对应四项付款检查的两个合取组，FQ1 见证可以重放；不声称已完成形式模型与任意运行时状态的全量精化证明。

## Gate A 的已实现修补

主定义链仍为 Paper → CONF → CORE。FORMAL、EVAL 与实现是分支。Observation 与 Audit 列分离；配对实验的上下文逐字一致；隐藏 Oracle 包含形成真值和审计现实；新增适用性冻结及禁止事后挑证据的检验。代码接受的是这些约束，不继承早期锚点里已被后发裁决覆盖的单线形式权威关系。
