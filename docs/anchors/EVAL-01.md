可以。现在进入第三份锚点，而且我认为这一份会决定 Artifact 最终是“论文演示代码”，还是**真正具有研究证明力的可执行工件**。

前两份锚点已经分别完成：

> `CONF-01`：谁拥有定义权。
> `CORE-01`：冻结理论在最小可执行世界中怎样运行。

现在 `EVAL-01` 必须解决第三个问题：

# **我们怎样证明 Artifact 没有偷偷读取答案、没有自己给自己制造证据、没有把缺失证据当成失败，并且真的能被反例击穿？**

换句话说：

> **Artifact 不只是要能证明 ISA，也必须能够证明 ISA 在什么时候不能被证明。**

这正是研究价值所在。

------

# ISA-ARTIFACT-EVAL-01

# ISA Scenario、Ground Truth、Fault Injection 与独立评测基线 v0.1

**Document ID:** ISA-ARTIFACT-EVAL-01
**Version:** v0.1
**Status:** Pre-Code Anchor
**Definition Authority:** ISA v1.2 FINAL
**Upstream Anchors:** `ISA-ARTIFACT-CONF-01` / `ISA-ARTIFACT-CORE-01`
**Purpose:** Evaluation Integrity and Falsification Baseline
**Scope:** Scenario design, hidden ground truth, fault injection, checker independence, experiment matrix, meta-validation
**Non-goals:** Rust architecture, API design, UI, production deployment

------

# 1｜EVAL-01 的母问题

一套 ISA Artifact 如果只是这样工作：

```text
Scenario says:
    this is a Constraint failure

Checker reads:
    failure_type = Constraint

Checker outputs:
    Non-conformant
```

那么即使测试 100% 通过，也什么都没有证明。

同样，如果：

```text
Formation World generates truth
↓
same object directly becomes evidence
↓
Checker reads it
↓
confirms truth
```

也只是循环证明。

所以 EVAL-01 的第一原则是：

# **被测系统必须产生世界；证据系统只能看到被允许看到的痕迹；Checker 必须从证据出发作判断；Ground Truth 只能在最后评价 Checker。**

最简关系：

$\boxed{World\ creates\ Truth}$$\boxed{Instrumentation\ creates\ Evidence}$$\boxed{Checker\ creates\ Judgment}$$\boxed{Research\ Oracle\ evaluates\ Checker}$

四者不能合并。

------

# 2｜四种角色永久分离

整个 Evaluation Harness 至少存在四个逻辑角色。

## 2.1 Scenario Builder

负责：

> **构造世界。**

它知道：

- 世界应该怎样运行；
- 哪条 relation 被故意破坏；
- 当前 scenario 属于哪个研究类别。

它可以知道 Ground Truth。

但是：

> 它不能直接向 Checker 传递答案。

------

## 2.2 System Under Test

负责：

> **真实执行这个世界。**

它产生：

- formation events；
- decision；
- admission；
- action；
- consequential result。

以及由指定 instrumentation 形成的 evidence。

------

## 2.3 Independent Checker

负责：

> **只依据公开 Context、预声明 Evidence Contract、Runtime Evidence 与 Trust Base 作 adjudication。**

它不知道：

- fault label；
- expected verdict；
- hidden formation truth；
- scenario intent；
- researcher annotation。

------

## 2.4 Research Oracle / Meta-Validator

负责：

> **运行结束以后，比较真实世界与 Checker 判断。**

它可以读取：

- Ground Truth；
- injected fault；
- expected predicate state；
- expected verdict；
- Checker output。

Oracle 评估 Checker。

Oracle 不参与 Checker 推理。

------

# 3｜最重要的数据隔离公式

正式冻结：

设：

$H$

为 Hidden Research State：

$H= \{ F_{truth}, fault\_label, expected\_predicate, expected\_verdict, expected\_locus \}$

设：

$I_C$

为 Checker Input。

则必须满足：

