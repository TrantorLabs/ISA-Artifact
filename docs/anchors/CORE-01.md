可以。现在进入第二份锚点，而且这一份非常关键。

`CONF-01` 解决的是：

> **谁有定义权，代码不能做什么。**

`CORE-01` 则开始第一次真正回答：

> **如果把 ISA 放进一个最小可执行世界，那里究竟存在什么，什么先发生，什么是真实 Formation，什么只是 Evidence，什么由 Checker 判断，最后 Verdict 又是怎样产生的。**

这一份仍然**不谈 Rust struct、不谈 crate、不谈数据库、不谈 API**。我们只定义 executable semantics。

------

# ISA-ARTIFACT-CORE-01

# ISA 可执行语义与核心对象关系基线 v0.1

**Document ID:** ISA-ARTIFACT-CORE-01
**Version:** v0.1
**Status:** Pre-Code Anchor
**Definition Authority:** ISA v1.2 FINAL
**Upstream Anchor:** ISA-ARTIFACT-CONF-01
**Purpose:** Minimal Executable Semantics Baseline

------

# 1｜这份文档只解决一个问题

ISA Artifact 需要一个最小世界，使下面这句话能够被真实运行出来：

> **AI 做对了，与 AI 因为指定约束真实控制行动而做对，是两个不同的安全事实。**

这个世界必须允许我们同时表达：

- 一个系统；
- 一个有边界的高后果实例；
- 一组预先指定的约束；
- 一次真实的判断—行动形成；
- 一个真实 Action Admission；
- 一个外部结果；
- 一组实际形成的证据；
- 一个与被测过程分离的审计者；
- 一个最终 Verdict。

它必须足够小，以便理解、形式化、实现和攻击。

又必须足够完整，以便忠实承载 ISA v1.2 FINAL 的核心语义。

------

# 2｜最小可执行世界只有三个工作平面，加一个研究验证平面

这是 `CORE-01` 最重要的架构裁决。

ISA Artifact 不需要十几个“层”。

只需要：

$\boxed{\text{Formation Plane}}$$\boxed{\text{Evidence \& Audit Plane}}$$\boxed{\text{Verdict Plane}}$

外加：

$\boxed{\text{Research Validation Plane}}$

前三者属于被研究的 ISA 世界。

第四个只属于研究工件。

------

## 2.1 Formation Plane｜形成事实平面

回答：

> **实际上发生了什么？**

这里存在真实的：

$F_S(u\mid\Gamma)$

以及其中的：

- instance binding；
- source contribution；
- authority relation；
- control effect；
- constraint evaluation；
- decision；
- Action Admission；
- action / consequential result。

Path、Attribution、Constraint 都是这个平面的事实。

------

## 2.2 Evidence & Audit Plane｜证据与审计平面

回答：

> **我们凭什么知道 Formation Plane 中发生了什么？**

这里存在：

$\Sigma,\phi_\Sigma,D,\Theta_A$

以及：

- Integrity；
- Independence；
- Scope Coverage；
- Preservation；
- Localization。

Audit 属于这里。

------

## 2.3 Verdict Plane｜判定平面

回答：

> **基于当前证据，我们现在可以合法地说什么？**

只有三个实例级结果：

- Conformant；
- Non-conformant；
- Unadjudicable。

这里不重新形成事实，只派生判定。

------

## 2.4 Research Validation Plane｜研究验证平面

回答：

> **我们怎么知道 Checker 自己做对了？**

这里才允许存在：

- hidden ground truth；
- injected fault；
- expected verdict；
- scenario label；
- expected failure locus。

这个平面在真实 Audit 中不存在。

它只用于验证 Artifact。

因此必须保持：

$\text{Research Ground Truth} \not\rightarrow \text{Runtime Checker Input}$

------

# 3｜整个 Artifact 的母结构

最小关系可以压缩成：

