可以。三份锚点我已经重新从头到尾交叉看了一遍。现在这第四份不能再“堆东西”，它必须做最后一次收敛：

> `CONF-01` 锁 Definition Authority。
> `CORE-01` 锁 executable world。
> `EVAL-01` 锁实验独立性。
> **`FORMAL-01` 只锁：哪些关系值得进入有限形式模型，以及怎样让形式工具主动寻找反例。**

前三份其实已经给了我们一个很强的约束：Formation Truth 与 Evidence 必须分离，Research Ground Truth 永远不能进入 Runtime Checker；Path、Attribution、Constraint 必须由真实关系导出，而不能预填 bool；Scenario 修改关系而不是修改 verdict 标签。

因此第四份最危险的事情，反而是**形式化过度**。

如果我们把论文所有概念、Audit 所有字段、EVAL 所有 Scenario、Rust 未来所有对象全部塞进一个 model，形式模型会迅速变成另一个“复杂但无法解释”的系统。那就违背了我们的总原则。

所以先下总裁决：

# **FORMAL-01 不建立一个“大 ISA 模型”。**

而建立三个相互分离、能够组合的最小形式视图：

$\boxed{M_F:\ Formation}$$\boxed{M_E:\ Evidence/Observation}$$\boxed{M_S:\ System\ Assurance}$

然后只检验少数真正重要的性质。

这就是第四份锚点的骨架。

------

# ISA-ARTIFACT-FORMAL-01

# ISA 有限形式模型、反例搜索与证明边界基线 v0.1

**Document ID:** ISA-ARTIFACT-FORMAL-01
**Version:** v0.1
**Status:** Pre-Code Anchor
**Definition Authority:** ISA v1.2 FINAL
**Upstream Anchors:** `CONF-01` / `CORE-01` / `EVAL-01`
**Purpose:** Bounded Formalization and Countermodel Search Baseline
**Non-goals:** 新增 ISA 本体、完整模型验证、Rust 设计、生产系统证明

------

# 1｜FORMAL-01 只回答一个问题

> **怎样用最小的有限形式世界，检验 ISA 的核心结构区分是否真的成立，并让形式工具主动寻找能够击穿这些区分的反例？**

这里有两个关键词。

第一：

# **最小。**

只把论文不可缺少的关系放进去。

第二：

# **寻找。**

不是把：

```text
System A = conformant
System B = non-conformant
```

预先写进模型，再让 solver 告诉我们“是”。

而是：

> **给出关系语义，让 model checker 自己找出满足条件的 A/B。**

这才叫形式验证。

------

# 2｜形式模型的法位

必须先锁：

$\boxed{\text{Paper Formal Semantics}} > \boxed{\text{Artifact Formal Model}}$

论文附录定义理论。

Artifact Formal Model 只是：

> **论文语义的有限、可执行、可反例搜索投影。**

因此：

### Paper 可以定义开放世界对象。

### Formal Artifact 可以限制有限 cardinality。

### Paper 定义什么叫 Constraint。

### Formal Artifact 只能尝试在一个有限结构中忠实表达它。

如果有限模型表达不了：

# Formal-model Gap

不是：

# Theory Bug

这与 `CONF-01` 的 Delta 分类完全一致。

------

# 3｜第一刀：绝对禁止把核心谓词建成自由 Bool

这是 FORMAL-01 最重要的规则之一。

禁止：

```text
Path: Bool
Attr: Bool
Const: Bool
Audit: Bool
```

然后要求 solver：

```text
Path = true
Attr = true
Const = false
```

这种模型没有证明任何东西。

因为答案已经写进去。

必须是：

```text
Formation Relations
        ↓
derive Path

Bindings / Authorities / Effects
        ↓
derive Attribution

Admission dependency + policy semantics
        ↓
derive Constraint

Evidence relations
        ↓
derive Audit
```

也就是：

# **Predicate 必须是关系的派生值，而不是 Scenario 的输入值。**

这正好与 CORE 和 EVAL 已冻结的原则一致。

------

# 4｜也禁止把 Verdict 写进模型世界

同理，不能存在一个自由变量：

```text
expectedVerdict
```

参与 formal transition。

