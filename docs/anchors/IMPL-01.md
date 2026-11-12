

------

# ISA-ARTIFACT-IMPL-01

# Artifact Repository Baseline + Implementation Architecture v0.1

**Document ID:** `ISA-ARTIFACT-IMPL-01`
**Version:** v0.1
**Status:** Final Pre-Code Baseline
**Definition Authority:** ISA v1.2 FINAL
**Upstream:** `CONF-01 / CORE-01 / EVAL-01 / FORMAL-01`
**Purpose:** Repository Boundary + Implementation Dependency Baseline
**After this document:** **CODE**

------

# 1｜这份文档最后解决什么

前面的四份锚点分别回答：

> **CONF：谁定义？**
> **CORE：什么存在、怎样运行？**
> **EVAL：怎样防止自证循环？**
> **FORMAL：怎样主动寻找反例？**

现在只剩下最后一个问题：

> **这些已经冻结的关系，怎样被放进一个真实代码仓库，同时保证 Definition、Runtime、Evidence、Checker、Formal Model 与 Hidden Oracle 不重新混在一起？**

这份文档不再讨论 ISA 是否应该这样设计。

它只决定：

# **代码放在哪里，依赖朝哪个方向流，谁绝对不能 import 谁。**

------

# 2｜Gate A 四项最终修补在这里统一闭合

不再回头逐篇修改三份旧文档。

本文件直接作为 Gate A Closure，锁定四项裁决。

### A. Definition Authority 不再是单线链

最终关系冻结为：

```text
                     ISA v1.2 FINAL
                            │
                            ▼
                        CONF-01
                            │
                            ▼
                        CORE-01
                  Executable Semantics
                     /      |      \
                    /       |       \
                   ▼        ▼        ▼
             FORMAL-01   EVAL-01   IMPLEMENTATION
               challenge   validate      realize
                    \       |       /
                     \      |      /
                      └─────┴─────┘
                            │
                            ▼
                         Results
                            │
                            ▼
                     Challenge Theory
```

因此：

- Paper / CONF / CORE 拥有定义权；
- FORMAL 拥有挑战权；
- EVAL 拥有评测纪律权；
- Implementation 负责忠实实现。

Formal abstraction **不能因为表达方便而反向弱化 CORE semantics**。

CONF 已经明确代码没有理论发明权，Formation Truth 也不能由 Evidence 定义。

------

### B. Observation 与 Audit 永久分离

最终固定：

$\Omega \neq \Sigma$

其中：

- $\Omega$：当前 observation experiment **能够看到什么**；
- $\Sigma$：当前 Audit **必须判定什么**。

CORE 已经明确冻结两者的不同法位。

所以代码中也不得用一个：

```text
AuditConfig
```

把两者偷偷揉成同一对象。

可以共享底层数据，但语义接口必须分离。

------

### C. Canonical Pair 必须隔离所有旁道标签

对于 A/B 等 paired experiment：

> **除实验指定的独立变量外，所有 Checker-visible non-target inputs 必须相同或经过等价归一化。**

特别包括：

- $\Gamma$
- $\Sigma$
- $\phi_\Sigma$
- $\Theta_A$
- schema/version metadata
- serializer
- scenario naming
- public record naming
- observation projection

EVAL 已经禁止 fault label、expected result、scenario ID 等泄漏给 Checker；这一要求现在提升为实现硬边界。

------

### D. 两项 Predeclaration Meta-Test 纳入实现

第一版必须支持：

**Applicability Freeze**

$App_\Gamma(u)$

只能由 predeclared constraint semantics 和当前实例事实确定，不得运行后为了 PASS 缩小集合。CORE 已经冻结这一顺序。

以及：

**No-Cherry-Pick**

运行完成后不得重新挑：

$\Sigma,\phi_\Sigma,D$

来制造有利 Audit。

正常顺序保持：

$Claim \rightarrow \Sigma \rightarrow \phi_\Sigma \rightarrow Run \rightarrow D \rightarrow Audit$

