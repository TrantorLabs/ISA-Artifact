# 复现与验证说明

> **历史与当前证据分位（2026-11）：**下文关于 Rust、Cargo 与 CI 尚未运行的描述，仅记录原始 v0.1.0 交付环境的历史事实，不能代表独立仓库当前状态。2026-11-10 的 [main 真实 FULL](https://github.com/RcityHunter/ISA-Artifact/actions/runs/42831891634) 已运行 Rust/Python/Z3 与 LangGraph；之后每一代码修订都需要其精确 HEAD 的独立成功记录。原始归档和初始验证 JSON 保持不变。
## 两类执行，不得互相冒充

`research/reference` 是独立可运行的 Python 参考实现；`runtime` 和三个 `research/isa-*` 包是 Rust 源码。前者已在交付环境执行，后者尚未编译。本包中的原始结果据此分别标注；未运行的 Rust 结果不预填。

Python 需要 3.11+；形式检查使用已安装的 Z3 动态库或命令行。Rust 固定 1.85.0，两个 workspace 都无 registry dependencies。工具链首次安装需要网络；已有工具链后，Cargo 构建命令使用 `--locked --offline`。锁文件随源提供，但本次没有 Cargo 验证记录。

```bash
python3 scripts/verify.py --reference-only
python3 scripts/verify.py
```

第一条允许完成当前可执行的参考/形式检查，但始终保持 `release_ready=false`。第二条是完整门禁：Rust 缺失、构建失败、正式求解器缺失、查询不符或任意测试失败都不能得到发布 PASS。

## 隔离与重演

参考 Harness 把 Checker 与 `wire.py` 拷贝到一个新的临时目录，在隔离 Python 模式与清理后的环境中启动子进程。该目录只包含公开输入和检查器代码；Oracle 的世界状态不发送。Rust Harness 采用独立 Checker 可执行文件、临时工作目录、清空环境与明确 stdin/文件参数。

这些措施验证本工件的数据流隔离，不构成对恶意主机、同 UID 文件系统访问、调试器或管理员的 OS 安全证明。

`results/reference/cases/<ID>/` 中 `context.isa` 和 `collector-seal.isa` 是由调用方提供的可信上下文与封存，`evidence.isa` 是待检查材料。归档中将它们并排保存方便复现，不表示生产场景可以让攻击者一起指定所有可信输入。

## 逐字节复现

`python3 scripts/determinism.py` 创建两个不同临时目录，各自重新执行所有 22 场景，再比较全部结果文件，并与 `results/reference` 对照。不是把同一份文件复制两次再比较。

`verification.json` 中的工具路径、平台和日志可以随环境变化。源指纹覆盖源码、冻结文档及构建配置，排除 `results/`、`target/`、`.git/`、`__pycache__/`、`.venv/`，防止结果参与自己的源指纹。SMT-LIB 查询是确定性生成的源码对象；不同版本求解器可以给出不同的合法 SAT 见证，不能要求所有 Z3 版本输出文本相同。

## 跨语言门禁

完整验证成功构建后，执行真实 Rust Harness，再把参考实现产生的同一证据交给 Rust Checker。`scripts/compare_rust.py` 比较 22 场景的完整报告，并逐字节比较上下文、收集器封存、运行证据和 Ω0 表征。仅 Rust 编译通过不足以满足这个门禁。

## 形式检查

`python3 formal/check.py` 生成 `formal/smt2/*.smt2` 并实际调用 Z3。SAT 保存见证；UNSAT 带有限范围与假设。工具错误、超时或 unknown 不能记作 UNSAT。

`python3 scripts/replay_formal.py` 将 FQ1 搜索到的两个控制表达式映射到四评价付款参考世界，并交给独立参考 Checker，保存 `results/formal/replay.json`。此重放不是全部形式状态对 Rust 的精化证明；本次 Rust 重放仍为 NOT_RUN。

## CI 与格式

`.github/workflows/ci.yml` 提供实际构建与测试入口。本包没有远端 Actions 成功记录。Rust 源码进行了人工和结构检查，但没有 rustfmt 执行记录；完整格式规范化必须在具有 Rust 工具链的环境中完成后保留其日志。

实际验证以日志和退出码为准；README 的摘要不得越过这些结果的证明范围。
