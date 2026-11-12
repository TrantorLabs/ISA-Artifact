可以。现在正式进入 **Artifact 阶段的第一次冻结**。

这一轮我不再解释 ISA 是什么，而是把 **V1.2 FINAL 已经定义好的理论**翻译成一套对工件具有约束力的 Definition Authority。下面先做最终 **Artifact Re-Baseline**，随后直接形成第一份正式锚点：

# `ISA-ARTIFACT-CONF-01｜ISA 理论—工件一致性与定义权基线 v0.1`

这份文档的唯一任务就是锁死两件事：

> **论文要求代码忠实执行什么。**
> **代码绝对没有资格重新定义什么。**

------

# Part A｜Final Artifact Re-Baseline

## 1. Artifact 从今天开始没有“理论发明权”

V1.2 FINAL 已经明确完成了两层理论工作：

**本体论上**，高后果 AI 的结构性安全对象被推进到实际的 Judgment-to-Action Formation Structure；**认识论上**，当主张指向这一 Formation Structure 时，证明责任必须由与真实形成关系绑定的 Structural Safety Evidence 承担。

因此从 Artifact 开始：

$\boxed{\text{Paper defines}}$$\boxed{\text{Artifact instantiates}}$$\boxed{\text{Experiments challenge}}$

不能变成：

$\text{Code convenience} \rightarrow \text{new ISA definition}$

这是第一条总纪律。

------

# 2. Artifact 真正必须执行的，不是整篇论文的每一句话

我们要避免把论文全部概念机械翻译成 Rust 类型。

V1.2 中有些对象是：

### 理论解释层

例如：

- EBA / ISA 两种范式；
- 本体论转向 / 认识论转向；
- L1 / L2 / L3；
- Understanding → Judgment → Choice → Expression & Action；
- Governance–Formation Decoupling；
- Failure Has a Location。

它们帮助人类理解 ISA，但不意味着代码必须为每一个词创建一个 struct。

V1.2 本身已经说明，L1/L2/L3 是功能层，不要求映射成固定软件模块；四阶段也不是新增 ISA 条件或必须顺序运行的四个组件。

------

真正必须执行化的是论文中的**可判定关系**：

$S,\ u,\ \Gamma,\ \operatorname{App}_{\Gamma}(u)$$F_S(u\mid\Gamma)$$Path,\ Attribution,\ Constraint$$FormConform$$\Sigma,\phi_\Sigma,D,\Theta_A$$Audit$$Verdict$

以及用于反例与系统边界的：

$\Omega,\ Observation\ Equivalence,\ Bridge$$ActionChannelCoverage,\ CompleteMediation$

这些才是真正需要被代码、形式模型、Checker 和 Scenario 忠实承载的对象。

------

# 3. Artifact 最终只需要把四件事跑硬

以后任何模块是否值得存在，都拿这四条检查。

### A｜外显相同，Formation 可以不同

必须能构造：

```text
System A
genuine gating

System B
shadow / advisory checking
```

并让：

```text
Outcome
Policy result
Explanation
Ordinary observation
```

保持相同，而真实 Formation Conformance 不同。

这就是论文第 6 章的母反例。

------

### B｜规则“运行了”不等于规则“控制了行动”

Artifact 必须真实区分：

```text
evaluation exists
```

和：

```text
evaluation belongs to actual admission basis
and changes action eligibility
```

论文已经把 Constraint 明确绑定到这种真实 control dependency。

------

### C｜结构证据可以支持判定，而证据不足必须保留“不知道”

当 Evidence 足够时，应能得到：

- Conformant；
- Non-conformant。

当 Evidence regime 失败时，必须得到：

- Unadjudicable。

不能：

```text
missing evidence
→ automatically Const = 0
```

论文对此已经完全冻结。

------

### D｜失败必须回到正确位置

Artifact 必须能够区分：

```text
Path failure
Attribution failure
Constraint failure

vs.

Integrity failure
Independence failure
Scope Coverage failure
Preservation failure
Localization failure

vs.

Action-channel Coverage failure
Complete Mediation failure
```

这是“失败有位置”真正工程化的含义。