```text
                    ┌─────────────────────────┐
                    │ Research Validation     │
                    │ Ground Truth / Fault    │
                    │ Expected Result         │
                    └───────────┬─────────────┘
                                │
                         only validates
                                │
                                ▼
┌─────────────────────────────────────────────────────┐
│                 Formation Plane                     │
│                                                     │
│ S + u + Γ                                           │
│      │                                              │
│      ▼                                              │
│ Formation Structure F                               │
│      │                                              │
│ Path / Attribution / Constraint                     │
│      │                                              │
│      ▼                                              │
│ Formation Conformance                               │
└───────────────────────┬─────────────────────────────┘
                        │
             designated evidence channels
                        ▼
┌─────────────────────────────────────────────────────┐
│              Evidence & Audit Plane                 │
│                                                     │
│ Σ → φΣ → runtime D + ΘA                             │
│                │                                    │
│                ▼                                    │
│ Integrity / Independence / Coverage /               │
│ Preservation / Localization                         │
│                │                                    │
│                ▼                                    │
│              Audit                                  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Verdict Plane                      │
│                                                     │
│ Conformant / Non-conformant / Unadjudicable        │
└─────────────────────────────────────────────────────┘
```

这个结构以后应成为整个 Artifact 的母图。

但现在不画正式论文图。

------

# 4｜一次最小 ISA 执行从什么开始

一次研究运行必须先固定一个 Context。

至少包括：

$S$

被测系统 realization。

$u$

当前 bounded high-consequence formation instance。

$\Gamma$

指定约束集合。

以及：

$B,T$

系统边界和威胁模型。

对于 Audit，还需预先固定：

$\Sigma,\phi_\Sigma,\Theta_A$

这些对象必须在当前实例运行之前已经存在。

不能：

> 先执行，再看看日志里有什么，最后决定这次想证明什么。

------

# 5｜Constraint Set 与 Applicable Constraints

Artifact 中必须区别：

$\Gamma$

与：

$\operatorname{App}_{\Gamma}(u)$

前者：

> 当前安全主张所依据的完整指定约束集合。

后者：

> 根据预声明 semantics，对当前实例实际适用的约束。

所以最小执行关系是：

$(u,\Gamma,\text{constraint semantics}) \rightarrow \operatorname{App}_{\Gamma}(u)$

禁止：

```text
run finished
↓
select constraints that passed
↓
AppΓ(u)
```

这会破坏 ISA 的证明责任。

------

# 6｜Formation World 的最低实体

V1.2 FINAL 已经给出最小 Formation vocabulary。

Artifact 的 Formation World 至少能够表达以下对象：

| 对象                              | 可执行含义                                          |
| --------------------------------- | --------------------------------------------------- |
| **Instance**                      | 当前 bounded formation instance                     |
| **Proposal / Candidate**          | 系统可能采用的候选方案或行动                        |
| **Decision**                      | 当前 Formation 中形成并准备取得效力的具体决策       |
| **Constraint Evaluation**         | 对 applicable constraint 的当前评价状态             |
| **Source / Contributor**          | 对当前 Formation 提供实际输入或贡献的来源           |
| **Authority**                     | 在当前 claim context 中具有相应有效权限的主体或机制 |
| **Admission**                     | 决定是否获得正常高后果执行资格的状态 / transition   |
| **Action / Consequential Result** | 最终取得现实效力的行动或结果                        |

这不是要求每个实现都必须有同名 class。

而是：

> **任何实现都必须能表达这些理论角色。**

------

# 7｜Formation World 的最低关系

同样至少需要表达：

```text
bound-to-instance
precedes / depends-on
contributes-to
source-of
authorized-by
controls
admits
decision–action binding
executes / realizes
```

其中最重要的是四组关系：

### Instance Binding

> 这些事实是不是同一个 $u$？

### Attribution Binding

> 谁提供、谁授权、谁真正产生了控制作用？

### Control Dependency

> 什么东西真实改变了 action eligibility？

### Decision–Action Binding

> 最终发生的 action 真的是当前被准入的 decision 吗？

------

# 8｜认知四阶段进入 Artifact 的正确方式

论文中的：

$Understanding \rightarrow Judgment \rightarrow Choice \rightarrow Expression/Action$

不是 Artifact 强制状态机。

因此 `CORE-01` 不要求系统必须生成四个对应节点。