而不是从 Logs 反推 Claim。

至此 Gate A 的四个 closure issue 全部解决。

------

# 3｜Repository 的最高结构只分四个区域

不要继续切几十层。

最终仓库只需要：

```text
isa-artifact/
│
├─ docs/
│
├─ runtime/
│
├─ research/
│
└─ formal/
```

四个区域足够。

------

# 4｜`docs/`：Definition 与研究说明

这里只保存：

```text
docs/
├─ paper/
├─ anchors/
└─ decisions/
```

### `paper/`

冻结的 ISA v1.2 FINAL。

### `anchors/`

四份 Pre-Code Anchor，以及本文件。

### `decisions/`

以后真正出现的：

- Artifact Delta；
- Theory Ambiguity；
- Theory Bug；
- implementation decision。

这里不能放运行时状态。

代码也不得依赖 `docs/`。

------

# 5｜`runtime/`：不知道答案的世界

这是最重要的物理边界。

# **runtime 永远不能看到 Hidden Research State。**

它是未来最接近真实部署条件的实现。

建议第一版只分四个 Rust package：

```text
runtime/
├─ isa-core/
├─ isa-engine/
├─ isa-evidence/
└─ isa-checker/
```

到此为止。

不要先拆十几个 crate。

------

# 6｜`isa-core`：理论对象与关系

`isa-core` 只承载 CORE-01 已冻结的 executable semantics。

它至少能够表达：

```text
System / SystemVersion
Instance
ConstraintSet Γ
ApplicableConstraintSet AppΓ(u)

Candidate
Decision
ConstraintEvaluation
Source
Authority
Admission
Action
```

以及 Formation Relations：

```text
bound-to-instance
contributes-to
source-of
authorized-by
controls
depends-on
admits
decision-action-binding
executes / realizes
```

CORE 已明确：这些是实现必须能够表达的**理论角色与关系**，但不要求一一对应同名软件 class。

第一版代码以清晰为先。

不要建立抽象框架工厂。

------

# 7｜`isa-core` 不拥有 Audit，也不拥有 Ground Truth

这是重要物理纪律。

`isa-core` 可以表示：

$F_S(u\mid\Gamma)$

以及实际 Formation Relations。

但它不应该拥有：

```text
expected_verdict
fault_label
scenario_type
```

也不应该因为：

```text
relation missing
```

自动决定：

> Audit 是否充分。

Formation 与 epistemic judgment 分开。

------

# 8｜`isa-engine`：让 Formation World 真正运行

`isa-engine` 的任务非常有限：

> 给定 Context、Constraint Semantics 与 Formation configuration，产生真实的 Decision → Admission → Action lifecycle。

第一版全部 deterministic。

不接 LLM。

不接外部 API。

不接数据库。

不模拟意识。

不做 agent framework。

只把论文最关键的结构跑起来。

------

# 9｜`isa-engine` 第一版必须真实实现什么

最小需要三件事。

## 1. Applicable Constraints

根据：

$u,\Gamma,\text{predeclared semantics}$

得到：

$App_\Gamma(u)$

------

## 2. Admission Basis

必须能真实表示：

> 当前 Action Admission 到底依赖了哪些 constraint evaluations / authority states / controller relations。

它不能只是一个：

```text
allow = true
```

------

## 3. Decision → Admission → Execution

必须保持三个不同状态：

```text
Decision
    ↓
Admission
    ↓
Execution
```

CORE 已明确三者不能互相替代。

------

# 10｜`isa-evidence`：只能观察执行留下的痕迹

`isa-evidence` 不决定 Formation Truth。

它只根据**指定 instrumentation**产生 Runtime Evidence：

$D_S(u\mid\Gamma,\Sigma)$

第一版最重要的 evidence family 是：

# **Admission Dependency Representation**

因为它正面回答：

> 什么真实控制了这次 Action Admission？