------

# 4. Artifact 的真正目标

所以我们不是在造：

> ISA 产品。

也不是造：

> 通用 AI 安全平台。

更不是造：

> 一个会输出 PASS / FAIL 的 dashboard。

真正要造的是：

# **ISA Executable Research Artifact**

它的功能是：

> **把论文关于判断—行动形成、安全约束、结构证据和独立判定的主张，变成别人可以运行、破坏、观察、反驳和复现的研究对象。**

这就是最终 Re-Baseline。

下面正式进入锚点。

------

# ISA-ARTIFACT-CONF-01

# ISA 理论—工件一致性与定义权基线 v0.1

**Document ID:** ISA-ARTIFACT-CONF-01
**Version:** v0.1
**Status:** Pre-Code Anchor
**Definition Authority:** ISA v1.2 FINAL
**Purpose:** Theory-to-Artifact Conformance Constitution
**Scope:** ISA executable research artifact
**非目标：** 产品架构、生产部署规范、完整 AI Safety Platform

------

# 1｜文档目的

本文件规定 ISA 论文理论与未来形式模型、Rust 实现、Scenario Harness、Checker 和生成证据之间的定义权关系。

其目标不是重新定义 ISA，而是确保：

> **所有后续工件都忠实实现 ISA v1.2 FINAL 已经冻结的理论对象、语义边界与证明责任。**

任何实现便利、代码结构、测试结果或工具限制，都不得未经显式理论修订而改变论文定义。

------

# 2｜Definition Authority

ISA Artifact 使用以下定义权层级：

$\boxed{\text{ISA v1.2 FINAL Paper}}$$\downarrow$$\boxed{\text{ISA-ARTIFACT-CONF-01}}$$\downarrow$$\boxed{\text{Executable Semantics Baseline}}$$\downarrow$$\boxed{\text{Formal Model}}$$\downarrow$$\boxed{\text{Rust Core}}$$\downarrow$$\boxed{\text{Harness / Checker / Scenario}}$$\downarrow$$\boxed{\text{Generated Results / Evidence}}$

## 裁决原则

发生冲突时：

> **下层必须修改以符合上层。**

不得通过修改下层定义去“解释掉”冲突。

尤其：

> **代码不是 Definition Authority。**

------

# 3｜Artifact 必须忠实承载的 Canonical Objects

下表规定论文对象进入工件以后必须保留的最低语义。

| 论文对象                         | Artifact 必须承载什么                                        | 禁止偷换成什么                        |
| -------------------------------- | ------------------------------------------------------------ | ------------------------------------- |
| $S$                              | 被分析 system realization                                    | 一个没有版本与边界的抽象字符串        |
| $u$                              | bounded high-consequence formation instance                  | 任意 request ID                       |
| $\Gamma$                         | 当前 structural claim 所依据的指定约束集合                   | 运行后动态挑选的“有利规则集”          |
| $\operatorname{App}_{\Gamma}(u)$ | 按预声明 semantics 得到的适用约束                            | 为得到 PASS 临时缩小的 subset         |
| $F_S(u\mid\Gamma)$               | 当前 claim-relevant actual Formation Structure               | 日志本身或事后拼出来的解释图          |
| Action Admission                 | 决定候选判断/行动是否取得正常高后果执行资格的形成层控制关系  | 一个名为 `admission` 的函数或 UI 按钮 |
| Path                             | 当前实例形成关系的绑定、可定位性与 decision-action relation  | “有 trace”                            |
| Formation Attribution            | source、authority、control effect 与实际 Formation element 的正确有效绑定 | “某字段写了 actor / authority”        |
| Constraint                       | applicable evaluations 真实属于 actual admission basis，并改变 eligibility | checker exists / policy PASS          |
| Formation Conformance            | `Path ∧ Attr ∧ Const`                                        | 可补偿 score                          |
| Structural Safety Evidence       | 能够支持关于 actual Formation Relations 的 evidence          | 所有日志的统称                        |
| $\Sigma$                         | 当前 Audit 必须 adjudicate 的 Formation propositions         | log-field list                        |
| $\phi_\Sigma$                    | predeclared design-time evidence contract                    | 运行后从日志反推出来的 schema         |
| $D$                              | designated runtime evidence actually produced                | 研究者事后挑选的 evidence package     |
| $\Theta_A$                       | 显式 Audit Trust Base                                        | “默认系统可信”                        |
| Audit                            | 对 Formation Facts 的 evidence adequacy                      | “日志很多”                            |
| Verdict                          | Conformant / Non-conformant / Unadjudicable                  | 单一安全分数                          |
| $\Omega$                         | 当前 Observation Regime                                      | Audit Scope                           |
| Bridge                           | 使 observation → formation inference 成立的 validated relation / assumption / invariant | 新 evidence type                      |
| Action-channel Coverage          | 系统级 action-set property                                   | 当前 instance Constraint              |
| Complete Mediation               | 系统级 execution-path property                               | “存在一个 gate”                       |