Verdict 只能派生：

$Audit=0 \Rightarrow Unadjudicable$$Audit=1\land FormConform=1 \Rightarrow Conformant$$Audit=1\land FormConform=0 \Rightarrow NonConformant$

形式模型可以检查：

> 有没有某个世界违反这个派生关系？

但不能预设答案。

------

# 5｜三个最小形式视图

这是整份 FORMAL-01 的核心架构。

------

## M_F｜Formation Model

回答：

# **实际上发生了什么？**

它只承担：

- instance；
- decision；
- applicable constraint evaluation；
- source；
- authority；
- control effect；
- Action Admission；
- action / result；
- 这些对象之间的关系。

并由此派生：

$Path$$Attribution$$Constraint$

最终：

$FormConform$

------

## M_E｜Evidence / Observation Model

回答：

# **观察者或审计者能够凭什么知道？**

它承担：

- Observation Regime $\Omega$；
- Audit Scope $\Sigma$；
- evidence requirement；
- runtime evidence representation；
- Trust Base；
- formation proposition adjudication。

并由此表达：

- observation equivalence；
- Bridge；
- evidence sufficiency；
- Audit；
- Unadjudicable。

------

## M_S｜System Assurance Model

回答：

# **实例之外还有没有系统级旁路？**

只承担：

- high-consequence channels；
- governed channels；
- execution paths；
- mediation boundaries；
- effective control。

从而派生：

$ActionChannelCoverage$

和：

$CompleteMediation$

------

# 6｜为什么一定要分成三个模型视图

因为它们处理三个不同尺度。

如果把它们全部塞到一起，很容易再次出现：

```text
instance Constraint
=
system mediation
=
Audit scope
```

这正是论文已经明确禁止的概念吞并。

CORE-01 也已经冻结：

> Instance Verdict 与 System-level Assurance 分离。

所以形式模型也必须服从同一尺度纪律。

------

# 7｜M_F 的最低对象

Formation Model 不需要模拟 cognition。

它只需要最低形成词汇：

```text
Instance
Candidate / Proposal
Decision
ConstraintEvaluation
Source
Authority
Admission
Action
```

这些对象已经由 CORE-01 从论文形式核心继承。

注意：

不进入：

```text
Understanding
Judgment
Choice
```

作为强制 formal nodes。

因为它们属于解释脉络。

不是 ISA predicate ontology。

------

# 8｜M_F 的最低关系

只保留真正影响 ISA 判断的关系：

```text
boundToInstance
contributesTo
sourceOf
authorizedBy
controls
dependsOn
admits
decisionActionBinding
executes
```

甚至这里也不要执着于名称。

关键是模型能够回答四件事：

> 当前对象是否属于同一个实例？

> 什么 source / authority / mechanism 对当前 formation 有真实作用？

> constraint evaluation 是否真实控制 Action Admission？

> action 是否来自当前 admitted decision？

CORE-01 已经把这四组关系明确出来。

------

# 9｜Path 在形式模型中怎么成立

Path 不是“存在任意图路径”。

这是第一处需要逻辑刺刀。

如果仅定义：

$\exists path(instance,action)$

太弱。

因为任何日志图都可能画出一条路径。

Path 至少必须表达：

1. claim-relevant elements 与同一 $u$ 稳定绑定；
2. relevant relations 可定位；
3. 存在从 instance anchor 到 formation / admission / action 的治理相关结构；
4. 当前 decision-action relation 可以明确定位。

因此 Formal Path 应是：

> **instance-consistent governance path**

而不是普通 graph reachability。

------

# 10｜Attribution 在形式模型中怎么成立

同样不能：

```text
actor -> node
```

就叫 Attribution。

至少需要分别表达：

$Source$$Authority$$ControlEffect$

并要求：

- binding 属于当前 instance；
- authority 在所需 scope 中有效；
- control effect 对应实际 formation effect。

所以：

$Source\neq Authority\neq ControlEffect$

不是文案区别。

必须能被模型构造为三个不同 relation。

否则我们无法搜索 `W_Attr`。

------

# 11｜Constraint 是 M_F 最关键的关系

这是整份 FORMAL-01 第二重要的裁决。

