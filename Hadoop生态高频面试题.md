# 一、HDFS 相关
## 1. HDFS 架构及其各组件作用
HDFS 采用主从架构：
- NameNode（Master）
管理文件系统命名空间，维护目录树、文件与数据块的映射关系、文件权限等元数据。所有元数据存于内存，持久化到磁盘的 fsimage + edits 文件。不存储真实用户数据。
- DataNode（Slave）
负责存储实际数据块（Block，默认 128MB，可配置），定期向 NameNode 上报心跳与块信息。
- SecondaryNameNode
并非 NameNode 热备，核心职责是合并 edits 日志到 fsimage，减轻 NameNode 启动时的检查点压力。
## 2. HDFS 写入流程（详细）
Client 向 NameNode 发起文件创建请求。
NameNode 检查权限、路径合法性，通过则分配数据块与节点列表。
Client 构建流水线（Pipeline），按副本数依次向 DataNode 发送数据包。
各 DataNode 边接收边向下传递，并逐级返回确认包（ACK）。
写入完成后，Client 告诉 NameNode 关闭文件，NN 更新元数据。
## 3. HDFS 读取流程
Client 向 NN 请求文件对应的数据块位置信息。
NN 返回块所在的 DN 列表，并按网络拓扑就近排序。
Client 直接与 DN 建立连接读取数据。
读取失败自动切换其他副本节点。
读完所有块后合并为完整文件。
## 4. 三副本放置策略
默认：
- 第一副本：客户端所在节点（本地优先）。
- 第二副本：同一机架不同节点。
- 第三副本：不同机架节点。
目的：保证可靠性、减少跨机架网络开销、提高读取效率。
## 5. 小文件问题及解决方案
- 危害：
大量小文件占用 NameNode 大量内存。
大量分片导致 MapTask 过多，计算引擎效率极低。
- 解决方案：
合并小文件（在采集 / 入仓阶段）。
使用 Har 文件、SequenceFile、Parquet 等容器格式。
Hive 级别的合并：SET hive.merge.mapfiles=true。
使用 CombineFileInputFormat 合并分片。
# 二、YARN 相关
## 1. YARN 架构与核心组件
- ResourceManager（RM）
全局资源调度器，负责整个集群的资源分配与管理，处理应用提交。
- NodeManager（NM）
每个节点的代理，管理本节点资源（CPU / 内存），启动容器（Container）并监控。
- ApplicationMaster（AM）
每个应用一个 AM，向 RM 申请资源，与 NM 协作启动 Task，监控任务运行。
- Container
资源抽象，封装 CPU、内存等，任务运行的最小单位。
## 2. YARN 任务提交流程
Client 向 RM 提交应用。
RM 分配一个 Container 启动 AM。
AM 向 RM 注册并申请资源。
RM 分配资源（Container），AM 指令 NM 启动 Task。
Task 运行并向 AM 汇报状态。
运行完成，RM 回收资源。
## 3. 调度器种类
- FIFO Scheduler：先进先出，生产不用。
- Capacity Scheduler：多队列，按容量分配，Hadoop 默认。
- Fair Scheduler：公平共享资源，适合多用户并发。
# 三、MapReduce 相关
## 1. MapReduce 完整流程
InputFormat 分片：将文件切分为 InputSplit，对应 MapTask。
Map 阶段：执行 map 函数输出 <K,V>。
Shuffle 阶段：分区、排序、合并、溢写、拉取。
Reduce 阶段：聚合计算，输出结果。
## 2. Shuffle 详细过程
Map 输出 → 分区（Partitioner）→ 排序（Sort）→ 溢写到磁盘（Spill）→ 合并（Merge）→ Reduce 拉取数据（Fetch）→ 归并排序 → 进入 reduce 方法。
Shuffle 是 MR 性能瓶颈核心。
# 四、Hive 相关（最重要）
## 1. Hive 本质
- Hive 是基于 Hadoop 的数据仓库工具，提供类 SQL（HQL）接口，底层将 SQL 翻译为 MR/Tez/Spark 任务执行。
- Hive 不是数据库：不支持行级增删改（旧版）、不适合高并发低延迟查询。
## 2. 内部表（MANAGED_TABLE） vs 外部表（EXTERNAL_TABLE）
- 内部表：Hive 管理数据与元数据，DROP TABLE 时数据 + 元数据一起删。
- 外部表：只管理元数据，数据存于 HDFS 任意路径，DROP 只删元数据，数据保留。
生产环境几乎全部使用外部表，更安全、灵活。
## 3. 分区表（Partition） vs 分桶表（Bucket）
- 分区：按字段（如 dt、city）创建目录，用于裁剪查询，减少扫描数据量。
- 分桶：对字段哈希取模分成文件，用于优化 Join、抽样查询。
## 4. Hive 数据倾斜
- 表现：大部分 Task 很快跑完，个别 Task 卡住不动。
- 原因：某 Key 数据量远大于其他 Key。
- 常见场景：group by、join、count (distinct)。
- 解决方案：
- 参数调优：hive.groupby.skewindata=true
空值 / 异常值加盐打散
两阶段聚合：局部聚合 + 全局聚合
大表小表 Join 转为 MapJoin
## 5. Hive 数仓分层（生产标准）
- ODS：原始数据层，直接同步日志 / DB。
- DWD：明细数据层，清洗、脱敏、结构化。
- DWS：汇总数据层，轻度聚合，宽表。
- ADS：应用数据层，指标结果，供报表查询。
# 五、HBase 相关
## 1. HBase 数据模型
- RowKey：行键，唯一标识，索引核心。
- ColumnFamily：列族，必须预定义，物理存储在一起。
- Column：列，在列族下可动态新增。
- Version：版本，时间戳标识。
- Cell：{RowKey, CF, Column, Version} 唯一确定一个单元格。
## 2. HBase 架构
- HMaster：管理 DDL、Region 分配、负载均衡。
- RegionServer：负责数据读写，管理 Region。
- ZooKeeper：维护集群状态、Master 高可用、Region 寻址。
- Region：表的分段，按 RowKey 范围切分。
## 3. RowKey 设计原则
- 散列性：避免连续递增导致热点写（可加盐、反转、哈希）。
- 长度适中：不宜过长，影响索引效率。
- 业务查询靠前：最常用查询字段放前面。
- 唯一性：保证一行一个 RowKey。
## 4. HBase 与 Hive 区别
- HBase：NoSQL，面向随机读写、低延迟、高并发。
- Hive：数仓，面向离线批量分析、高延迟、SQL 友好。
- 可配合使用：Hive 做 ETL，HBase 供业务实时查询。
# 六、ZooKeeper 相关
## 1. 核心功能
- 分布式统一配置管理
- 分布式锁
- 集群节点上下线感知
Master 选举（HBase、Kafka 依赖）
## 2. ZNode 节点类型
- 持久节点：创建后一直存在。
- 临时节点：客户端断开自动删除。
- 顺序节点：自动追加自增序号。
- 临时顺序节点：常用于分布式锁与选举。
# 七、Flume & Sqoop
## 1. Flume 核心组件
- Source：采集源（如 Kafka、Taildir、NetCat）。
- Channel：缓冲通道（Memory Channel 快、File Channel 可靠）。
- Sink：输出目的地（HDFS、Kafka、HBase）。
- 可靠性保证：事务 + 断点续传。
## 2. Sqoop 作用
在关系型数据库（MySQL/Oracle）与 Hadoop（HDFS/Hive/HBase）之间批量数据传输。
import：DB → Hadoop
export：Hadoop → DB
支持增量导入、按主键分片、多 Map 并行。
# 八、典型大数据业务流程
- 离线数仓流程
日志 / 业务库 → Flume/Sqoop → HDFS（ODS） → Hive 清洗（DWD/DWS） → 指标计算（ADS） → Superset/BI 报表。
- 实时计算流程
日志 → Flume → Kafka → Flink/Spark Streaming → 实时计算 → HBase/ClickHouse → 实时大屏 / 监控。