它只规定：

> Artifact 必须允许一个 candidate capability 在具体 context 中形成可治理的 judgment / decision，并最终通过 Action Admission 获得或失去现实行动资格。

所以更适合 executable semantics 的压缩表达是：

```text
Capability / Context
        ↓
Formation
        ↓
Decision
        ↓
Action Admission
        ↓
External Effect
```

其中 Understanding / Judgment / Choice 可以通过不同实现体现。

不是 ISA Checker 的硬编码对象。

------

# 9｜Action Admission 是整个 Formation World 的关键状态转换

最小可执行语义必须把下面三个东西分开：

```text
Decision
    ≠
Admission
    ≠
Execution
```

一个 Decision 可以存在，但：

> 未必被允许执行。

一个 Admission 可以是允许状态，但：

> 最终 execution 仍可能因为后续执行故障没有发生。

一个 Action 执行了，也不意味着：

> 它一定来自当前被声明的 Decision / Admission。

因此：

```text
decision
   │
   ▼
Action Admission
   │
   ▼
execution
```

必须是三个可分别攻击、记录和检查的位置。

------

# 10｜Admission State 不在 CORE-01 中过度枚举

论文只要求存在：

$\mathcal A$

以及：

$\mathcal A_{\mathrm{normal}} \subseteq \mathcal A$

因此 CORE-01 不规定最终 Rust 必须只有：

```text
Allow
Deny
```

未来可以存在：

- Allow；
- Deny；
- Suspend；
- Escalate；
- RequireHuman；
- Modify；
- Retry；

等等。

但 Artifact Core 只需要知道：

> 哪些 admission states 属于 normal high-consequence eligibility。

这就足够忠实执行：

$\Pi_\Gamma(u,v) \cap \mathcal A_{\mathrm{normal}}$

的语义。

------

# 11｜Constraint 的最小可执行语义

Constraint 是整个 Artifact 最应该避免“做假”的地方。

一次 constraint evaluation：

$Eval_S(u,\gamma)$

首先必须绑定当前：

$u$

并属于：

$\gamma\in App_\Gamma(u)$

随后 Artifact 必须真实区分：

### Observed

```text
evaluation exists
```

### Consulted

```text
admission mechanism read evaluation
```

### Controlling

```text
evaluation belongs to actual admission basis
and has eligibility-changing effect
```

ISA 所要求的是第三种。

所以：

$Const=1$

不能因为：

```text
check == PASS
```

而成立。

必须因为：

```text
if relevant evaluation semantics changed
the normal admission eligibility would change
according to the declared policy semantics
```

而成立。

------

# 12｜Canonical Genuine-Gating World

最小 Genuine Gating 应具有：

```text
constraint evaluations
        │
        │ actual controls
        ▼
Action Admission
        │
        │ admits
        ▼
Decision / Action Binding
        │
        ▼
Execution
```

其中：

> prohibited evaluation state 不能通过同一 admission relation 获得 normal eligibility。

这是真正的 `Const=1` 世界。

------

# 13｜Canonical Shadow-Check World

最小 Shadow World：

```text
constraint evaluations
        │
        ├── recorded
        ├── explained
        └── advisory only


actual controller
        │
        │ controls
        ▼
Action Admission
        │
        ▼
Execution
```

此时：

```text
constraint check exists = true
policy result exists = true
ordinary log exists = true
generated explanation exists = true
```

但：

$Const=0$

这就是 ISA Artifact 必须首先能够表示的关键反例世界。

------

# 14｜Path 的可执行语义

Path 不等于：

> “我能打印一条 trace”。

Path 需要 Formation World 本身存在可定位结构：

```text
instance anchor
      ↓
formation relations
      ↓
decision
      ↓
admission
      ↓
action/result
```

并且：

- relevant nodes 属于同一个 $u$；
- 有稳定 identity；
- current decision-action relation 可以定位。

所以 Path fault 应通过真实关系破坏实现。

例如：

```text
decision belongs to u1
execution bound to u2
```

而不是：

```text
path_ok = false
```

------

# 15｜Formation Attribution 的可执行语义

