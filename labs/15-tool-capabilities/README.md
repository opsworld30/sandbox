# Lab 15：Tool Capability Model

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
python3 -m unittest -v
```

## 实验目标

为 Shell、Browser、MCP 三种 Tool 分配不同能力：

- Shell：只能读写 Workspace，不允许联网；
- Browser：只允许访问配置的公网域名，不允许读 Workspace；
- MCP Issue Reader：只允许读取 issue，不允许写入或访问本地文件。

## 观察

Tool 的授权不能只看 Agent 有没有权限，还要看调用的是哪个 Tool、执行在哪个进程 / 服务、底层能力由谁强制执行。

本实验是应用层 Capability Broker，不是 OS Sandbox。生产环境需要把授权落实到对应进程、代理或远端服务。