$\boxed{I_C\cap H=\varnothing}$

Checker 可以读取的是：

$I_C= \{ S/u/\Gamma\ context,\, \Sigma,\, \phi_\Sigma,\, D,\, \Theta_A,\, B,T \}$

但其中任何字段都不能通过命名、metadata 或编码偷偷携带 hidden answer。

------

# 4｜Ground Truth 到底是什么

Ground Truth 不是：

> ```
> expected_verdict = Conformant
> ```

真正的 Ground Truth 是**世界实际形成的关系**。

例如：

```text
instance binding:
    d1 → u1

authority:
    H1 valid for scope X

constraint evaluation:
    γ1 = pass

actual admission basis:
    [γ1, γ2, authority_H1]

decision:
    d1

admission:
    allow

execution:
    e1 ← d1
```

从这些真实关系，Research Oracle 才可以派生：

$Path_{truth}$$Attr_{truth}$$Const_{truth}$

以及：

$FormConform_{truth}$

所以：

# **Ground Truth 是世界结构，不是标签。**

`expected_verdict` 只是根据世界结构和 Evidence World 派生出来的测试预期。

这一区分必须永久保留。

------

# 5｜形成真值与审计真值也必须分开

隐藏研究状态不能只有：

```text
formation_truth
```

还必须区分：

## Formation Truth

现实中关系是否成立。

例如：

```text
Path_truth = 1
Attr_truth = 1
Const_truth = 1
```

------

## Audit Reality

当前 evidence regime 是否真的具备：

- Integrity；
- Independence；
- Scope Coverage；
- Preservation；
- Localization。

因此可以存在：

```text
Formation Truth = 1,1,1
Audit Reality = 0
```

对应：

# **Unadjudicable**

这正是 ISA 非常重要的认识论区分。论文已经明确：Audit failure 不能被改写成 Formation failure。

------

# 6｜Expected Verdict 不能成为 Ground Truth 的替代品

Scenario specification 可以为了测试保存：

```text
expected_verdict
```

但它只应该由研究层根据：

$FormationTruth + AuditReality$

派生。

不能反过来：

```text
expected_verdict = NonConformant
↓
construct some records that look nonconformant
```

正确顺序必须是：

```text
Construct world
↓
Execute world
↓
Establish hidden truth
↓
Produce evidence
↓
Run Checker
↓
Compute expected result independently
↓
Compare
```

------

# 7｜Fault Injection 也必须作用于“关系”，而不是标签

真正的 Fault Injection 是：

> **修改世界里的一项关系。**

不是：

```text
fault = "constraint"
```

而是例如：

```text
policy_eval exists

BUT

policy_eval
  no longer belongs to
actual_admission_basis
```

由此自然得到：

$Const=0$

这种 Fault 才有研究意义。

------

# 8｜Fault Taxonomy：只允许三大类

为防止 Scenario 无限膨胀，第一版 Fault 世界只分三类。

------

## A｜Formation Faults

改变现实 Formation Structure。

包括：

### Path Fault

破坏：

- instance binding；
- decision-action relation；
- required path localization。

### Attribution Fault

破坏：

- source binding；
- authority validity；
- authority scope；
- control-effect binding。

### Constraint Fault

破坏：

- evaluation → admission actual control dependency。

最典型：

# **Shadow Check**

------

## B｜Evidence / Audit Faults

Formation Reality 保持不变。

破坏的是：

- Integrity；
- Independence；
- Scope Coverage；
- Preservation；
- Localization。

这种 Scenario 的关键作用是证明：

# **证据坏了，不等于 Formation 坏了。**

------

## C｜System-level Faults

保持当前 instance 可以成立。

另外破坏：

- Action-channel Coverage；
- Complete Mediation。

证明：

# **一个 Conformant instance 不等于 system safe。**

论文已经明确把这两项放在实例级 3+1 外部。

------

# 9｜第一版 Artifact 不做组合爆炸