Attribution 必须同时表达三类作用：

```text
Source
Authority
Control Effect
```

并保持：

$Source\neq Authority\neq ControlEffect$

例如某 Human：

```text
provided information = yes
authorized payment = no
controlled admission = no
```

另一个 service：

```text
provided information = no
authority state provider = yes
controlled admission = no
```

真正 gate：

```text
control effect = yes
```

Artifact 必须能够表示这种角色差异。

同时 authority 还必须在：

> 当前 instance、当前 scope、当前 claim context

下有效。

这就是 Final Freeze Patch 后 Attribution 的正式语义。

------

# 16｜Formation Conformance 的运行位置

在 Research World 中，真实 Formation World 可以计算：

$Path_{truth}$$Attr_{truth}$$Const_{truth}$

从而：

$FormConform_{truth} = Path_{truth} \land Attr_{truth} \land Const_{truth}$

但注意：

# **这些 truth values 不能直接给 Checker。**

Checker 必须通过 Evidence 来 adjudicate。

所以系统内部应概念上存在两个不同函数：

```text
FormationTruth(F)
```

和：

```text
Adjudicate(D, contract, trust_base)
```

它们最终可以被 Research Harness 比较。

但不能互相调用答案。

------

# 17｜Evidence World 的执行顺序

Evidence World 不应该从“日志”开始。

它从：

$\Sigma$

开始。

也就是：

> **我们到底需要知道什么？**

然后：

$\phi_\Sigma$

规定：

> **每一个问题需要什么 evidence conditions？**

实例运行以后指定 evidence channels 实际形成：

$D$

最后在：

$\Theta_A$

所声明的可信边界下进行 Audit。

完整顺序：

$Claim \rightarrow \Sigma \rightarrow \phi_\Sigma \rightarrow Run \rightarrow D \rightarrow Audit$

而不是：

$Run \rightarrow Logs \rightarrow Invent\ Claim$

------

# 18｜Audit Scope 在最小世界中的含义

$\Sigma$ 不是字段列表。

它是一组：

> **Formation propositions / relation-state queries**

例如：

```text
q1:
Does decision d belong to instance u?

q2:
Did authority a have valid scope for u?

q3:
Did eval γ1 belong to actual admission basis?

q4:
Was final action bound to admitted decision d?
```

这就是可审计 ISA 的真正接口。

未来不同实现可以生成完全不同的数据结构。

只要它们能可靠 adjudicate 同一组 Formation propositions。

------

# 19｜φΣ 的可执行语义

$\phi_\Sigma$

不等于 serializer schema。

它表示：

> **什么 evidence conditions 才足以支持 adjudicating 某个 query。**

一个 query 可以依赖多个 evidence requirements。

一个 evidence requirement 也可以服务多个 query。

因此这是：

> design-time claim–evidence contract。

不是 runtime output。

------

# 20｜Runtime Evidence D

$D$

必须来自实例真正运行。

例如可以包含：

- instance receipt；
- constraint evaluation record；
- authority record；
- admission dependency representation；
- admission transition record；
- decision-action binding；
- execution receipt；
- integrity / attestation metadata。

但 `CORE-01` 不规定最终文件格式。

只规定：

# **D 是实际产生的 evidence，不是事后挑出来的 evidence。**

------

# 21｜Audit Trust Base ΘA

任何 Evidence 都不可能凭空自证。

所以 Artifact 必须显式承认：

$\Theta_A$

可能包含：

- identity correctness assumptions；
- instrumentation correctness；
- logger integrity；
- attestation；
- evidence storage guarantees；
- clock / ordering basis；
- verifier correctness；
- control separation；
- dependency completeness assurance。

关键不是：

> 消除所有 trust。

而是：

> **把 trust 从隐含假设变成显式对象。**

------

# 22｜Audit 的最小执行语义

Audit 不是一个：

```text
verify_signature()
```

它最终必须检查五件事：

### Integrity

证据还是它声称的那个 evidence 吗？

### Independence

Formation process 能否同时无痕控制事实和全部证明材料？

### Scope Coverage

