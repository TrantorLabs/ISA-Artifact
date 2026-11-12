# ISA Artifact 0.1.0｜交付与验证报告

## 总裁决

**源码已交付；已执行的参考/形式验证通过；Rust 发布验证未完成。**

机器状态：`VALIDATION_INCOMPLETE`，`release_ready: false`。

当前环境没有 rustc、cargo、rustfmt，无法下载工具链。Rust 源码因此没有编译或执行记录。本报告不会把 Python 参考执行、静态检查或 Z3 结果冒充 Cargo 测试。

## 交付范围

7 个标准库 Rust 包，分别置于运行时和研究两个 Cargo workspace；11 个 Rust 源文件，共 1436 行。运行时包含 core、engine、evidence 和独立 checker；研究部分包含 scenarios、oracle 和 harness。另有独立 Python 参考实现、SMT-LIB 查询与 Z3 接口、22 个定向场景、复现脚本、CI 配置、原始证据和差额账本。

用户提供的 6 份锚点与 ISA v1.2 FINAL 主稿共 7 份输入保持字节不变。来源文件及 SHA-256 见 `docs/SOURCE_REGISTRY.json`。代码实现以这些冻结语义为准，必要的实现选择与评测例子澄清见 `docs/decisions/ARTIFACT_DELTA.md`。

## 实际执行结果

| 检查 | 实际结果 | 原始证据 |
| --- | --- | --- |
| Python 参考单元/集成测试 | 60 个测试通过 | `results/validation/reference-tests.log` |
| 独立子进程 Checker 与 Oracle 对照 | 22/22 定向场景一致 | `results/reference/matrix.csv` |
| 三种判定 | 5 符合、8 不符合、9 不可判定 | `results/reference/summary.json` |
| A/B 观察等价 | Ω0 逐字节相同；非目标上下文相同；结构证据不同 | `results/reference/pair.json` |
| Checker 源码变异测试 | 6/6 个故意错误版本被检出 | `results/validation/mutation-report.json` |
| Z3 实际求解 | 17 个查询完成，覆盖 8 组 | `results/formal/queries.json` |
| 独立有限枚举 | 2,560 个世界 | `results/formal/enumeration.json` |
| 形式见证重放 | 已将求解器找到的控制程序映射并在独立参考 Checker 重放 | `results/formal/replay.json` |
| 双次新鲜复现 | 两次独立执行的 356 份文件逐字节一致，并与归档一致 | `results/validation/determinism.json` |
| 来源/依赖/导入边界 | 7 项静态检查通过 | `results/validation/boundary-check.json` |

上表中的负例被正确识别，意味着测试通过，并不意味着被测场景安全。定向场景计数不是真实业务安全概率。

## 尚未执行

| 项目 | 状态 |
| --- | --- |
| Rust runtime workspace 构建与 Cargo 测试 | NOT_RUN |
| Rust research workspace 构建与 Cargo 测试 | NOT_RUN |
| 真实 Rust Harness | NOT_RUN |
| Rust/Python 输入、证据、报告逐项对照 | NOT_RUN |
| Rust 形式见证重放 | NOT_RUN |
| rustfmt / clippy | NOT_RUN |
| 远端 GitHub Actions | NOT_RUN |
| 生产身份鉴证、可信硬件、真实支付或真实 LLM | NOT_IMPLEMENTED / NOT_TESTED |

这意味着现在不能给出“Rust 无编译错误”“Rust 测试全部通过”或“生产可用”的结论。源码必须在有工具链的环境中通过完整门禁后，才可改变发布状态。

## 逻辑锤刺得到的实质结果

**真实控制不等于读取。** 检查器不仅看评价是否被访问，还独立执行有限控制程序，在固定 Γ 语义下改变评价值，区分真实资格依赖、只读取不控制和影子检查。

**证据失效不等于形成失败。** 参考测试保持真实世界不变，分别破坏完整性、独立性、范围、语义保持与定位，要求保留不可判定。另有“真实形成不符合但证据不足”的混合场景，防止通过隐藏真值猜答案。

**弱桥接被实际击穿。** `FQ2-WEAK` 得到 SAT：仅补充程序证据不能自动证明路径和归因。完整有限桥接要覆盖所需形成关系；这个结果没有被抹成全绿。

**信任根失陷的界限被保留。** `FQ5-TRUST-BREACH` 得到 SAT：若连可信收集器/监测输入都可被伪造，证据-only Checker 可能虚假确定。该情形超出声明信任假设，不被包装成已经防御成功。

**预声明不能事后改写。** 适用性缩减、契约变更和挑选有利证据均有对应测试；参考程序原先可变输入引用的问题已修复为运行快照，并加入回归测试。

## 重要范围

运行时是四评价、有限 DAG、单付款实例的具体实现。形式层是更小的有限关系投影；已重放 FQ1，但不声称全部形式状态与 Rust 已完成精化证明。两个 workspace、清空环境和独立进程防止本工件中答案误传，不是恶意主机安全沙箱。校验和不是认证，真实信任基础仍需独立工程保证。

## 完整验证命令

安装仓库固定 Rust 1.85.0 工具链，并提供 Python 3.11+ 和 Z3 后：

```bash
python3 scripts/verify.py
```

此命令缺少工具或任一门禁失败时返回非零，不会继续声称 release ready。当前已执行的是：

```bash
python3 scripts/verify.py --reference-only
```

## 可追溯信息

- Python：`3.13.5`。
- 形式求解器：`Z3 4.13.3.0`。
- 测试对应源码 SHA-256：`5da6e0d5e17451105a44cf68d33fa888e06acdccee6ac8dde320a7658b1597e5`。
- 源指纹纳入文件数：81，排除结果、构建目录和缓存。
- 参考 SRG 仓库 commit：`b428ada1c4805cb9b1db20562ca44d185ac336a0`。
- 远端仓库未创建、未修改、未发布；论文未改动。