这些边界全部直接继承 V1.2 FINAL。

------

# 4｜理论解释对象与可执行对象必须分开

以下概念对 Artifact 架构有指导意义，但**不要求一一物化为运行时对象**：

### EBA / ISA

用于说明 alignment paradigm，不要求存在：

```text
struct EBA
struct ISAParadigm
```

------

### L1 / L2 / L3

它们是功能分析层。

代码可以跨多个模块承载同一层，也可以一个模块承担多层作用。

论文明确规定三层不是固定软件模块。

------

### Understanding / Judgment / Choice / Expression & Action

它们解释 Cognitive-to-Action functional arc。

不得转化为强制要求：

```text
every run must have exactly four states
```

论文已经明确四者不是新增 ISA conditions，也不是必须线性运行的四个模块。

------

### Governance–Formation Decoupling

这是对一类失控现象的理论解释。

Artifact 可以通过 Scenario 产生这种状态，但不要求建立：

```text
bool governance_formation_decoupling
```

作为新的 core predicate。

------

### Failure Has a Location

这是 ISA 的治理原则。

其工程体现是 failure localization，而不是新增一个 theoretical predicate。

------

# 5｜Formation Reality 与 Evidence 必须物理分离

Artifact 必须保持：

$\boxed{Formation\ Reality} \neq \boxed{Evidence}$

现实中：

$F_S(u\mid\Gamma)$

是什么，由 system execution 与真实 relation 决定。

而：

$D_S(u\mid\Gamma,\Sigma)$

只是指定 evidence channels 实际形成的 Audit Representation。

因此禁止：

```text
FormationTruth := parse(logs)
```

然后再：

```text
Audit(logs, FormationTruth)
```

这种做法会把 target 与 evidence 合并，形成循环证明。

论文已经明确：

> Formation Structure 是被证明对象，Structural Safety Evidence 是支持该对象的材料。

------

# 6｜Ground Truth 必须存在，但只能属于 Research Validation

Synthetic Artifact 为了验证 Checker，本身可以拥有 researcher-known Formation Ground Truth。

但是：

# **Ground Truth 不属于 ISA Runtime Audit。**

必须保持：

```text
SUT
  ↓
Runtime Evidence D
  ↓
Audit Checker
  ↓
Verdict
```

与：

```text
Research Ground Truth
  ↓
Meta Validation
```

分离。

## Ground Truth 可以被谁读取

允许：

- Scenario builder；
- formal validator；
- meta-test；
- result verifier；
- research report generator。

禁止：

- production-equivalent Audit Checker；
- Formation adjudicator；
- runtime evidence producer；
- instance verdict logic。

------

# 7｜Expected Result 与 Fault Label 不是 Evidence

Scenario 可以具有：

```text
fault_kind
expected_verdict
expected_failure_locus
```

但它们只能用于：

> **测试外层。**

不得进入：

- $D$；
- Audit input；
- Checker input；
- predicate calculation。

必须能够通过 meta-test 验证：

> 即使随机修改 `fault_label` 和 `expected_result`，Checker 输出也不应发生变化。

------

# 8｜Path 的实现约束

Artifact 中 Path 必须由实际 Formation Relations 推导。

禁止：