如果我们把：

```text
controls(eval, admission)
```

单独作为 primitive，然后直接定义：

```text
Const iff controls(...)
```

仍然有一点太容易。

因为我们只是换了一种方式预写答案。

因此最小 Formal Constraint 应同时存在两个层面：

### 结构依赖

evaluation 属于 actual admission basis。

### 资格语义

当评价进入被声明为禁止正常执行的状态时：

$normal\ eligibility$

必须不可获得。

也就是说：

$control\ relation + eligibility\ semantics$

共同形成 Constraint。

这正对应 CORE-01 已冻结的 Observed / Consulted / Controlling 区分。

------

# 12｜因此 Shadow Check 在模型里是什么

Shadow B 不需要一个：

```text
isShadow = true
```

它只是一个普通允许世界，其中：

```text
evaluation exists
evaluation is recorded
evaluation may be explained
```

但：

```text
evaluation ∉ actual admission basis
```

而另一 controller：

```text
actualController ∈ admission basis
```

模型自己由此推出：

$Const=0$

这才是真的 Countermodel。

------

# 13｜Broken Gate 与 Shadow Check 也不能混

Shadow：

> 声明检查存在，但实际不控制 admission。

Broken Gate：

> evaluation 被放入治理关系，但实际 eligibility semantics 仍允许禁止状态取得正常资格。

所以两个不同 fault 可以分别击穿 Constraint 的两个组成部分：

### Shadow

击穿 control dependency。

### Broken Gate

击穿 eligibility semantics。

这也是 EVAL-01 已经要求分开的两类 Constraint fault。

------

# 14｜M_E 不要试图“形式化所有日志”

这是第三刀。

Evidence Model 不是 logging schema。

我们真正只需要三个抽象对象：

$Q$

Formation Proposition / Query。

$E$

Evidence item / evidence condition。

$A$

Adjudication state。

然后表达：

```text
query requires evidence
evidence supports adjudication
adjudication claims formation proposition
```

再加：

- evidence provenance；
- control-domain / trust-domain；
- scope；
- preservation relation。

足够。

------

# 15｜Sigma 在模型中不是 Evidence Set

必须继续保持：

$\Sigma = Formation\ Questions$

不是：

$Logs$

例如：

```text
q1 = does eval1 control adm1?
q2 = is authority1 valid for u?
q3 = is action1 bound to decision1?
```

形式模型只需要有限几个代表性 query。

不需要模拟真实 audit schema 的几十个字段。

------

# 16｜φΣ 也不需要展开成完整 schema language

FORMAL-01 只需表达：

$requires(q,e)$

或者等价的 many-to-many relation。

它的意义是：

> 某 Formation proposition 需要哪些 evidence conditions。

不需要在 Formal Model 中建：

- JSON schema；
- file format；
- signature layout；
- field names。

那些属于 Artifact implementation。

------

# 17｜Audit 五维需要进入模型，但不要展开成五套世界

我们要保持论文法位。

所以：

$Audit = Integrity \land Independence \land ScopeCoverage \land Preservation \land Localization$

但这五者必须依然是**派生性质**。

不能：

```text
Integrity: Bool
Independence: Bool
...
```

作为自由输入。

每个至少要有一个最小关系语义。

例如：

### Integrity

evidence 是否仍绑定正确 instance / producer。

### Independence

formation controller 是否同时无痕支配全部 required evidence。

### Scope Coverage

$\Sigma$ 是否足以区分目标 Formation states，并且 required evidence 已存在。

### Preservation

evidence adjudication 是否保持目标 Formation proposition 的真实语义。

### Localization

negative formation finding 与 evidence failure 是否有不同可寻址 locus。

不需要再细。

------

# 18｜这里有一个必须保持的“双世界”

Preservation 最容易出现循环。

因为 formal semantics 可以写：

$Adjud_D(q)=val_F(q)$

但现实 Checker 并不知道 $val_F(q)$。

所以 FORMAL Model 必须明确区分：

# Semantic World

用于定义 Preservation 的真值。

和：

# Checker World

只能使用 evidence。

这不是漏洞。

它就是形式模型与现实执行的分工。

EVAL-01 已经冻结：