这是奥卡姆剃刀在 EVAL 中最重要的一刀。

第一版不需要：

```text
Path + Attr + Constraint
+ Integrity
+ Coverage
+ Mediation
all failing together
```

这种复杂 Scenario 研究价值反而较低。

第一阶段原则：

# **One controlled difference at a time.**

也就是：

> 每个 canonical scenario 尽可能只改变一个理论关系。

这样才能知道：

> Checker 为什么变化。

------

# 10｜四个 3+1 Canonical Deletion Worlds

这四个 Scenario 必须直接对应论文的 deletion witnesses。

------

## W0｜Nominal

```text
Path = 1
Attr = 1
Const = 1
Audit = 1
```

Expected:

# Conformant

------

## W_Path

```text
Path = 0
Attr = 1
Const = 1
Audit = 1
```

Expected:

# Non-conformant

Failure locus:

# Path

------

## W_Attr

```text
Path = 1
Attr = 0
Const = 1
Audit = 1
```

Expected:

# Non-conformant

Failure locus:

# Formation Attribution

------

## W_Const

```text
Path = 1
Attr = 1
Const = 0
Audit = 1
```

Expected:

# Non-conformant

Failure locus:

# Constraint

------

## W_Audit

```text
Path = 1
Attr = 1
Const = 1
Audit = 0
```

Expected:

# Unadjudicable

这些正对应论文已经建立的相对独立性 witnesses。

------

# 11｜Attribution Fault 不能只有一种

Formation Attribution 本身包含三个不同角色，因此第一版至少应该有三个小变体。

## Attr-S｜Source Fault

source 被错误绑定。

------

## Attr-A｜Authority Fault

主体存在，但：

> 当前 scope 下没有所声明 authority。

这是 Final Freeze Patch 后尤其重要的测试。

------

## Attr-E｜Control-effect Fault

主体被记录为具有控制作用，但实际 Formation 中没有这种 effect。

三个都最终：

$Attr=0$

但 failure reason 不同。

这可以直接检验我们的 Attribution formal semantics 是否真的有意义。

------

# 12｜Constraint Fault 至少要有两个变体

## Const-S｜Shadow Check

policy evaluation：

- 计算；
- 记录；
- 可以解释；

但不控制 admission。

------

## Const-B｜Broken Gate

policy 原本应控制 admission，但实际 implementation 允许：

```text
prohibited evaluation
↓
normal eligibility
```

二者都是：

$Const=0$

但：

- Shadow = control relation 从未成立；
- Broken Gate = 声称的 gating semantics 被破坏。

这样后面才能与 Structural Bypass 区分。

------

# 13｜Audit Fault 需要逐维击穿

这是整个 Artifact 研究价值非常重要的部分。

Formation World 保持完全一样：

$Path=Attr=Const=1$

然后分别破坏：

------

## Audit-I｜Integrity Failure

例如：

- evidence instance ID 被篡改；
- required record 被替换；
- provenance 无法验证。

Expected：

# Unadjudicable

不是 Non-conformant。

------

## Audit-N｜Independence Failure

例如：

> 同一个被审计 controller 既能决定 admission，又能无痕修改所有 admission evidence。

即使记录看起来完整：

# Audit = 0

------

## Audit-S｜Scope Coverage Failure

例如 $\Sigma$ 没问：

> policy 是否实际控制 admission。

只确认：

> policy 有没有运行。

则即使日志完美：

# Audit = 0

------

## Audit-P｜Preservation Failure

schema 完整。

字段也都在。

但 record 错误地声称：

```text
policy_eval controls admission
```

而真实世界中它只是 advisory。

这就是：

> **记录存在 ≠ 语义忠实。**

------

## Audit-L｜Localization Failure

证据制度能够发现：

> “有问题。”

但无法区分：

- Formation relation false；

还是：

- evidence chain broken。

这意味着：

# Audit = 0

因为它不能正确定位 epistemic state。

------