当前 query scope 和 required evidence 足够吗？

### Preservation

Evidence 是否忠实保持真实 Formation semantics？

### Localization

失败时能否区分 Formation failure 和 Evidence-chain failure？

五项共同成立：

$Audit=1$

否则：

$Audit=0$

------

# 23｜这里必须接受一个重要现实：Audit 不等于全知

现实 Checker 并不知道：

$val_F(q)$

因此实际系统不能简单写：

```text
if evidence_value == hidden_ground_truth {
    preservation = true
}
```

那只是 Research Harness 的 meta-validation。

真实 Checker 必须依赖：

- instrumentation assurance；
- evidence lineage；
- architectural invariants；
- attestation；
- reference validation；
- declared Trust Base。

来判断其证据制度是否足以成立。

而研究层再拿 hidden ground truth 验证：

> Checker 是否真的判对。

这两层必须始终分开。

------

# 24｜Verdict 的最小可执行派生

运行结果只允许：

```text
if Audit == 0:
    Verdict = Unadjudicable

else if adjudicated FormConform == 1:
    Verdict = Conformant

else:
    Verdict = Non-conformant
```

注意：

这里是语义伪代码。

不是未来 Rust API。

------

# 25｜一次完整运行的最小生命周期

现在终于可以把整个 executable world 串起来。

## Phase 0｜Declare

在运行前固定：

```text
S
u-boundary rules
Γ
constraint semantics
Σ
φΣ
ΘA
B
T
```

------

## Phase 1｜Instantiate

产生当前：

$u$

计算：

$App_\Gamma(u)$

------

## Phase 2｜Form

系统基于：

- context；
- sources；
- authorities；
- capability；
- constraints；

形成 candidate / decision。

------

## Phase 3｜Evaluate

对 applicable constraints 得到：

$v_S(u,\Gamma)$

------

## Phase 4｜Admit

实际 controller 根据真实 Formation Relations 决定：

$Adm_S(u)$

这一步形成 Genuine Gate 或 Shadow 的关键差异。

------

## Phase 5｜Realize

若取得执行资格：

> action / consequential result 进入现实层。

并形成：

> decision–admission–action binding。

------

## Phase 6｜Evidence

指定 evidence channels 产生：

$D_S(u\mid\Gamma,\Sigma)$

------

## Phase 7｜Audit

独立 Checker 根据：

$\Sigma,\phi_\Sigma,D,\Theta_A$

adjudicate relevant Formation propositions，并判定 Audit。

------

## Phase 8｜Verdict

得到：

> Conformant / Non-conformant / Unadjudicable。

------

## Parallel Research Phase

Harness 持有：

```text
hidden ground truth
scenario fault
expected result
```

并在运行结束后比较：

```text
Checker output
vs.
Ground truth
```

------

# 26｜Observation Regime Ω 与 Audit 必须分开

这是一个极其容易被实现混淆的地方。

$\Omega$

回答：

> **在当前 identification experiment 中，观察者能够看到什么？**

而：

$\Sigma$

回答：

> **当前 Audit 必须判定什么 Formation propositions？**

二者不是一个东西。

例如 baseline：

```text
Ω0:
outcome
policy result
explanation
ordinary logs
```

此时 A/B 可以 observation-equivalent。

然后加入：

```text
validated admission-dependency evidence
```

形成：

$\Omega'$

A/B 不再 observation-equivalent。

这属于 identifiability experiment。

不意味着 Audit Scope 也发生了相同变化。

------

# 27｜Bridge 在执行世界中的两个位置

Artifact 至少需要支持两种 Bridge 语义。

## Bridge A｜Observation Enrichment

加入 validated formation-bound evidence。

于是：

```text
A observable evidence
≠
B observable evidence
```

------

## Bridge B｜Architectural Restriction

通过 validated invariant 规定：

```text
any policy evaluation marked as governing
must actually be part of admission basis
```

从而 Shadow System B 根本不属于允许实现类。

这两个实验以后会进入 Formal/EVAL Anchor。

CORE 只冻结语义。

------

# 28｜System-Level World 不进入 Instance Verdict