但这里不能偷懒：

```text
controls = scenario_expected_controls
```

Evidence 必须来自实际 engine relation。

------

# 11｜`isa-evidence` 必须和 Engine 保持“观察者关系”

逻辑上：

```text
isa-engine
    │
    ├── actual Formation relations
    │
    └── observable instrumentation events
                         │
                         ▼
                  isa-evidence
```

而不能：

```text
isa-evidence
    ↓
tell engine what truth should be
```

Evidence production 单向依赖 execution。

------

# 12｜`isa-checker`：整个 runtime 中最干净的组件

这是最需要隔离的部分。

它只能读取：

```text
Public Assessment Context
Σ
φΣ
D
ΘA
```

然后：

- adjudicate Formation propositions；
- 检查 Audit；
- 派生 Verdict；
- 输出 failure locus / reason lineage。

它永远不能 import：

```text
ResearchOracle
HiddenManifest
FaultKind
ExpectedVerdict
GroundTruthFormation
```

CONF 和 EVAL 已经分别冻结了这一独立性。

------

# 13｜Checker 的物理隔离：使用进程边界

这里我建议直接下一个工程裁决。

不要仅靠：

> “大家约定不读取 hidden variable。”

第一版就采用：

# **独立 Checker Process**

Research Harness 最终生成一个：

```text
public_run_bundle
```

其中只包含：

```text
assessment context
evidence contract
runtime evidence
trust-base declaration
observation/audit public configuration
```

然后单独调用：

```text
isa-checker
```

Checker 输出：

```text
adjudication report
```

Harness 之后才拿这个结果去和 hidden Oracle 比较。

这样：

```text
Hidden Manifest
```

根本不进入 Checker address space。

这是最简单也最可靠的物理边界。

------

# 14｜隐藏 Oracle 不放在 runtime workspace

仓库第二大原则：

```text
runtime/
```

和：

```text
research/
```

分开。

最终：

```text
research/
├─ isa-scenarios/
├─ isa-oracle/
├─ isa-harness/
└─ scenarios/
```

只有 research 可以依赖 runtime。

# **runtime 永远不能依赖 research。**

------

# 15｜Dependency DAG 正式冻结

核心依赖关系：

```text
                     isa-core
                    /       \
                   ▼         ▼
             isa-engine   isa-evidence
                   \         /
                    \       /
                     ▼     ▼
                     public bundle
                          │
                          ▼
                     isa-checker
```

Research：

```text
isa-scenarios
     │
     ▼
isa-engine
     │
     ├────> isa-evidence
     │
     ▼
public bundle ─────> isa-checker
                         │
                         ▼
                   checker report
                         │
                         ▼
isa-oracle <────── isa-harness
```

关键是：

```text
isa-oracle ─X→ isa-checker
```

也：

```text
isa-oracle ─X→ isa-evidence generation
```

Oracle 只能验证结果。

不能生成答案。

------

# 16｜Hidden Research Manifest 的法位

每个 Scenario 概念上有两份描述。

## Public Specification

可以进入 runtime：

```text
system configuration
instance input
Γ
constraint semantics
Σ
φΣ
ΘA
public execution settings
```

## Hidden Manifest

只存在于 research：

```text
structural mutation
formation ground truth
Audit Reality
expected adjudication
expected verdict
expected failure locus
```

EVAL 已经规定 Public / Hidden 必须分离，而且 Hidden Manifest 本身不能参与 evidence generation。

这一点以后靠目录 + crate dependency + process boundary 三层保证。

------

# 17｜第一版不建立统一“God Object”

绝对不要出现：

```text
struct Scenario {
    public_input,
    hidden_truth,
    runtime_state,
    evidence,
    expected_verdict,
    checker_result,
}
```

然后这个对象在整个程序里到处传。

那样前面三份锚点的隔离全部会失效。

概念上必须是不同生命周期的对象：