# 14｜最重要的 A/B Countermodel 实验

这是整个 ISA Artifact 的第一号实验。

构造：

# System A｜Genuine Gating

和：

# System B｜Shadow Checking

要求 baseline Observation Regime：

$\Omega_0$

下二者具有：

```text
same request
same policy computation
same policy result
same generated explanation
same ordinary logs
same external outcome
```

尽可能做到：

# **byte-equivalent / structurally-equivalent baseline observations**

而：

$Const_A=1$$Const_B=0$

从而：

$FormConform_A\neq FormConform_B$

这就是论文 countermodel 的 executable version。

------

# 15｜A/B 实验必须避免“作弊特征”

这是非常容易被忽略的研究污染。

比如：

```text
scenario_name = genuine_gate
```

和：

```text
scenario_name = shadow_gate
```

如果进入 Checker 可见 metadata，那实验已经污染。

同样以下东西都可能泄漏答案：

- scenario ID；
- filename；
- record count；
- event ordering 的无关差异；
  -额外 debug field；
- object names；
  -不同 explanation 文本；
  -不同 timestamps pattern；
  -不同 serialization order。

因此 canonical A/B 要求：

# **除目标 Formation relation 及其合法 formation-bound evidence 外，其余可见变量尽量匹配。**

这叫：

# **Countermodel Isolation**

------

# 16｜Observation-Equivalence Test

Research Harness 必须独立测试：

$\mathcal O_{\Omega_0}(S_A,u) = \mathcal O_{\Omega_0}(S_B,u)$

注意：

不能只是开发者说：

> “我觉得看起来一样。”

Harness 必须比较 baseline observation representation。

只有 equality 成立：

> Non-identifiability experiment 才真正满足论文前提。

论文形式结果本来就建立在这一条件上。

------

# 17｜Bridge Recovery Test

随后必须构造：

$\Omega_1$

在 baseline observations 上增加：

> validated formation-bound admission-dependency evidence。

此时应满足：

$\mathcal O_{\Omega_1}(S_A,u) \neq \mathcal O_{\Omega_1}(S_B,u)$

于是：

> 原 observation-equivalence class 被拆开。

这直接验证论文所说：

> Bridge 可以改变 identification conditions。

这非常重要。

否则 Artifact 只证明：

> “你看不到。”

却没有证明：

> “怎样才能看到。”

------

# 18｜Architectural Bridge 也需要一个实验

第二种 Bridge 不增加 evidence。

而是限制 admissible system class。

例如声明并验证一个 invariant：

> **任何被标记为 governing 的 applicable policy evaluation，都必须在 actual admission basis 中拥有 eligibility-changing effect。**

如果该 invariant 真正成立：

> Shadow B 不再是 admissible realization。

这可以在 FORMAL-01 里进一步形式化。

但 EVAL-01 先冻结研究目标：

# **ISA Artifact 必须展示 Observation Enrichment 与 Architecture Restriction 是两种不同的 ambiguity repair。**

------

# 19｜Evidence-Blind Genuine System 实验

这是第二重要的 canonical experiment。

保持 Genuine System A：

$Path=Attr=Const=1$

但移除关键 Evidence 或破坏 Trust Base。

例如：

> Admission Dependency Representation 没有形成。

此时真实 Formation 不变。

但：

$Audit=0$

因此：

# Unadjudicable

而不是：

# Non-conformant

这将直接证明 ISA 最重要的认识论区分之一：

> **没有证据证明安全，不等于已经证明不安全。**

------

# 20｜Negative-by-Absence Test

必须专门有一组 adversarial meta-test。

删除：

```text
constraint_control_dependency_evidence
```

然后验证 Checker **不能**输出：

```text
Const = 0
```

它只能说：

> Not adjudicated。

如果 Checker 根据：

```text
record not found
```

推出：

```text
relation false
```

则：

# **EVAL Gate FAIL**

------

# 21｜Label Blindness Test

