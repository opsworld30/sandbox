# Lab 19：Tool-level Sandbox Expansion（单次命令扩权）

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
python3 -m unittest -v
```

## 目标

演示 Gemini CLI 类似的按命令申请额外能力的设计：

- Base Policy 默认禁止网络；
- Agent 为某条命令申请访问一个精确域名；
- 用户批准后，只把能力附加到该 command_id；
- 下一条命令仍然使用原始 Base Policy。

## 安全边界

这是自研 Runtime 的概念模型，不是 Gemini CLI 的真实 API Schema，也没有执行网络请求。生产实现必须绑定命令摘要、Session、目标域名、审批主体、过期时间和重放保护。