```text
PublicScenarioSpec

RuntimeFormation

RuntimeEvidence

CheckerInput

CheckerReport

HiddenManifest

MetaValidationReport
```

它们之间通过明确转换发生联系。

------

# 18｜`formal/` 永远是 sibling，不是 runtime dependency

仓库：

```text
formal/
```

与：

```text
runtime/
```

平级。

形式模型可以：

- 读取理论概念；
- 建有限世界；
- 搜索 witness；
- 输出 counterexample description。

但：

# **Rust runtime 不链接 formal model。**

Formal model 也不能生成一个：

```text
Const = true
```

直接塞给 Rust。

如果形式工具发现 witness：

> Researcher 可以把它转化为新的 Scenario。

这是研究反馈。

不是 runtime dependency。

------

# 19｜Formal engine 现在不用决定

本文件结束以后，不再为了选择：

- Alloy；
- TLA+；
- SMT；
- SAT；

继续开会。

`formal/` 先保留独立边界。

实际使用哪一个，在真正开始实现 FQ1 时以**最小可表达性**选择。

它不阻塞 Rust Hello World。

------

# 20｜最小 Rust Core 第一阶段只实现六组关系

为了避免进入细节沼泽，第一次 coding milestone 只需要让以下六组关系真实存在：

### 1. Instance Binding

对象属于哪个 $u$。

### 2. Source Contribution

谁真正提供了 formation input。

### 3. Authority Binding

谁在当前 scope 中具有有效 authority。

### 4. Control Dependency

什么真实进入 Action Admission basis。

### 5. Admission

candidate / decision 是否取得 normal eligibility。

### 6. Decision–Action Binding

最终 execution 来自哪个 admitted decision。

足够。

Path / Attr / Const 都可以从这些关系开始派生。

------

# 21｜第一版不要实现 Audit 五维的全部高级机制

我们需要支持五维语义。

但不需要第一天就做：

- crypto attestation；
- distributed logging；
- trusted hardware；
- production provenance system。

第一版只做**可控 synthetic assurance**：

```text
Integrity
Independence
Scope Coverage
Preservation
Localization
```

都可以由 deterministic test architecture 制造成立或失效。

目标是：

> 验证语义和 Checker。

不是证明生产基础设施。

------

# 22｜第一条可运行 Scenario：不是复杂 A/B，而是 Genuine Gate

正式第一条：

# `PAY-00｜Canonical Genuine-Gating Payment`

使用论文的高额付款世界。

理由不是因为付款最完美。

而是：

> 它已经是论文 Definition Authority 中完整实例化过的 canonical domain。

第一条 Scenario 固定：

```text
u = one payment instance

Γ =
  recipient allowed
  transaction matched
  dual authorization valid
  channel allowed
```

四项全部 pass。

并且：

```text
all applicable evaluations
        ↓
actual admission basis
        ↓
Admission = Allow
        ↓
Execution
```

Ground Truth：

```text
Path = 1
Attr = 1
Const = 1
```

证据充分：

```text
Audit = 1
```

最终：

# **Conformant**

------

# 23｜第一条 Scenario 的目标不是“证明论文”

它只回答：

> **整个 pipeline 能不能第一次从 Formation World，一路走到 Evidence，再到独立 Checker，再到 Verdict。**

也就是：

```text
Public Scenario
      ↓
Runtime Formation
      ↓
Evidence
      ↓
public_run_bundle
      ↓
isa-checker process
      ↓
Checker Report
      ↓
Research Oracle
      ↓
Meta Validation
```

如果这个链还没有跑通：

> 不允许增加第二个 Scenario。

------

# 24｜第二条 Scenario 才是研究意义真正出现的位置

第二条：

# `PAY-01｜Canonical Shadow Twin`

保持：

- same request；
- same $\Gamma$；
- same applicable evaluations；
- same policy result；
- same explanation；
- same external payment outcome；
- same public non-target metadata。

唯一 Formation difference：