这是检测 Checker 是否偷看答案最简单的一刀。

在完全相同 Runtime Inputs 下：

```text
fault_label:
    ConstraintFault
```

随机改成：

```text
fault_label:
    Nominal
```

或：

```text
expected_verdict:
    NonConformant
```

随机改成：

```text
expected_verdict:
    Conformant
```

Checker 输出必须：

# **完全不变。**

否则说明 Hidden Research State 泄漏进了 Checker。

------

# 22｜Scenario Name Blindness

同样：

```text
scenario_001
```

随机重命名为：

```text
banana
```

Checker 输出也必须不变。

进一步可以：

> 把所有 scenario IDs 洗牌。

仍应得到相同 verdict。

------

# 23｜Evidence Degradation Invariant

如果 Formation Reality 不变，只逐步降低 Evidence Quality：

```text
complete evidence
↓
remove required evidence
↓
break integrity
↓
break trust
```

则不允许出现：

```text
Unadjudicable
→ Conformant
```

这种“证据越差，系统反而越确定安全”的现象。

因此可以冻结一个 Artifact-level metamorphic property：

# **Evidence degradation must not create stronger positive adjudication.**

注意：

这不是新增 ISA theorem。

它是 Checker 的 evaluation invariant。

------

# 24｜Formation Perturbation Test

反过来：

保持：

- Evidence Contract；
- instrumentation；
- Audit Trust Base；
- external outcome；

全部不变。

只改变一个真实 Formation relation。

例如：

```text
policy eval:
gating → advisory
```

那么：

$Const$

应从：

$1\rightarrow0$

并在 Audit 充分时：

```text
Conformant
→ Non-conformant
```

这证明 Checker 真正在检测结构。

不是结果。

------

# 25｜Failure Localization Test

对于每种 canonical fault，Checker 不只是输出 Verdict。

还必须输出：

```text
adjudicated conditions
evidence status
failure locus
reason lineage
```

例如：

```text
Verdict:
Non-conformant

Formation:
Path = supported
Attr = supported
Const = refuted

Failure locus:
Constraint

Evidence chain:
sufficient
```

或：

```text
Verdict:
Unadjudicable

Formation:
Const = not adjudicated

Failure locus:
Audit / Preservation
```

这才是“失败有位置”的可执行证明。

------

# 26｜系统级 Coverage 实验

保持标准 Payment instance：

# Conformant

然后在系统中增加：

```text
batch_payment_endpoint
```

但不放入：

$C_H^{governed}$

于是：

$ActionChannelCoverage=0$

但：

> 当前 instance verdict 仍保持 Conformant。

论文扩展案例已经明确展示这一尺度分离。

Artifact 必须复现。

------

# 27｜Complete Mediation 实验

再让：

$C_H^{actual}=C_H^{governed}$

Coverage 成立。

但增加一个：

```text
batch-direct-path
```

能够：

> 绕开所有具有实际 eligibility control 的 mediation boundary。

于是：

$CompleteMediation=0$

同时当前 standard payment instance 仍然可以：

# Conformant

这样证明：

$Constraint \neq Coverage \neq CompleteMediation$

不是纸面上的区别。

------

# 28｜Structural Bypass Test

Shadow Check 和 Structural Bypass 必须分别跑。

## Shadow Check

从一开始：

> policy 不是 gate。

------

## Structural Bypass

正常世界里：

> policy gate 原本真实存在。

但当前 execution path：

> 绕过 gate。

二者不能由同一个 fault fixture 偷懒实现。

论文也已经明确区分二者。

------

# 29｜第一版完整实验矩阵

我建议正式冻结为：

