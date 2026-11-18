# Lab 20：Windows Sandbox 配置实验（.wsb）

## 环境

Windows 10/11 Pro、Enterprise 或 Education（具体版本与硬件要求以 Microsoft 文档为准），并启用 Windows Sandbox 可选功能。Windows Home 通常不提供该功能。

## 准备

在宿主机创建：

```powershell
New-Item -ItemType Directory -Force C:\SandboxLab\workspace
Set-Content C:\SandboxLab\workspace\hello.txt "hello from host workspace"
```

## 运行

双击 `sandbox.wsb`，或从 PowerShell 启动：

```powershell
Start-Process .\sandbox.wsb
```

Sandbox 中映射的 workspace 为只读；网络、剪贴板、打印机、音频和视频输入均关闭。关闭 Windows Sandbox 后，临时 VM 内的更改会丢弃。

## 安全边界

这演示的是 Windows Sandbox 的隔离 VM 配置，不是 Codex Windows Sandbox 的实现，也不是 per-process Job Object 示例。不要把映射目录设置为可写，除非你确实需要把不可信工作负载的修改带回宿主机。