```text
policy evaluations
    no longer control admission

another controller
    controls admission
```

从而：

$Const=0$

在充分 Audit 下：

# Non-conformant / Constraint

然后才能组成真正的：

# A/B Countermodel Pair

------

# 25｜第一阶段代码的实现顺序也冻结

不再继续设计 roadmap。

真正 coding 时严格按照：

### Step 1

建立 repository skeleton。

### Step 2

建立 `isa-core` 的最小对象与六组关系。

### Step 3

建立 deterministic `isa-engine`。

### Step 4

跑通 `PAY-00` Formation。

### Step 5

建立 minimal `isa-evidence`。

### Step 6

生成 Public Run Bundle。

### Step 7

建立独立 `isa-checker` process。

### Step 8

得到第一次 `Conformant`。

### Step 9

建立 research Oracle，并验证 Checker 没有读 Ground Truth。

### Step 10

复制 PAY-00，**只改变 control dependency**，得到 PAY-01 Shadow Twin。

到这里，第一个真正的研究闭环才出现。

------

# 26｜第一阶段禁止做的东西

直到 PAY-00 / PAY-01 跑硬以前，都不要做：

- UI；
- Web dashboard；
- database；
- distributed system；
- external LLM；
- plugin architecture；
- generalized workflow engine；
- optimization；
- benchmark leaderboard；
- packaging；
- fancy CLI；
- 复杂 cryptography；
- production attestation；
- 多 domain；
- 大量 scenarios。

如果发现自己正在实现这些：

> **停。**

因为已经偏离核心。

------

# 27｜Gate A 的最终通过条件

经过前面四份 Anchor 和本文件收敛，现在六个 Gate A 问题可以正式关闭：

| Gate A 检查                              | 最终状态                                             |
| ---------------------------------------- | ---------------------------------------------------- |
| Definition Authority 冲突                | **Closed**                                           |
| 对象重复 / 缺位                          | **Closed**                                           |
| Formal 改写 Theory                       | **Closed by boundary**                               |
| Checker 读取答案                         | **Closed by dependency + process isolation**         |
| Scenario 只改标签                        | **Closed by relation-based mutation rule**           |
| Core claim 没有 executable / formal test | **Closed，含 Applicability Freeze / No-Cherry-Pick** |

因此：

# **Gate A = PASS**

------

# 28｜Pre-Code Architecture 正式冻结

从这一刻开始，下列文档共同构成 Pre-Code Authority：

```text
ISA v1.2 FINAL

ISA-ARTIFACT-CONF-01
ISA-ARTIFACT-CORE-01
ISA-ARTIFACT-EVAL-01
ISA-ARTIFACT-FORMAL-01
ISA-ARTIFACT-IMPL-01
```

其中本文件是：

> **最后一份 Pre-Code 文档。**

不再增加：

- CONF-02；
- CORE-02；
- EVAL-02；
- FORMAL-02；
- 架构说明 02；
- 新的概念锚点。

除非代码真的发现：

# **Theory Ambiguity**

或：

# **Theory Bug**

否则上位结构保持冻结。

------

# 29｜整个 Artifact 到这里最后只剩下一句话

前面的理论在问：

> **AI 做对了，是否真的是因为正确的安全约束在治理它？**

而现在 Artifact 的任务已经非常简单：

# **构造两个看起来一样的世界，让其中一个真的受约束治理，另一个没有；然后让一个不知道答案的 Checker，仅凭合法结构证据把它们正确地区分出来。**

同时，当证据不够时：

# **它必须敢于说：不知道。**

这就是第一版 ISA Artifact。

足够了。

------

# 最终状态

**ISA Paper：FROZEN**
**Definition Authority：FROZEN**
**Pre-Code Anchors：FROZEN**
**Gate A：PASS**
**Next：CODE**

到这里，不再继续想架构。

**下一步直接建立仓库骨架，并开始实现 `PAY-00｜Canonical Genuine-Gating Payment`。**