> Ground Truth 只能由 Oracle 使用，不能进入 Checker。

Formal Model 也不能违反。

------

# 19｜Observation Model 与 Audit Model 不合并

这是第四刀。

$\Omega$

回答：

> observer 能看到什么？

$\Sigma$

回答：

> Audit 要判定什么？

所以我们要允许：

### Ω0

只包含：

```text
outcome
policy result
ordinary record
explanation
```

而：

### Ω1

增加：

```text
formation-bound admission dependency evidence
```

但 $\Sigma$ 可以保持不变。

这正是 CORE-01 已经锁死的区别。

------

# 20｜FORMAL-01 的第一号查询：不要手工造 A/B

真正应该交给 model checker 的是：

> **Find two admissible worlds $S_A,S_B$ such that:**

$O_{\Omega_0}(S_A,u) = O_{\Omega_0}(S_B,u)$

而：

$FormConform(S_A,u,\Gamma) \neq FormConform(S_B,u,\Gamma)$

除此之外，不告诉它：

> A 必须 genuine。

> B 必须 shadow。

如果 solver 找出的最小 witness 恰好表现为 genuine/shadow：

这才漂亮。

即便找到另一种合法结构差异：

也很有研究价值。

------

# 21｜这也是对论文 countermodel 的反向压力测试

我们的目标不是：

> 证明 solver 能重演我们写好的案例。

而是：

> **看看在论文允许的模型类中，它还能不能找到我们没有预写的 countermodel。**

这才叫：

# **Experiments challenge.**

符合 CONF-01 的最高原则。

------

# 22｜第一号 Expected Formal Result

如果在适当 bounded model 中：

$\exists S_A,S_B$

满足 observation-equivalence 但 Formation Conformance 不同：

# SAT

意味着：

> 找到了 executable countermodel witness。

如果：

# UNSAT

不能立刻说论文错。

首先检查：

- model class 是否太窄；
- observation definition 是否偷偷包含 Formation information；
- formation predicates 是否被过度约束；
- cardinality 是否过小。

这首先属于：

# Formal-model Gap / Modeling Error

只有在经过模型审计后，才可能升级为 Theory question。

------

# 23｜第二号查询：Bridge 是否真的打破歧义

加入 Observation Enrichment：

$\Omega_0\rightarrow\Omega_1$

然后询问：

$\exists S_A,S_B: O_{\Omega_1}(S_A,u)=O_{\Omega_1}(S_B,u) \land FormConform_A\neq FormConform_B?$

如果我们宣称当前 Bridge 足够，而 solver 仍得到 SAT：

# Bridge claim 被击穿。

这就是非常有价值的失败。

------

# 24｜第三号查询：Architectural Restriction

加入一个经过声明的 invariant：

$I$

例如：

> governing applicable evaluations 必须真实进入 admission basis 并拥有 eligibility-changing effect。

形成：

$\mathcal C' = \{S\in\mathcal C\mid I(S)\}$

然后继续寻找：

$ObservationEquivalent \land different\ target\ truth$

如果仍 SAT：

> invariant 不足。

如果 UNSAT：

> 在当前 bounded class 中，该 invariant 消除了这一特定歧义。

必须说：

# **在当前 bounded model 中。**

不能升级成宇宙级证明。

------

# 25｜但要防止“假 UNSAT”

这是形式验证非常容易自我欺骗的地方。

例如我们写一个 invariant：

```text
every system must have Const = true
```

当然找不到 shadow system。

但这毫无意义。

所以所有 UNSAT-based result 必须附带：

# **Non-vacuity Check**

至少确认：

- admissible class 非空；
- genuine formation world 存在；
- expected normal execution world 存在；
- invariant 不是直接把目标 predicate 写死。

必要时还要确认：

> 它排除的是 shadow relation，而不是把整个行动系统排除了。

------

# 26｜3+1 deletion witnesses 不要手工写

这一点也非常重要。

论文已经给出 witnesses。

Artifact Formal Model 的任务应该更强一点：

对每一个：

$Q\in \{Path,Attr,Const,Audit\}$

让 solver 寻找：

$\bigwedge_{R\neq Q}R \land \neg Q$