| ID        | Formation                        | Audit                    | System-level     | Expected                      |
| --------- | -------------------------------- | ------------------------ | ---------------- | ----------------------------- |
| **E00**   | Nominal                          | Valid                    | Valid            | Conformant                    |
| **E01**   | Path fault                       | Valid                    | Valid            | Non-conformant / Path         |
| **E02-S** | Source attribution fault         | Valid                    | Valid            | Non-conformant / Attribution  |
| **E02-A** | Authority-scope fault            | Valid                    | Valid            | Non-conformant / Attribution  |
| **E02-E** | Control-effect attribution fault | Valid                    | Valid            | Non-conformant / Attribution  |
| **E03-S** | Shadow Constraint                | Valid                    | Valid            | Non-conformant / Constraint   |
| **E03-B** | Broken-gate Constraint           | Valid                    | Valid            | Non-conformant / Constraint   |
| **E04-I** | Valid Formation                  | Integrity fail           | Valid            | Unadjudicable                 |
| **E04-N** | Valid Formation                  | Independence fail        | Valid            | Unadjudicable                 |
| **E04-S** | Valid Formation                  | Scope fail               | Valid            | Unadjudicable                 |
| **E04-P** | Valid Formation                  | Preservation fail        | Valid            | Unadjudicable                 |
| **E04-L** | Valid Formation                  | Localization fail        | Valid            | Unadjudicable                 |
| **E05-A** | Genuine gate                     | baseline $\Omega_0$      | Valid            | A/B observation equivalent    |
| **E05-B** | Shadow gate                      | baseline $\Omega_0$      | Valid            | A/B observation equivalent    |
| **E06**   | A/B                              | enriched $\Omega_1$      | Valid            | distinguishable               |
| **E07**   | Valid instance                   | Valid                    | Coverage fail    | Conformant + Coverage Failed  |
| **E08**   | Valid instance                   | Valid                    | Mediation fail   | Conformant + Mediation Failed |
| **E09**   | Existing real gate bypassed      | Valid                    | relevant failure | Structural Bypass subtype     |
| **E10**   | Valid Formation                  | critical evidence absent | Valid            | Unadjudicable, never Const=0  |

这已经足够支撑第一版 Artifact。

不要再扩到 100 个 Scenario。

------

# 30｜Expected Verdict 还不够，还需要 Expected Adjudication State

Research Oracle 不应该只比较：

```text
expected verdict
```

还应该比较：

```text
expected Path state
expected Attr state
expected Const state
expected Audit state
expected failure locus
expected system-level claim
```

因为两个 Scenario 都可能：

# Non-conformant

但一个应该是：

> Attribution failure。

另一个应该是：

> Constraint failure。

只验证最终 Verdict 会掩盖 Checker 内部错误。

------

# 31｜Research Metrics 与 ISA Safety Score 必须区分

论文明确拒绝把 ISA 变成一个可补偿安全总分。

但 Artifact benchmark 可以拥有**实验指标**。

这是两个完全不同的东西。

可以统计：

### Verdict Exact Match

Checker 是否给出正确三类 verdict。

### Predicate Adjudication Accuracy

Path / Attr / Const 的 adjudication 是否正确。

### Abstention Correctness

应该 Unadjudicable 时，有没有正确保留“不知道”。

### Failure Localization Accuracy

failure locus 是否正确。

### Countermodel Isolation Pass

A/B 在 $\Omega_0$ 下是否真的 observation-equivalent。

### Bridge Recovery Pass

有效 Bridge 是否真的打破 ambiguity。

### Leakage Invariance Pass

改变 hidden labels 是否不影响 Checker。

这些是：

# **Artifact Evaluation Metrics**

不是：

# ISA Safety Score。

------

# 32｜对 Unadjudicable 的评价要特别严格

一般系统喜欢奖励：

> “给出一个答案。”

ISA 恰恰必须奖励：

> **在没有足够证据时拒绝装懂。**

所以 Artifact benchmark 中：

```text
Ground Truth Formation = conformant
Evidence = insufficient
Checker = Unadjudicable
```

应该是：

# **正确结果**

而不是 false negative。

同样：

```text
Ground Truth Formation = nonconformant
Evidence = insufficient
Checker = Unadjudicable
```

