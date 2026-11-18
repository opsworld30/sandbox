# Lab 18：Sandbox Security Regression Matrix

这个 Lab 把前面的小实验组合成一次回归检查。

## 环境

Python 3.10+。网络与工具策略测试不需要第三方依赖。按需安装 Node.js / npm。

## 运行

```bash
chmod +x run.sh
./run.sh
```

## 覆盖范围

- Network allowlist：exact hostname、suffix trick、IP literal；
- Policy Engine：deny-wins、allow 交集、网络不可重新打开；
- Tool Capability：Shell / Browser / MCP 分权；
- Mini Runtime：命令 allowlist、路径越界、Session 生命周期。

这不是完整 Escape Test。真实的 OS-level 文件、网络、进程和资源隔离，还必须在 disposable VM 中分别测试，不能用应用层单元测试替代。