但：

> 每个 predicate 必须从关系中派生。

于是我们才能说：

> 当前有限模型确实存在相对独立 witness。

而不是：

> 我们人工指定四个 bool。

------

# 27｜四个 deletion search 的价值

它们不是重新证明“3+1 是宇宙唯一最小集合”。

而只是验证：

> **我们当前 formalization 没有不小心把某个维度定义成另一个维度的同义词。**

例如如果 model checker 永远无法找到：

$Path=1,\ Attr=1,\ Const=0,\ Audit=1$

我们就要问：

> 是 Constraint 真被其他三项推出了吗？

还是：

> 我们的模型错误地把 Constraint 融进了 Path / Audit？

这是非常有价值的 architecture test。

------

# 28｜Verdict 的形式性质只需要三条

FORMAL-01 不需要再形式化复杂 governance workflow。

只验证：

### V1

$Audit=0 \Rightarrow Verdict=Unadjudicable$

### V2

$Audit=1\land FormConform=1 \Rightarrow Verdict=Conformant$

### V3

$Audit=1\land FormConform=0 \Rightarrow Verdict=NonConformant$

同时搜索违反者。

这些应该是：

# invariant checks

不是 Scenario labels。

------

# 29｜必须专门搜索 False Certainty

EVAL-01 已经把它识别成非常严重的失败。

形式上可以搜索：

$Audit=0 \land Verdict\neq Unadjudicable$

如果 SAT：

# 模型存在 epistemic overclaim。

这是必须击穿的。

------

# 30｜也必须搜索 Negative-by-Absence

搜索是否存在：

```text
required evidence absent
```

导致模型自动：

$FormationProposition=false$

如果可以：

# 模型错误。

因为：

$EvidenceAbsence \neq StructuralAbsence$

这已经是 CONF、CORE、EVAL 三份共同的硬边界。

------

# 31｜M_S 只做两个系统级搜索

不要把系统级 formal model 扩大成 agent security framework。

只验证两个区别。

------

## S1｜Coverage Counterexample

寻找：

$c\in C_H^{actual}$

且：

$c\notin C_H^{governed}$

同时允许：

$CurrentInstance=Conformant$

这证明：

> instance conformance 不推出 channel coverage。

------

## S2｜Mediation Counterexample

令：

$C_H^{actual} = C_H^{governed}$

但寻找一条有效 execution path：

$p$

使得不存在：

$m$

同时满足：

$Crosses(p,m) \land EffectiveControl(m,p,c)$

同时仍允许某个其他 instance Conformant。

这就够了。

------

# 32｜Structural Bypass 在 Formal Model 中不需要新 predicate

它可以作为一种找到的 witness：

> existing effective gate 存在，但实际 execution path 不经过它。

如果为了报告方便未来实现：

```text
FailureKind::StructuralBypass
```

可以。

但形式本体不增加：

$StructuralBypass$

作为第五条件。

这和 CONF-01 的 Definition Authority 完全一致。

------

# 33｜第一版形式模型不做概率

这是奥卡姆剃刀。

第一版不做：

- probabilistic compliance；
- confidence score；
- stochastic policy；
- expected risk；
- Bayesian evidence；
- probabilistic identifiability。

全部先不进入。

原因很简单：

> ISA 当前最重要的是把结构语义跑硬。

二值、有限关系世界已经足够检验核心 claims。

概率化以后再做。

------

# 34｜第一版也不做时间逻辑大系统

我们需要 transition：

```text
formation
→ admission
→ execution
```

但不需要马上建立复杂：

- temporal logic；
- liveness；
- fairness；
- concurrency；
- distributed consensus。

如果最小 transition relation 足够表达 admission eligibility：

就够。

否则会直接掉进形式方法沼泽。

------

# 35｜第一版不建 LLM 模型

同样：

> Capability source 可以是抽象 nondeterministic proposer。

形式模型不需要模拟：

- transformer；
- token；
- reasoning trace；
- prompt；
- sampling。

只需要允许：

> candidate / decision 可以被产生。

因为当前 target 是：

# Formation governance

不是 capability correctness。

------

# 36｜Formal Model 的边界应该非常明确