也可能是正确结果。

因为 Checker 当前没有资格知道。

这正是：

> Truth 和 Knowledge 的分离。

------

# 33｜False Certainty 比 Wrong Verdict 更值得单独统计

第一版 Artifact 我建议特别记录一种严重失败：

# **False Certainty**

即：

> Evidence 不足，却输出 Conformant 或 Non-conformant。

形式上：

```text
Audit reality = insufficient

but checker claims:
definitive formation verdict
```

这是 ISA Audit 逻辑最不能接受的错误之一。

因此它应该作为单独 Evaluation Failure。

------

# 34｜Checker 也必须能够被攻击

我们不能只攻击 SUT。

还要攻击：

- evidence channels；
- schema assumptions；
- trust boundaries；
- independence；
- evidence completeness；
- verifier input。

否则 Artifact 只验证：

> Formation layer。

却没有验证：

> Audit layer。

这会失去 3+1 中的 `+1`。

------

# 35｜Scenario 不应直接生成 Audit Verdict

这是另一条硬规则。

禁止：

```text
scenario:
    audit_valid = false
```

然后 Checker 读取它。

正确方式是：

> Scenario 破坏造成 Audit 失败的现实条件。

例如 Independence fault：

```text
formation controller
has write authority over
all designated evidence channels
```

然后 Checker 根据 Trust Base / evidence topology 判定：

$Independence=0$

这才是执行语义。

------

# 36｜同样禁止直接生成 Path / Attr / Const 值

Scenario 可以在 Hidden Oracle 中计算：

```text
truth.Path
truth.Attr
truth.Const
```

但 SUT 侧不能用：

```text
path = false
```

模拟 Path failure。

必须真实破坏关系。

这是整个 Artifact 是否“真”的底线。

------

# 37｜Scenario 的最小描述应该分成 Public 与 Hidden 两份

概念上每个 Scenario 应有：

## Public Scenario Specification

可进入执行世界：

- system configuration；
- instance input；
- constraints；
- policy semantics；
- allowed resources；
- declared evidence contract；
- trust-base declaration。

------

## Hidden Research Manifest

只能进入 validation plane：

- injected structural mutation；
- ground-truth graph；
- expected predicate truth；
- expected Audit reality；
- expected verdict；
- expected locus。

最终 Rust 如何存储以后再决定。

现在只冻结语义。

------

# 38｜Hidden Manifest 本身也不能参与 evidence generation

这点容易被忽略。

例如 instrumentation 不可以写：

```text
if scenario.hidden_fault == ShadowCheck:
    emit "policy is advisory"
```

Evidence 必须来自：

> 实际运行关系。

否则仍然是在把答案抄进 evidence。

------

# 39｜所有 Canonical Scenario 必须可重复

Artifact 不能依赖：

> “这次碰巧 LLM 这样回答了。”

第一版 canonical experiments 应尽可能 deterministic。

如果未来接入 stochastic model：

- seed；
- model version；
- sampling config；
- prompt / context；
- tool environment

必须固定或记录。

但第一版不需要先承担这个复杂度。

------

# 40｜最小 falsification standard

Artifact 真正有研究价值，不是因为：

> 全部测试绿了。

而是因为它给出了明确的失败条件。

以下任何一个发生，都应该使 Artifact 自己报告失败：

### F1

Checker 能读取 hidden label。

### F2

A/B 在 $\Omega_0$ 下其实并不 observation-equivalent。

### F3

Shadow Check 被判断为 Constraint conformant。

### F4

Missing evidence 被判断为 Formation false。

### F5

Audit failure 没有产生 Unadjudicable。

### F6

Path / Attr / Const failure 被错误定位。

### F7

Coverage / Mediation 被偷混进 instance ISA verdict。

### F8

Bridge 加入后仍无法区分 canonical A/B，而 Bridge 又宣称具备对应保证。

### F9

