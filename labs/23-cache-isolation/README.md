# Lab 23：Shared Cache、Session Cache 与完整性校验

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 demo.py
python3 -m unittest -v
```

## 目标

- 将依赖文件按 SHA-256 内容寻址；
- Session 使用自己的可写副本；
- 复用前重新校验基础 Cache 的摘要；
- 检测缓存内容被意外篡改。

## 安全边界

这是应用层完整性检查。文件权限和 Hash 校验不能替代签名、可信来源验证、不可变存储和租户隔离。共享可写 Cache 可能造成跨 Session 污染。