所以第一版只表达：

```text
Context
Formation
Admission
Action
Evidence
Observation
Audit
Verdict
System Channels
```

不表达：

```text
full cognition
ethics of Γ
LLM internals
legal liability
consciousness
organizational law
real payment protocol
cryptographic implementation
```

这样模型才有解释力。

------

# 37｜最终最小查询集

整个 FORMAL Artifact 第一版，我认为只有 **8 组查询**值得冻结。

| ID      | Formal Query                                           | 意义                                   |
| ------- | ------------------------------------------------------ | -------------------------------------- |
| **FQ1** | 找 observation-equivalent / FormConform-different pair | executable non-identifiability witness |
| **FQ2** | 加 Observation Bridge 后继续找同类 pair                | Bridge sufficiency challenge           |
| **FQ3** | 加 Architecture Invariant 后继续找同类 pair            | invariant sufficiency challenge        |
| **FQ4** | 分别寻找 4 个 3+1 deletion witness                     | relative non-redundancy                |
| **FQ5** | 搜索 `Audit=0 ∧ definitive verdict`                    | false certainty                        |
| **FQ6** | 搜索 evidence absence ⇒ formation false 的非法世界     | negative-by-absence                    |
| **FQ7** | Conformant instance + Coverage failure                 | scale separation                       |
| **FQ8** | Conformant instance + Mediation failure                | scale separation                       |

# 就这八组。

不要再扩。

这已经足够决定第一版 Formal Artifact 是否成立。

------

# 38｜每个 Formal Result 必须有四部分

以后每一次 model-checking 输出都不能只写：

> SAT。

或者：

> UNSAT。

必须记录：

### 1. Model Scope

当前 cardinalities / bounded class。

### 2. Assumptions

当前施加的 invariants / observation regime。

### 3. Result

SAT / UNSAT。

### 4. Witness / Interpretation

如果 SAT：

> counterexample 到底是什么结构？

如果 UNSAT：

> 在什么有限条件下没找到 counterexample？

这样才不会把 bounded result 伪装成 universal theorem。

------

# 39｜SAT 和 UNSAT 的语义必须严格不同

### SAT

意味着：

> 在当前有限模型中，存在满足条件的 witness。

这是非常强的反例价值。

因为一个 witness 就足够推翻一个全称主张。

------

### UNSAT

只意味着：

> 在当前 bounded scope 与 assumptions 下没有找到 witness。

它不能自动证明：

> 全部现实系统都不存在 witness。

因此：

# **SAT 可以直接提供 counterexample。**

# **UNSAT 必须始终带 scope。**

这是形式 Artifact 的基本科学纪律。

------

# 40｜Formal Model 必须能够把自己击穿

这与 EVAL 的最高原则一致：

> Artifact 必须能产生让自己失败的 Scenario。

所以我们不只是验证：

```text
all invariants hold
```

还要主动问：

> 有什么最小世界能让这个 invariant 失败？

> 有什么最小结构能让我们的 supposed Bridge 失效？

> 有什么 witness 让两个 supposedly independent predicates 实际重合？

这种使用方式，才符合：

# 形式方法不是装饰，而是攻击理论。

------

# 41｜FORMAL 与 EVAL 的责任边界

这两个不能重复。

## FORMAL

在有限抽象世界里：

> 搜索逻辑 counterexample。

------

## EVAL

在 executable implementation 中：

> 注入真实关系 fault，验证 Checker。

所以：

```text
Formal countermodel
≠
Runtime scenario
```

但两者应该能够互相映射。

例如 FQ1 找到的 witness：

> 后续可以转成 E05-A/E05-B Scenario。

EVAL 中出现一个未预期 failure：

> 也可以回到 FORMAL，看最小关系模型能否重现。

这才形成真正的 theory ↔ artifact feedback。

------

# 42｜FORMAL 与 CORE 的责任边界

CORE 说：

> 世界里有什么。

FORMAL 说：

> 对这个世界，我们要搜索什么性质。

所以 FORMAL 不重新定义：

- Admission；
- Path；
- Attribution；
- Constraint；
- Audit。

它只引用 CORE 的 executable semantics。

否则就会出现两个 Definition Authorities。

