# Lab 05：macOS Seatbelt 文件访问实验

## 环境

macOS。该实验依赖系统自带的 `sandbox-exec`，但 Apple 已不鼓励开发者依赖这个未公开的低层接口；不同 macOS 版本可能出现行为差异。仅在测试目录执行。

## 准备与运行

```bash
mkdir -p workspace outside
echo "allowed" > workspace/allowed.txt
echo "secret" > outside/secret.txt
chmod +x run.sh
./run.sh
```

预期：

- Workspace 内的文件可读；
- Workspace 外的文件读取返回拒绝；
- Workspace 内允许创建文件。

## 原理

`profile.sb` 使用 Seatbelt Profile 描述进程可执行的操作。Sandbox 作用于进程及其子进程，而不是只识别 `cat` 命令。

## 注意

本实验只演示文件系统访问策略，不是 Claude Code 的完整 Profile，也没有实现网络、IPC、凭证和进程资源隔离。不要把示例 Profile 直接用于生产。
