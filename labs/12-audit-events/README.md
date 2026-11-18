# Lab 12：Sandbox Audit Event 与 Secret Redaction

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
```

程序会输出 JSONL 审计事件。Session ID 经过 SHA-256 摘要处理；Token / Authorization 等敏感字段会被脱敏；不记录原始命令输出。这里的无盐 Hash 只是演示稳定标识，不是匿名化；生产环境应使用带服务端密钥的 HMAC，并限制关联权限。

## 进一步实验

在 demo 中加入 `api_key`、`password`、`Bearer ...` 等字段，确认不会把明文 Secret 写入日志。

## 安全边界

日志脱敏是纵深防御，不应依赖正则表达式保护所有秘密。生产系统应采用 allowlist 方式定义可记录字段，限制日志访问与保留期，并避免记录原始环境变量、命令行参数和文件内容。