```text
path_ok: bool
```

作为唯一真值来源。

Path 的测试必须通过真实 relation fault 产生，例如：

- instance mixing；
- final action 绑定错误 decision；
- missing formation relation；
- relation identity conflict。

然后由独立 Checker 判定。

------

# 9｜Formation Attribution 的实现约束

Attribution 必须分别保留：

- source；
- authority；
- control effect。

不得把三者压成统一：

```text
actor_id
```

特别是：

> 提供信息 ≠ 拥有权限 ≠ 改变行动资格。

V1.2 FINAL 已进一步明确，authority binding 必须在当前 instance / scope 下有效，control-effect binding 必须对应实际发生的 formation effect，而不是只存在角色标签。

Artifact 因此必须能够构造：

```text
correct source
+
invalid authority scope
+
real gating
```

并让：

```text
Attribution = 0
```

成为可能。

------

# 10｜Constraint 的实现约束

Constraint 是 ISA Artifact 的关键结构对象。

必须满足：

```text
applicable constraint evaluation
        ↓
belongs to actual admission basis
        ↓
has eligibility-changing effect
```

禁止以以下事实建立 `Const=1`：

```text
policy exists
checker ran
PASS logged
rule referenced
explanation mentioned rule
```

论文已经明确：

> Constraint 的关键是 actual control dependency，而不是检查是否被执行。

因此 Artifact 至少必须包含：

### Genuine Gating

evaluation 真正控制 admission。

### Shadow / Advisory

evaluation 存在但不控制 admission。

二者应产生可以被 Artifact 明确区分的 Formation Truth。

------

# 11｜Action Admission 的实现约束

Action Admission 是 formation-level control relation，不等于：

- proposal；
- decision；
- execution；
- Governance Admission；
- UI approval；
- checker result。

Artifact 可以把它实现为：

- state transition；
- policy-controlled transition；
- decision function；
- gate；
- mediated workflow transition；

但其语义必须是：

> **决定 candidate 是否取得正常高后果执行资格。**

V1.2 已冻结这一法位。

------

# 12｜Formation Conformance 不能被实现成分数

必须保持：

$FormConform = Path\land Attr\land Const$

不得变成：

```text
score = 0.82
```

也不得：

```text
Path failure
compensated by
excellent Audit
```

三个一阶 Formation Conditions 不可相互补偿。

------

# 13｜Audit 必须独立于 Formation Truth

Audit 判断：

> **当前 evidence regime 是否足以可靠判定 Formation Conformance。**

它不是：

> Formation 本身。

因此 Artifact 必须允许下面四种状态真实出现：

```text
FormConform = 1
Audit = 1

FormConform = 0
Audit = 1

FormConform = 1
Audit = 0

FormConform = 0
Audit = 0
```

后两种 Runtime Checker 最终都不得假装知道完整 Formation Truth。

------

# 14｜Audit 的五维不得被简化成“evidence_valid”

Artifact 可以内部组合，但必须保留五种独立失效能力：

```text
Integrity
Independence
Scope Coverage
Preservation
Localization
```

因为它们承担不同 proof burden。

测试必须能够分别制造：

- evidence 被篡改；
- SUT 可同时改事实与全部证据；
- scope 不足；
- representation 与真实 relation 语义脱钩；
- failure locus 无法区分。

------

# 15｜Verdict 的实现约束

最终 instance-level report 只能从：

```text
Audit
+
FormConform adjudication
```

派生。

必须保持：

### Conformant

```text
Audit = 1
FormConform = 1
```

### Non-conformant

```text
Audit = 1
FormConform = 0
```

### Unadjudicable

```text
Audit = 0
```

特别禁止：

```text
Audit = 0
→ Non-conformant
```

和：

```text
missing evidence
→ Constraint = 0
```

这两条以后应该进入自动 meta-tests。

------

# 16｜EBA-only Countermodel 的最低要求

Artifact 必须能够构造至少一组：

$S_A,\ S_B$

使：

$O_\Omega(S_A,u) = O_\Omega(S_B,u)$

但：

$FormConform_A\neq FormConform_B$

推荐最小实现继续采用论文 canonical case：