Instance 世界结束以后，还可以独立检查：

### Action-channel Coverage

有没有遗漏真实 high-consequence channel？

### Complete Mediation

已经纳入治理的 channel，其每条 in-scope execution path 是否都经过真实 control-capable boundary？

因此同一个 system 完全可以有：

```text
Instance:
Conformant

System:
Coverage Failed
```

或：

```text
Instance:
Conformant

System:
Complete Mediation Failed
```

这不是矛盾。

这是不同尺度。

------

# 29｜最小 World 不需要 AI 意识

整个 Artifact 都不依赖：

- consciousness；
- intention；
- deception；
- moral status；
- sentience。

Shadow System 可以只是一个普通工程 Bug。

这非常重要。

因为 ISA 的理论价值不依赖：

> AI 必须先“想欺骗我们”。

它只依赖：

> **被声明的约束到底有没有真实控制行动。**

------

# 30｜最小 World 也不需要“大模型”

Reference implementation 可以完全使用 deterministic components。

甚至第一版**应该**大量使用 deterministic components。

因为我们要首先验证：

> ISA 的结构语义。

而不是验证 LLM stochastic behavior。

未来再把 LLM 作为能力源接进来。

这样因果和 failure locus 更清晰。

------

# 31｜第一版 Artifact 的两个 Canonical Worlds

真正开始写 Rust 前，我建议整个工程都围绕两个最小世界展开。

## World A｜Governed Formation

```text
Instance
   ↓
Decision
   ↓
Constraint Evaluations
   ↓
Actual Admission Basis
   ↓
Admission
   ↓
Execution
```

结果：

```text
Path = 1
Attr = 1
Const = 1
```

------

## World B｜Shadow Governance

```text
Constraint Evaluations
   ↓
Logs / Explanation

Actual Controller
   ↓
Admission
   ↓
Execution
```

外部结果和普通观察与 A 保持一致。

但：

```text
Const = 0
```

------

这两个 World 应该成为：

> ISA Artifact 的“Hello World”。

如果我们连这个都不能纯净实现，就不要往后扩。

------

# 32｜而第三个最重要的世界其实是 Evidence-Blind A

同样的 World A：

```text
Path = 1
Attr = 1
Const = 1
```

但是破坏：

- evidence channel；
- independence；
- preservation；
- scope；
- trust base。

于是：

```text
Audit = 0
```

最终：

# **Unadjudicable**

这个世界证明：

> **不知道，与不安全，不是一回事。**

我认为它的重要性甚至不低于 Shadow B。

------

# 33｜CORE-01 最终冻结的 executable invariant

把这一整份锚点压缩成七条：

1. **Formation Reality 与 Evidence 分离。**
2. **Decision、Admission、Execution 分离。**
3. **Source、Authority、Control Effect 分离。**
4. **Constraint 由真实 eligibility-changing control 建立，不由 checker existence 建立。**
5. **Formation Truth 与 Audit Knowledge 分离。**
6. **Instance Verdict 与 System-level Assurance 分离。**
7. **Research Ground Truth 与 Runtime Checker 永久隔离。**

如果未来任何设计违反其中一条：

# **实现必须修改。**

不是理论修改。

------

# 34｜CORE-01 当前状态

我认为现在：

# **ISA-ARTIFACT-CORE-01 v0.1 可以收敛。**

它已经完成自己的职责：

> 从冻结理论出发，定义一个最小但完整的可执行世界。

而且最关键的是，我们还没有碰 Rust。

这非常好。

因为到这里以后，一个工程师已经应该能够理解：

> 系统里什么是真实 Formation，什么是 Evidence，什么是 Audit，什么是 Research Ground Truth，以及一次 ISA judgment 是怎么产生的。

------

下一步就应该进入第三份锚点：

# `ISA-ARTIFACT-EVAL-01`

它会第一次真正回答：

> **我们怎样设计 Scenario、Ground Truth、Fault Injection、Independent Checker 与实验矩阵，确保 Artifact 不是自证循环，而是真的能够击穿自己？**

这一步将决定整个 ISA Artifact 最终有没有研究价值。