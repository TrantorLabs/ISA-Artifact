# 0.1.0 — 源码候选与参考证据交付

依据 ISA v1.2 FINAL 和六份原始文档实现七个标准库 Rust 包、两个 workspace、独立 Checker 进程、22 个定向场景、独立 Oracle、系统级有限图检查、八组形式查询及参考执行。

附带真实参考测试、故意错误 Checker 的变异结果、Z3 原始求解与见证、可复现报告、来源指纹、差额账本和完整门禁脚本。

**不是已验证的 Rust release。** 当前环境没有 Rust 工具链，相关门禁为 NOT_RUN。任何后续正式发布必须先执行全量 `scripts/verify.py`，并保留对应 source fingerprint 和实际结果。