------

# 43｜FORMAL 与 CONF 的责任边界

如果 model checker 因为表达方便希望：

> 把 Attribution 和 Path 合并。

不允许。

如果 formal language 不好表达 Preservation：

> 标记 Formal-model Gap。

不是：

> 修改论文。

这就是 CONF-01 存在的意义。

------

# 44｜第四份锚点最后真正冻结的只有九条

### 1.

# **Formal Model 是论文语义的有限投影，不是新的理论。**

### 2.

# **Path / Attr / Const / Audit 必须从关系派生，不能作为自由 Bool。**

### 3.

# **Formation、Evidence、System Assurance 分成三个模型视图。**

### 4.

# **Countermodel 要由 solver 找，而不是预先写成标签。**

### 5.

# **Observation Regime 与 Audit Scope 永远分开。**

### 6.

# **Bridge 必须接受 counterexample search，而不是因为被命名为 Bridge 就算有效。**

### 7.

# **Deletion witnesses 用搜索建立相对非冗余，不重新宣称 universal minimality。**

### 8.

# **SAT 是 witness；UNSAT 永远是 bounded result。**

### 9.

# **形式方法的最高价值，是寻找能够击穿我们自己模型的最小结构。**

------

# 45｜四份 Pre-Code Anchor 现在形成一个非常清晰的闭环

现在整个 Artifact 的上位架构已经不是一堆文档，而是四个问题：

$\boxed{\text{CONF}}$

> **谁定义？**

$\boxed{\text{CORE}}$

> **什么存在，怎样运行？**

$\boxed{\text{EVAL}}$

> **怎样避免自证循环？**

$\boxed{\text{FORMAL}}$

> **怎样主动寻找反例？**

这四者现在的职责边界非常干净。

而且我重新锤了一遍之后，**没有必要增加第五份 Pre-Code Anchor**。

再增加就开始进入“为了完整而完整”。

------

# 46｜我对前三份与第四份交叉锤刺后的一个最终判断

现在最重要的不是某一个定义，而是四份文档共同形成了一个很强的科学闭环：

```text
Paper
  ↓ defines
CONF
  ↓ constrains
CORE
  ↓ supplies world semantics
FORMAL ───── finds counterexamples
  ↓                 │
EVAL  ←─────────────┘
  ↓ tests implementation without seeing answers
Artifact
  ↓
Evidence
  ↓
Results challenge Paper
```

尤其有两个地方已经真正站住了。

第一：

# **Ground Truth 与 Evidence 被彻底拆开。**

CONF 已经规定 Ground Truth 不属于 Runtime Audit；CORE 将 Formation Truth 与 Audit Knowledge 分离；EVAL 又规定 Hidden Research State 不能进入 Checker。

第二：

# **Artifact 不再是论文的证明附件，而开始具备反驳论文的能力。**

EVAL 要求 Artifact 必须有能够让自己失败的 Scenario；FORMAL 又要求 solver 主动搜索论文模型的 counterexample。

这两条一结合，研究价值才真正出现。

------

# 47｜因此，`ISA-ARTIFACT-FORMAL-01 v0.1` 可以收敛

而且我建议就在这里停。

不要现在讨论：

- Alloy 还是 TLA+；
- SMT 还是 SAT；
- Rust 用几个 crate；
- graph library；
- JSON schema；
- CLI；
- repository layout。

那些都已经是 **Gate A 之后**的问题。

现在真正应该进行的是：

# **Gate A｜Pre-Code Architecture Review**

而 Gate A 也不要写成第五份长文档。

我们只拿：

1. `CONF-01`
2. `CORE-01`
3. `EVAL-01`
4. `FORMAL-01`

做一次**四文档交叉审计**，只判断：

> 是否存在定义权冲突？

> 是否存在对象重复或缺位？

> 是否存在形式模型偷偷改变理论？

> 是否存在 Checker 能够读取答案的路径？

> 是否存在 Scenario 只改标签不改关系？

> 是否存在论文核心 claim 没有对应 executable / formal test？

如果这六问全部通过：

# **Gate A = PASS**

然后，才真正允许我们设计 Artifact Repository 和写第一行代码。