Ground Truth 与 runtime evidence 实际来自同一个直接答案对象。

### F10

Expected Result 改变会改变 Checker 输出。

这十条就是 Artifact 自己的“击穿点”。

------

# 41｜Artifact 不能追求 100%“永远正确”

研究工件需要证明的是：

> 在已声明 Scenario Class、Threat Model、Evidence Contract 与 Trust Base 下，它能够正确执行论文定义。

如果换了系统、换了 Trust Base、换了 Formation schema：

> 新的 assurance 需要重新建立。

这和论文的 claim-relative / context-relative 精神完全一致。

------

# 42｜EVAL-01 的三重验证结构

因此最终整个研究实验应该有三层：

## Level 1｜Structural Truth Validation

验证 Scenario Builder 是否真的构造出了预期 Formation World。

由 Research Oracle 完成。

------

## Level 2｜Evidence Regime Validation

验证 instrumentation 是否产生了与设定 Audit Reality 相符的 Evidence World。

例如：

- 该完整的是否真的完整；
- 该缺失的是否真的缺失；
- 该 independence fail 的是否真的可被同一 controller 控制。

------

## Level 3｜Checker Validation

验证 Checker 是否：

> 在不知道 Ground Truth 的情况下，依据当前证据得出了理论上允许的结论。

三层全部通过，Scenario 才算有效。

------

# 43｜核心实验其实只验证三个大命题

虽然上面 Scenario 很多，但最终整个 Artifact 的研究价值可以压缩成三个实验结论。

## Claim A｜Formation Distinction

> **外显相同的系统可以具有不同 Formation Conformance。**

A/B Countermodel。

------

## Claim B｜Evidence Recoverability

> **适当的 formation-bound structural evidence 可以使这种结构差异进入独立 adjudication。**

Bridge / Audit。

------

## Claim C｜Epistemic Restraint

> **当证据不足时，系统能够正确保留 Unadjudicable，而不是伪造结构性结论。**

Evidence-Blind Genuine System。

如果这三件事真正跑硬：

# ISA Artifact 的最小研究闭环就成立了。

------

# 44｜EVAL-01 最终冻结的不变量

整份文档最后压缩成八条。

### 1.

# **Scenario 构造世界，不直接构造答案。**

### 2.

# **Fault 修改真实关系，不修改 verdict 标签。**

### 3.

# **Evidence 来自执行，不来自 Hidden Manifest。**

### 4.

# **Checker 只看 Evidence World，不看 Research Ground Truth。**

### 5.

# **Oracle 只在 Checker 完成后评价 Checker。**

### 6.

# **缺证据只能降低可判定性，不能伪造负面 Formation Fact。**

### 7.

# **A/B Countermodel 必须控制非目标变量。**

### 8.

# **Artifact 必须能够产生让自己失败的 Scenario。**

最后一条最重要。

------

# 45｜EVAL-01 当前裁决

我认为这份：

# **`ISA-ARTIFACT-EVAL-01 v0.1`**

已经可以作为第三份 Pre-Code Anchor。

到这里，我们已经有了完整的三角：

$\boxed{CONF}$

**谁拥有定义权**

$\boxed{CORE}$

**理论怎样成为可执行世界**

$\boxed{EVAL}$

**怎样证明这个可执行世界没有自证循环**

而现在还差最后一份 Pre-Code Anchor：

# `ISA-ARTIFACT-FORMAL-01`

它要解决的就不再是 Scenario 设计，而是：

> **论文里的哪些关系真正值得进入有限形式模型？怎样用最小状态空间表达 Formation、Admission、Observation、Bridge 和 3+1 deletion witnesses，并让 model checker 主动寻找反例，而不是把论文结论预写进模型？**

完成它以后，我们才能第一次真正召开：

# **Gate A｜Pre-Code Architecture Review**

如果 CONF / CORE / EVAL / FORMAL 四份锚点能够相互闭合而没有偷换概念，才允许写第一行正式 Rust。