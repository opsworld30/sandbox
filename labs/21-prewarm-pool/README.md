# Lab 21：Prewarm / Snapshot / Pool 生命周期模拟

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
python3 -m unittest -v
```

## 目标

用可控时钟模拟：

- Prewarm Environment 未附加 Session 时的短 TTL；
- attach 多个 Session；
- 活动时刷新 idle deadline；
- 空闲后进入 Suspended；
- checkpoint 保留期限；
- 删除 Session 不等于删除共享 Environment。

## 安全边界

这是帮助理解生命周期的本地状态机，不调用 OpenAI API，也不代表所有云 Sandbox 的默认参数。共享 Environment 会共享 workspace，因此不可信任务之间不能仅靠创建多个 Session 获得隔离。
