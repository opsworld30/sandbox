# Lab 13：Multi-Agent Workspace 与显式 Artifact 交换

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
```

程序创建 Agent A、Agent B 两个独立目录。A 写入自己的文件后，不能通过 Artifact Broker 直接读取 B 的目录；只有经过 Broker 发布的文件才会复制到 B 的 inbox，并附带 SHA-256。

## 安全边界

这是单进程中的逻辑隔离演示。两个目录仍由同一个 OS 用户拥有，不能抵御恶意进程直接访问另一个目录。生产环境应给每个 Agent 使用独立 UID / Container / MicroVM / Workspace ACL，并通过受控 Artifact API 交换数据。
