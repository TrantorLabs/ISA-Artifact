# Artifact Delta：实际实现差额账本

本文记录实现过程中必须澄清的差额。它不是新锚点，也不修改 ISA v1.2 FINAL。六份原始设计文档保持原样。

| ID | 类型 | 实际问题与处理 | 状态 / 影响 |
| --- | --- | --- | --- |
| D01 | Implementation decision | IMPL 与 Gate A 覆盖早期 CONF 的单线定义层级。两个 workspace 和独立 formal 目录落实分支结构。 | 已实现；无论文变化 |
| D02 | Artifact clarification | CORE 的顺序图把 Evidence 放在执行之后，容易被读成事后生成。实现采用 EventSink 随执行采集，事后只封存与汇总，Oracle 不参与采集。 | 已实现；时间语义回归论文 |
| D03 | Artifact clarification | CORE 的“改变 evaluation semantics”不能解释为实验中改变 Γ 来证明控制。实现固定准入语义，仅干预评价值，枚举有限向量检验真实资格依赖。 | 已实现；控制不是读取日志 |
| D04 | Scenario correction | EVAL 的 E04-P 同时要求 Formation 全真，又用真实 advisory 作例子。该例混合两种变化。实现保持 genuine world，单独让序列化把 AND 写成 OR；独立监测摘要保留原实际程序。 | 已实现；明确修正评测例子，不改论文 |
| D05 | Artifact boundary | Audit 五维是不同证明责任，不等于任意故障只会使一个维度失败。缺失关键材料可同时触发 Coverage/Preservation。报告保留全部失败位置，不为了单一标签伪造真值。 | 已实现 |
| D06 | Evidence boundary | 一个进程不能凭空检测完全不可观察的信任根失陷。采用显式 synthetic collector root；独立封存承诺支持当前证据。FQ5-TRUST-BREACH 和单测保留“根与证据一起被伪造”导致 false certainty 的反例。 | 范围外限制保留；不声称解决 |
| D07 | Isolation boundary | 独立进程不等于恶意主机沙箱。实现隔离输入/环境/工作目录与编译依赖，并做标签变异；没有主机权限隔离、seccomp 或硬件证明。 | 研究数据流隔离已实现；生产安全不声称 |
| D08 | Formal refinement | 仅观察程序控制关系不能证明 Path/Attr；FQ2-WEAK 为 SAT。完整有限桥接包含所需绑定与程序的可信表征。FQ3 用具体绑定与 AND 构造器，并单独检查非空和合法拒绝。 | 已检验；不把局部桥接扩成全局证明 |
| D09 | Implementation profile | 标准库 Rust + ISA/1 文本协议减少下载依赖。执行语义限定单实例、四个布尔检查、两项授权和有限 DAG；Scope/Trust 是声明的参考配置，不是通用保证平台。 | 已实现的有界实例，不是穷尽所有实现 |
| D10 | Evidence Gap | 当前机器没有 rustc/cargo/rustfmt，网络下载受阻。Rust 编译、测试、跨语言对照和 Rust 形式见证重放均未执行。 | OPEN；阻止 release_ready=true |
| D11 | Model scope | Z3 两组评价模型与四评价 runtime 不是逐状态同一个模型。FQ1 可映射并重放，完整状态精化未建立。 | 明示边界；禁止声称全量等价证明 |
| D12 | Implementation bug fixed | 参考世界最初保留可变输入引用；修改输入可能反向改写 Oracle 事实。现于 Run 创建时深拷贝 Spec，新增不可回写测试。Rust Run 本来保存 clone。 | 修复；测试实际状态见验证日志 |
| D13 | Evidence separation | 当整个 Audit 无法成立，本参考 Checker 保守地将 Formation 诊断留为 not_adjudicated，不用局部可疑证据凑成总体结论。 | 有界操作策略；不改变三种 Verdict |
| D14 | Implementation bug fixed | E09 的实例绕过标准付款 gate，但系统图最初只加 batch 旁路。现按实际执行端点增加 standard 旁路，补充跨尺度一致性测试，并归档系统图证据而不只保存判定。 | 修复；无论文变化 |
| D15 | Implementation bug fixed | 已补足 context 的 system/version/scope/boundary/trust-domain 等非空前提检查，防止契约不完整但摘要被重新封存后继续给出确定结论；新增逐字段缺失回归测试。 | 修复；不新增实例 Verdict |


## 不变项

没有编辑论文，没有增加第五个 ISA 形成条件，没有把系统级覆盖/中介并入实例 ISA，没有让 Oracle 为 Checker 提供答案，没有把来源标签或 `complete=true` 当成真实保证。

## 对假定的处理

预声明 context 和 collector seal 是调用方确认的可信输入；其真实性与完整性不由这些文件自己证明。校验和只建立“与可信封存相符”。本包不提供可抵御任意离线伪造的生产证书体系。

## 发布裁决

本次交付是可检查的源码和已执行的参考/形式证据包。**D10 未关闭前，不应将其标为 Rust 已验证正式发布。** 完整门禁和 CI 均把这一要求写成机器状态，而不是靠说明文字掩盖。
