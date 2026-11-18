# Lab 14：Resource Limits——CPU、Memory、File Size

## 环境

Linux + Python 3.10+。建议 disposable VM。脚本会主动触发受限条件，但每个测试都有上限。

## 运行

```bash
chmod +x run.sh
./run.sh
```

实验使用 Python `resource.setrlimit`：

- CPU：限制 CPU 时间；
- Address Space：限制虚拟地址空间；
- File Size：限制单个文件大小。

## 重要边界

RLIMIT 不是完整的多租户资源管理。进程数、总内存、CPU 配额、IO、网络和整组进程生命周期通常还需要 cgroup v2。不要在生产机器或包含重要任务的环境运行资源压力实验。