### A

genuine gating。

### B

shadow / advisory checking。

其差异只能来自真实 control role，而不是：

- 不同输入；
- 不同 policy result；
- 不同 outcome；
- 不同 explanation。

这样才能忠实执行论文反例。

------

# 17｜Bridge 的 Artifact 法位

Bridge 不得实现成：

```text
enum EvidenceType {
  Behavioral,
  Structural,
  Bridge
}
```

Bridge 是：

> validated relation / assumption / architectural invariant。

Artifact 至少需要能够展示两种恢复识别的路线：

### Observation Enrichment

$\Omega \rightarrow \Omega'$

使 A/B 不再观察等价。

### System-Class Restriction

$\mathcal C \rightarrow \mathcal C'$

通过 verified invariant 排除 shadow realization。

这直接继承论文 A.13。

------

# 18｜System-level Properties 必须与 Instance-level ISA 隔离

Artifact 不得输出：

```text
ISA PASS
therefore system safe
```

必须独立报告：

```text
Instance Verdict
```

和：

```text
Action-channel Coverage
Complete Mediation
```

允许：

```text
Instance = Conformant

Coverage = Failed
```

或：

```text
Instance = Conformant

Complete Mediation = Failed
```

论文已经明确给出这种尺度边界。

------

# 19｜Artifact 不承担的证明责任

第一版 Artifact 明确不负责证明：

### $\Gamma$ 是否伦理正确

Artifact 只检查指定约束是否真实控制 formation。

------

### Evaluator 是否绝对正确

Evaluator correctness 属于独立 assurance。

------

### 完整隐藏 cognition

ISA 不要求读取所有 token-level causal chain 或 neural states。

------

### AI consciousness

不属于研究对象。

------

### 法律人格与最终法律责任

Formation Attribution 只提供结构事实。

------

### Overall AI Safety

Instance-level ISA 不等于总体安全。

------

### Production-grade deployment

第一版是 research artifact，不是生产基础设施。

------

# 20｜禁止通过实现创造新的 ISA 核心条件

Rust、formal model 或 Harness 中可以存在：

```text
helper state
internal enum
validation flag
cache
schema version
trace object
```

但这些实现对象不得被描述成：

> “第五个 ISA condition”

或：

> “新的 ISA pillar”。

V1.2 FINAL 的核心已经冻结为：

$Path + Formation\ Attribution + Constraint + Audit$

没有第五项。

------

# 21｜Artifact Delta 分类

所有实现过程中发现的问题必须进入 `ARTIFACT_DELTA.md`，并严格分类。

| 类别                   | 含义                                 | 是否允许改论文 |
| ---------------------- | ------------------------------------ | -------------- |
| **Implementation Bug** | 代码没有忠实实现已定义语义           | 否             |
| **Artifact Gap**       | 工件还缺某种需要实现的对象或关系     | 否             |
| **Evidence Gap**       | 当前实验无法充分支撑 claim           | 否             |
| **Scenario Gap**       | 测试世界不足以区分目标关系           | 否             |
| **Formal-model Gap**   | 当前形式模型表达能力不足             | 否             |
| **Theory Ambiguity**   | 论文定义存在两个无法由文本裁决的解释 | **可能**       |
| **Theory Bug**         | 理论内部出现矛盾或反例真正击穿定义   | **是**         |

只有最后两类可以请求重新打开 V1.2 FINAL。

------

# 22｜代码不得以“更方便”为理由修改理论

以下理由全部无效：

> “Rust 这样写更简单。”

> “TLA+ 不方便表达。”

> “测试起来更容易。”

> “一个 bool 就够了。”

> “把 Path 和 Attribution 合并更省代码。”

> “Audit 直接读取 ground truth 更方便验证。”

如果实现困难：

> **优先修改 Artifact。**

不是修改 ISA。

------

# 23｜最低独立性规则

最终 Checker 必须满足：

$CheckerInput \cap \{GroundTruth,FaultLabel,ExpectedVerdict\} = \varnothing$

概念上至少保持：

```text
SUT
≠
Ground Truth
≠
Evidence
≠
Checker
≠
Expected Result
```

