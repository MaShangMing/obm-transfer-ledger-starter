# 库存调拨基线

本目录提供单笔库存调拨的起始代码和合成输入。新增批量事务的公开约定在proposal.json中，当前基线用于后续扩展。

| 文件 | 用途 |
| --- | --- |
| app/store.py | Store、apply、snapshot、close的起始实现，当前逐笔修改库存并持久保存成功快照。 |
| app/journal.py | 起始日志读取与保存模块，供扩展帧验证和恢复使用。 |
| app/lowlevel.py | 固定帧编码、完整写入、fsync和同步截断，保留不改。 |
| data/seed.json | 三个储位的合成数量与容量。 |
| data/moves.jsonl | 普通调拨、循环换位和容量边界的公开输入，按行解析后调用apply。 |
| Dockerfile | LinuxCPU、Python3.12.14标准库环境；复制app和data，不安装第三方包。 |
| README.md | 文件用途与运行说明。 |

从本目录构建镜像：

```sh
docker build -t transfer-ledger-starter .
```

在Linux上以Python3.12运行，设置PYTHONPATH指向app即可导入Store。调用方先创建空工作目录，将seed.json解析为字典并传给Store，再把moves.jsonl逐行解析后传给apply；snapshot读取状态，close结束使用。一个目录同时只由一个Store对象使用，线程并发限定同一对象，重开前结束旧对象的使用。

帧由四字节大端长度、UTF-8JSON载荷和32字节SHA-256摘要组成，载荷上限1MiB。append_frame完成短写循环、文件fsync以及Linux上的新建文件父目录同步；hook依次收到before_write、after_write、after_sync。trim_tail截断并同步文件。首帧绑定种子，业务JSON布局由后续实现选择。这些底层函数不代替事务、幂等、版本或恢复逻辑。

本目录只包含起始代码、运行环境和公开输入。数据为专门设计的合成记录，不包含客户资料。