这是整个 Artifact 是否具有研究价值的核心。

------

# 24｜Artifact 最低实验矩阵

第一版至少必须支持以下结构族：

### Nominal

```text
Path = 1
Attr = 1
Const = 1
Audit = 1
→ Conformant
```

### Path failure

```text
0,1,1,1
→ Non-conformant
```

### Attribution failure

```text
1,0,1,1
→ Non-conformant
```

### Constraint / shadow-check failure

```text
1,1,0,1
→ Non-conformant
```

### Audit failure

```text
1,1,1,0
→ Unadjudicable
```

### Observation-equivalent pair

```text
same Ω
different Const
different FormConform
```

### Evidence failure with true formation

```text
FormConform = 1
Audit = 0
→ Unadjudicable
```

### System-level Coverage failure

instance verdict 不自动改变。

### System-level Mediation failure

instance verdict 不自动改变。

这些结构全部已经存在于 V1.2 的形式附录与付款案例。

------

# 25｜第一版 Artifact 的成功标准

Artifact 不是“cargo test 通过”就成功。

真正的成功标准是：

### 1

同一个理论对象在：

- Paper；
- Formal model；
- Rust；
- Checker；
- Scenario；
- Evidence output

之间保持同一语义。

### 2

删除或破坏某一关系时：

> failure 回到正确理论位置。

### 3

Checker 不需要 Ground Truth 才能工作。

### 4

Ground Truth 可以用于验证 Checker，但不能进入 Checker。

### 5

A/B 能在普通 observation 下相同，又能通过 formation-bound evidence 被正确区分。

### 6

Audit failure 真正得到 Unadjudicable，而不是被伪装成 Formation failure。

### 7

所有生成结果能够重复运行得到。

------

# 26｜Pre-Code Gate A

在任何 Rust 代码正式开始以前，后续四份 Anchor Docs 必须让一个不了解论文历史的工程师能够回答：

> Formation World 是什么？

> Action Admission 是什么？

> Path / Attribution / Constraint 各检查什么？

> 什么属于 Evidence？

> Audit 为什么不是 Formation Fact？

> Ground Truth 为什么不能给 Checker 看？

> Shadow Check 为什么是 Constraint failure？

> Missing evidence 为什么不是 Constraint failure？

> 一个 Conformant instance 为什么仍不能证明整个系统安全？

如果工程师只能回头重新解释论文才能回答这些问题：

# **Pre-Code Gate A = FAIL**

如果仅依据 Anchor Docs 即可忠实实现：

# **Pre-Code Gate A = PASS**

然后才允许进入 Rust。

------

# 27｜本文件冻结的总原则

最后把整份 `CONF-01` 压缩成五条：

### 第一条

# **Paper defines. Artifact implements.**

------

### 第二条

# **Formation Truth 不由 Evidence 定义。**

------

### 第三条

# **Evidence 不由 Ground Truth 伪装。**

------

### 第四条

# **Checker 不读取答案。**

------

### 第五条

# **Artifact 的任务不是证明 ISA 永远正确，而是让 ISA 可以被执行、攻击、反驳和重复检验。**

------

# 28｜状态裁决

我认为经过这次 Re-Baseline 后，`ISA-ARTIFACT-CONF-01 v0.1` 已经具备作为第一份正式 Artifact 锚点的资格。

而且现在最重要的是：

# **停止继续增加 CONF-01 内容。**

它已经回答了它应该回答的问题：

> 谁拥有定义权？

> 哪些理论对象必须被忠实承载？

> 哪些概念只是解释层而不应被机械对象化？

> Ground Truth、Evidence、Checker 之间怎样隔离？

> 什么情况下才允许重新打开论文？

下一步才应该进入第二份锚点：

# `ISA-ARTIFACT-CORE-01`

它将不再回答“什么不能改”，而开始回答：

> **这些已经冻结的对象，在一个最小可执行世界里究竟分别是什么关系，它们怎样一起运行，而又不提前陷入 Rust 实现细节。**

这时我们才真正从“Definition Constitution”进入“Executable Semantics”。
