# Metrics Collector Documentation

## Table of Contents

1. [SessionMonitor (Oracle Session Metrics)](#sessionmonitor-oracle-session-metrics)
2. [OsStat (Oracle OS Statistics)](#osstat-oracle-os-statistics)
3. [AsmDiskGroup (Oracle ASM Disk Group Metrics)](#asmdiskgroup-oracle-asm-disk-group-metrics)
4. [InstanceViewer (Oracle Instance Health & Performance)](#instanceviewer-oracle-instance-health-performance)
   - [InstanceViewer Submetrics Overview](#instanceviewer-submetrics-overview)
5. [Explanation of Collected Metrics](#explanation-of-collected-metrics)
6. [How to Use Metrics in Datadog Dashboards](#how-to-use-metrics-in-datadog-dashboards)
7. [Enabling Metric Collection](#enabling-metric-collection)

---

## SessionMonitor (Oracle Session Metrics)

**Metric Group:** `Session`
**Metric Name:** `SessionMonitor`

**Metric Prefix:** `dbxplorer.oracle.database.session`

### Collected Metrics

The `SessionMonitor` collector gathers advanced Oracle session-level metrics, including:

| Metric Name                | Description                                      |
|---------------------------|--------------------------------------------------|
| SID, SERIAL#              | Session identifiers                              |
| USERNAME                  | Oracle user                                      |
| STATUS                    | Session status (ACTIVE/INACTIVE)                 |
| SESSION_TYPE              | Type of session (USER/BACKGROUND)                |
| SQL_ID, PREV_SQL_ID       | Current and previous SQL statement IDs           |
| PROGRAM, MODULE, ACTION   | Client program/module/action                      |
| CPU_USED                  | CPU time used by this session                    |
| DB_TIME                   | Total DB time for this session                   |
| SESSION_LOGICAL_READS     | Logical reads by session                         |
| PHYSICAL_READS/WRITES     | Physical I/O by session                          |
| PARSE_COUNT_TOTAL         | Total parses                                     |
| SORTS_MEMORY/DISK         | Sorts in memory/disk                             |
| TABLE_SCANS_LONG/SHORT    | Table scan counts                                |
| OPENED_CURSORS_CUM        | Opened cursors (cumulative)                      |
| PDB_NAME                  | Pluggable database name (if CDB)                 |
| INSTANCE_NAME, HOST_NAME  | Instance and host info                           |
| DB_UNIQUE_NAME, NAME      | Database unique and display name                 |
| COLLECTION_TIMESTAMP      | Timestamp of metric collection                   |

### Example Usage in Datadog Dashboards

- **Session Activity:**
  - Visualize active vs. inactive sessions using `dbxplorer.oracle.database.session.status`.
- **Top SQL by DB Time:**
  - Use `dbxplorer.oracle.database.session.db_time` grouped by `sql_id` to find the most resource-consuming SQL.
- **Session CPU Usage:**
  - Chart `dbxplorer.oracle.database.session.cpu_used` to monitor CPU-intensive sessions.
- **Session Metadata:**
  - Filter or group by `program`, `module`, or `action` for application-level insights.

**Tip:** Use tags like `cluster_name`, `instance_name`, or `host_name` for multi-instance environments.

---

## OsStat (Oracle OS Statistics)

**Metric Group:** `OS`
**Metric Name:** `OsStat`

**Metric Prefix:** `dbxplorer.oracle.database.osstat`

### Collected Metrics

| Metric Name                | Description                                      |
|---------------------------|--------------------------------------------------|
| USER_TIME_IN_SECONDS       | User CPU time (seconds)                          |
| BUSY_TIME_IN_SECONDS       | Busy CPU time (seconds)                          |
| IDLE_TIME_IN_SECONDS       | Idle CPU time (seconds)                          |
| PHYSICAL_MEMORY_BYTES      | Total physical memory                            |
| FREE_MEMORY_BYTES          | Free memory                                      |
| VM_IN_BYTES/VM_OUT_BYTES   | Virtual memory in/out                            |
| LOAD                       | System load                                      |
| SYS_TIME_IN_SECONDS        | System CPU time (seconds)                        |
| IOWAIT_TIME_IN_SECONDS     | I/O wait time (seconds)                          |
| NUM_CPUS                   | Number of CPUs                                   |
| COLLECTION_TIMESTAMP       | Timestamp of metric collection                   |

### Example Usage in Datadog Dashboards

- **CPU Utilization:**
  - Visualize `busy`, `idle`, and `user` time to monitor system load and identify bottlenecks.
  - **Note:** These metrics are cumulative counters (monotonically increasing). To get the rate (e.g., per second), use Datadog's `per_second()` function in your dashboard queries.
  - **Example:**
    - `per_second(avg:dbxplorer.oracle.database.osstat.busy_time_in_seconds{*} by {dbsys,cluster_name,host_name})`
    - `per_second(avg:dbxplorer.oracle.database.osstat.idle_time_in_seconds{*} by {dbsys,cluster_name,host_name})`
    - `per_second(avg:dbxplorer.oracle.database.osstat.user_time_in_seconds{*} by {dbsys,cluster_name,host_name})`
  - **CPU % Calculation:**
    - To estimate CPU utilization percentage:
      - `CPU % = 100 * per_second(avg:dbxplorer.oracle.database.osstat.busy_time_in_seconds{*} by {{grouping}}) / (per_second(avg:dbxplorer.oracle.database.osstat.busy_time_in_seconds{*} by {{grouping}}) + per_second(avg:dbxplorer.oracle.database.osstat.idle_time_in_seconds{*} by {{grouping}}))`
    - Replace `{{grouping}}` with your desired tags, e.g. `dbsys,cluster_name,host_name`.
    - In Datadog, use a formula widget to compute this ratio.
  - **Throughput:**
    - For throughput or activity rate, always use the `per_second()` function in Datadog to convert counters to per-second values.
    - Example: `per_second(avg:dbxplorer.oracle.database.osstat.busy_time_in_seconds{*} by {dbsys,cluster_name,host_name})`
  - **Tip:** Always use the `per_second()` function for these metrics to get meaningful, real-time values in your dashboards.

- **Memory Usage:**
  - Track `physical_memory_bytes` and `free_memory_bytes` for memory pressure.
- **System Load:**
  - Use `load` and `num_cpus` to correlate workload with available resources.

---

## AsmDiskGroup (Oracle ASM Disk Group Metrics)

**Metric Group:** `Space`
**Metric Name:** `AsmDiskGroup`

**Metric Prefix:** `dbxplorer.oracle.database.asmdiskgroup`

### Collected Metrics

The `AsmDiskGroup` collector gathers Oracle ASM disk group metrics, with special handling for redundancy types (EXTERNAL, NORMAL, HIGH, FLEX) and Intelligent Data Placement (IDP):

| Metric Name                | Description                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------|
| total_mb                  | Raw total MB in the disk group (not adjusted for redundancy)                                |
| free_mb                   | Raw free MB in the disk group (not adjusted for redundancy)                                 |
| usable_file_mb            | Usable MB for files, after all redundancy and overhead (always use for available space)     |
| hot_used_mb               | Raw MB used by 'hot' files (IDP feature, not adjusted for redundancy)                       |
| cold_used_mb              | Raw MB used by 'cold' files (IDP feature, not adjusted for redundancy)                      |
| required_mirror_free_mb   | Raw MB required to restore redundancy after a failure                                       |
| type                      | Redundancy type (EXTERNAL, NORMAL, HIGH, FLEX)                                              |
| state                     | Disk group state                                                                            |
| name                      | Disk group name                                                                             |
| collection_timestamp      | Timestamp of metric collection                                                              |

#### Redundancy Handling
- **EXTERNAL**: No mirroring, all space is usable.
- **NORMAL**: 2-way mirroring, usable space ≈ `total_mb / 2`.
- **HIGH**: 3-way mirroring, usable space ≈ `total_mb / 3`.
- **FLEX**: Usable space cannot be calculated from `total_mb`; always use `usable_file_mb`.

#### Hot/Cold Used MB
- `hot_used_mb` and `cold_used_mb` are raw values (not adjusted for redundancy).
- For a usable perspective, divide by the redundancy factor (2 for NORMAL, 3 for HIGH), but always prefer `usable_file_mb` for available space.

#### Example Table
| Metric         | Raw Value (MB) | Usable (MB, approx) | Explanation                                 |
|---------------|----------------|---------------------|---------------------------------------------|
| total_mb      | 574,000,000    | 191,333,333         | Theoretical max usable, not actual           |
| free_mb       | 85,000,000     | 28,333,333          | Usable free space for new files              |
| cold_used_mb  | 490,000,000    | 163,333,333         | Usable cold file data (if adjusted)          |
| usable_file_mb| 28,000,000     | 28,000,000          | Actual space available for new files         |

**Note:** Always use `usable_file_mb` for reporting available space. The other columns are raw and must be divided by the redundancy factor for a "usable" perspective.

### Raw vs. Redundancy-Adjusted Metrics

The following table clarifies which metrics from `AsmDiskGroup` are raw (direct from Oracle) and which are calculated/adjusted for redundancy:

| Metric Name                  | Raw Value? | Redundancy-Adjusted? | Notes                                                                 |
|-----------------------------|:----------:|:--------------------:|-----------------------------------------------------------------------|
| total_mb                     |    —       |         —            | Not collected directly; only bytes version is available                |
| free_mb                      |    —       |         —            | Not collected directly; only bytes version is available                |
| usable_file_mb               |   Yes      |        Yes           | Already adjusted for redundancy and overhead (use for available space) |
| hot_used_mb                  |   Yes      |         No           | Raw hot file usage (IDP feature)                                      |
| cold_used_mb                 |   Yes      |         No           | Raw cold file usage (IDP feature)                                     |
| required_mirror_free_mb      |   Yes      |         No           | Raw MB required to restore redundancy                                 |
| raw_total_bytes              |   Yes      |         No           | total_mb * 1024 * 1024; raw bytes, not MB                             |
| total_bytes                  |    No      |        Yes           | Calculated: total_mb in bytes, adjusted for redundancy                |
| raw_free_bytes               |   Yes      |         No           | free_mb * 1024 * 1024; raw bytes, not MB                              |
| free_bytes                   |    No      |        Yes           | Calculated: free_mb in bytes, adjusted for redundancy                 |
| raw_hot_used_bytes           |   Yes      |         No           | hot_used_mb in bytes                                                  |
| hot_used_bytes               |    No      |        Yes           | Calculated: hot_used_mb in bytes, adjusted for redundancy             |
| raw_cold_used_bytes          |   Yes      |         No           | cold_used_mb in bytes                                                 |
| cold_used_bytes              |    No      |        Yes           | Calculated: cold_used_mb in bytes, adjusted for redundancy            |
| raw_required_mirror_free_bytes|  Yes      |         No           | required_mirror_free_mb in bytes                                      |
| required_mirror_free_bytes   |    No      |        Yes           | Calculated: required_mirror_free_mb in bytes, adjusted for redundancy |
| usable_file_bytes            |   Yes      |        Yes           | Already adjusted for redundancy and overhead                          |

- **Raw**: Direct from Oracle, not adjusted for redundancy.
- **Redundancy-Adjusted**: Calculated in the query using the disk group type (EXTERNAL, NORMAL, HIGH) to reflect actual usable space.
- **Always use `usable_file_mb` or `usable_file_bytes` for available space reporting.**

- **Note:** The query does not collect `total_mb` or `free_mb` (raw MB) directly; only the byte-converted and redundancy-adjusted versions are available. For raw MB, divide `raw_total_bytes` or `raw_free_bytes` by 1024*1024.

### Example Usage in Datadog Dashboards
- **Disk Group Free Space:**
  - Visualize `dbxplorer.oracle.database.asmdiskgroup.usable_file_mb` to monitor available space.
- **Redundancy-Aware Usage:**
  - Use `usable_file_mb` for alerts and dashboards, not `free_mb` or `total_mb`.
- **Hot/Cold File Usage:**
  - Track `hot_used_mb` and `cold_used_mb` for IDP-enabled groups, but remember these are raw values.
- **Group/Filter:**
  - Group by `name`, `type`, or `state` to monitor specific disk groups or redundancy types.

**References:**
- [V$ASM_DISKGROUP](https://docs.oracle.com/en/database/oracle/oracle-database/19/refrn/V-ASM_DISKGROUP.html)
- [Intelligent Data Placement](https://docs.oracle.com/en/database/oracle/oracle-database/19/ostmg/intelligent-data-placement.html)

---

## InstanceViewer (Oracle Instance Health & Performance)

**Metric Group:** `Health`  
**Metric Name:** `InstanceViewer`

### InstanceViewer Submetrics Overview

The following table summarizes all submetrics collected by the `InstanceViewer` metric group. Each submetric provides a focused view of Oracle instance health and performance. Use this table to quickly identify available submetrics, their main metrics, and the Oracle view/table they are sourced from.

| Submetric Name   | Main Metrics (examples)                                 | Oracle View/Table(s)                |
|------------------|--------------------------------------------------------|-------------------------------------|
| physical_read    | physical_read_total_bytes, physical_read_io_requests   | v$sysstat                           |
| physical_write   | physical_write_total_bytes, physical_write_io_requests | v$sysstat                           |
| sessions         | active_session_count, total_session_count              | v$session, v$containers             |
| sga              | buffer_cache_size, total_sga_size                      | v$sgainfo                           |
| redo             | redo_generated_per_sec, redo_writes_per_sec            | v$con_sysmetric, v$sysmetric        |
| dbblock          | db_block_gets_per_sec, db_block_changes                | v$con_sysmetric                     |
| user             | user_commits, user_rollbacks                           | v$sysstat                           |
| dedicated_server | dedicated_server_proc_count                            | v$session                           |
| hardparse        | hard_parse_count_per_sec, parse_failures_per_sec       | v$con_sysmetric                     |
| execute          | sql_cpu_time, sql_executions                           | v$sql (or similar)                  |
| dbsystem         | cpu_usage, memory_usage                                | v$sysmetric (or similar)            |
| read_write       | read_throughput, write_throughput                      | v$sysstat (or similar)              |
| sqlnet           | sqlnet_roundtrips_per_sec, sqlnet_bytes_sent_per_sec   | v$sysstat                           |
| system           | cpu_usage, memory_usage                                | v$sysmetric (or similar)            |
| client           | client_count                                           | (see code, typically v$session)     |
| pq_slave         | pq_slave_count                                         | (see code, typically v$px_session)  |
| redologs         | redolog_status, redolog_switch_count                   | (see code, typically v$log)         |
| db_size          | db_size_total, db_size_used                            | (see code, typically dba_data_files)|
| job_server       | job_server_count                                       | (see code, typically dba_jobs)      |
| redo_blocks      | redo_blocks_written                                    | (see code, typically v$log)         |
| host             | host_cpu_utilization_pct, database_cpu_time_ratio, host_cpu_usage_per_sec | v$sysmetric |

**Tip:** For detailed metric names, descriptions, and dashboard usage, see the dedicated section for each submetric below.

#### physical_read (Physical Read Statistics)
- **Submetric name:** `physical_read`
- **Oracle View/Table:** `v$sysstat`
- **Metrics Collected:**
  - `physical_read_total_io_requests`: Total number of physical read I/O requests.
  - `physical_read_total_multi_block_requests`: Total number of multi-block physical read requests.
  - `physical_read_requests_optimized`: Number of optimized physical read requests.
  - `physical_read_total_bytes_optimized`: Total bytes read by optimized physical reads.
  - `physical_read_total_bytes`: Total bytes read from disk.
  - `physical_read_io_requests`: Number of physical read I/O requests.
  - `physical_read_bytes`: Bytes read by physical read operations.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.physical_read.physical_read_total_bytes-value{*} by {instance_name,host_name}
```
This query shows the average bytes read from disk per instance and host.

#### physical_write (Physical Write Statistics)
- **Submetric name:** `physical_write`
- **Oracle View/Table:** `v$sysstat`
- **Metrics Collected:**
  - `physical_write_requests_optimized`: Optimized write requests (if available).
  - `physical_write_total_bytes_optimized`: Optimized write bytes (if available).
  - `physical_write_total_io_requests`: Total number of physical write I/O requests.
  - `physical_write_total_multi_block_requests`: Multi-block write requests.
  - `physical_write_total_bytes`: Total bytes written to disk.
  - `physical_write_snap_io_requests_new_allocations`: Snap I/O requests for new allocations.
  - `physical_write_io_requests`: Number of physical write I/O requests (may overlap with total).
  - `physical_write_bytes`: Bytes written by physical write operations.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.physical_write.physical_write_total_bytes-value{*} by {instance_name,host_name}
```
This query shows the average bytes written to disk per instance and host.

#### sessions (Session and Connection Statistics)
- **Submetric name:** `sessions`
- **Oracle View/Table:** `v$session`, `v$containers`
- **Metrics Collected:**
  - `active_session_count`: Number of active sessions.
  - `inactive_session_count`: Number of inactive sessions.
  - `total_session_count`: Total number of sessions.
  - `blocked_session_count`: Number of blocked sessions.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.sessions.active_session_count-value{*} by {instance_name,host_name}
```
This query shows the number of active sessions per instance and host.

#### sga (SGA Memory Usage)
- **Submetric name:** `sga`
- **Oracle View/Table:** `v$sgainfo`
- **Metrics Collected:**
  - `buffer_cache_size`: Size of the buffer cache in bytes.
  - `data_transfer_cache_size`: Size of the data transfer cache in bytes.
  - `fixed_sga_size`: Size of the fixed SGA in bytes.
  - `free_sga_memory_available`: Free SGA memory available in bytes.
  - `granule_size`: SGA granule size in bytes.
  - `java_pool_size`: Size of the Java pool in bytes.
  - `large_pool_size`: Size of the large pool in bytes.
  - `log_buffer_size`: Size of the log buffer in bytes.
  - `shared_io_pool_size`: Size of the shared I/O pool in bytes.
  - `shared_pool_size`: Size of the shared pool in bytes.
  - `streams_pool_size`: Size of the streams pool in bytes.
  - `total_sga_size`: Total SGA size in bytes.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.sga.buffer_cache_size-value{*} by {instance_name,host_name}
```
This query shows the buffer cache size per instance and host.

#### redo (Redo Log Activity)
- **Submetric name:** `redo`
- **Oracle View/Table:** `v$con_sysmetric`, `v$sysmetric`
- **Metrics Collected:**
  - `redo_generated_per_sec`: Redo bytes generated per second.
  - `redo_writes_per_sec`: Redo writes per second.
  - `redo_entries_per_sec`: Redo entries per second.
  - `redo_size`: Total redo size in bytes.
  - `redo_writes`: Total redo writes.
  - `redo_entries`: Total redo entries.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.redo.redo_generated_per_sec-value{*} by {instance_name,host_name}
```
This query shows the redo bytes generated per second per instance and host.

#### dbblock (Database Block Activity)
- **Submetric name:** `dbblock`
- **Oracle View/Table:** `v$con_sysmetric`
- **Metrics Collected:**
  - `db_block_changes_per_sec`: Number of DB block changes per second.
  - `db_block_gets_per_sec`: Number of DB block gets per second.
  - `db_block_changes`: Total DB block changes.
  - `db_block_gets`: Total DB block gets.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.dbblock.db_block_gets_per_sec-value{*} by {instance_name,host_name}
```
This query shows the DB block gets per second per instance and host.

#### user (User-Level Activity)
- **Submetric name:** `user`
- **Oracle View/Table:** `v$sysstat`
- **Metrics Collected:**
  - `user_commits`: Number of user commits.
  - `user_rollbacks`: Number of user rollbacks.
  - `user_calls`: Number of user calls.
  - `user_logons_cumulative`: Cumulative user logons.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.user.user_commits-value{*} by {instance_name,host_name}
```
This query shows the number of user commits per instance and host.

#### dedicated_server (Dedicated Server Session Counts)
- **Submetric name:** `dedicated_server`
- **Oracle View/Table:** `v$session`
- **Metrics Collected:**
  - `dedicated_server_proc_count`: Number of dedicated server sessions.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.dedicated_server.dedicated_server_proc_count-value{*} by {instance_name,host_name}
```
This query shows the number of dedicated server sessions per instance and host.

#### hardparse (Hard Parse Statistics)
- **Submetric name:** `hardparse`
- **Oracle View/Table:** `v$con_sysmetric`
- **Metrics Collected:**
  - `hard_parse_count_per_sec`: Number of hard parses per second.
  - `parse_failures_per_sec`: Number of parse failures per second.
  - `soft_parse_count_per_sec`: Number of soft parses per second.
  - `total_parse_count_per_sec`: Total number of parses per second.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.hardparse.hard_parse_count_per_sec-value{*} by {instance_name,host_name}
```
This query shows the number of hard parses per second per instance and host.

#### execute (SQL Execution Statistics)
- **Submetric name:** `execute`
- **Oracle View/Table:** `v$sql` (or similar, check actual query)
- **Metrics Collected:**
  - `sql_cpu_time`: SQL CPU time in microseconds.
  - `sql_elapsed_time`: SQL elapsed time in microseconds.
  - `sql_disk_reads`: SQL disk reads.
  - `sql_buffer_gets`: SQL buffer gets.
  - `sql_executions`: SQL executions.

**Example Datadog Dashboard Query:**
```
top(avg:dbxplorer.oracle.database.health.instanceviewer.execute.sql_cpu_time-value{*} by {sql_id}, 10, 'mean', 'desc')
```
This query shows the top 10 SQL statements by average CPU time.

#### dbsystem (System-Level Metrics)
- **Submetric name:** `dbsystem`
- **Oracle View/Table:** `v$sysmetric` (or similar, check actual query)
- **Metrics Collected:**
  - `cpu_usage`: CPU usage percentage.
  - `memory_usage`: Memory usage percentage.
  - `io_usage`: I/O usage percentage.
  - `network_usage`: Network usage percentage.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.dbsystem.cpu_usage-value{*} by {instance_name,host_name}
```
This query shows the CPU usage percentage per instance and host.

#### read_write (Read/Write Throughput and Latency)
- **Submetric name:** `read_write`
- **Oracle View/Table:** `v$sysstat` (or similar, check actual query)
- **Metrics Collected:**
  - `read_throughput`: Read throughput in bytes per second.
  - `write_throughput`: Write throughput in bytes per second.
  - `read_latency`: Read latency in milliseconds.
  - `write_latency`: Write latency in milliseconds.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.read_write.read_throughput-value{*} by {instance_name,host_name}
```
This query shows the read throughput in bytes per second per instance and host.

#### sqlnet (SQL*Net Network Metrics)
- **Submetric name:** `sqlnet`
- **Oracle View/Table:** `v$sysstat`
- **Metrics Collected:**
  - `sqlnet_roundtrips_per_sec`: SQL*Net roundtrips per second.
  - `sqlnet_bytes_sent_per_sec`: SQL*Net bytes sent per second.
  - `sqlnet_bytes_received_per_sec`: SQL*Net bytes received per second.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.sqlnet.sqlnet_roundtrips_per_sec-value{*} by {instance_name,host_name}
```
This query shows the SQL*Net roundtrips per second per instance and host.

#### system (System Resource Metrics)
- **Metrics Collected:**
  - `cpu_usage`: CPU usage percentage.
  - `memory_usage`: Memory usage percentage.
  - `io_usage`: I/O usage percentage.
  - `network_usage`: Network usage percentage.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.system.cpu_usage-value{*} by {instance_name,host_name}
```
This query shows the CPU usage percentage per instance and host.

#### client (Client Connection Counts)
- **Metrics Collected:**
  - `client_count`: Number of distinct client connections.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.client_count{*} by {instance_name,host_name}
```
This query shows the number of client connections per instance and host.

#### pq_slave (Parallel Query Slave Process Counts)
- **Metrics Collected:**
  - `pq_slave_count`: Number of parallel query slave processes.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.pq_slave.pq_slave_count-value{*} by {instance_name,host_name}
```
This query shows the number of parallel query slave processes per instance and host.

#### redologs (Redo Log File Status)
- **Metrics Collected:**
  - `redolog_status`: Status of redo log files.
  - `redolog_switch_count`: Number of redo log switches.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.redologs.redolog_switch_count-value{*} by {instance_name,host_name}
```
This query shows the number of redo log switches per instance and host.

#### db_size (Database Size Metrics)
- **Metrics Collected:**
  - `db_size_total`: Total database size in bytes.
  - `db_size_used`: Used database size in bytes.
  - `db_size_free`: Free database size in bytes.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.db_size.db_size_used-value{*} by {instance_name,host_name}
```
This query shows the used database size in bytes per instance and host.

#### job_server (Job Server Process Counts)
- **Metrics Collected:**
  - `job_server_count`: Number of job server processes.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.job_server.job_server_count-value{*} by {instance_name,host_name}
```
This query shows the number of job server processes per instance and host.

#### redo_blocks (Redo Blocks Written)
- **Metrics Collected:**
  - `redo_blocks_written`: Number of redo blocks written.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.redo_blocks.redo_blocks_written-value{*} by {instance_name,host_name}
```
This query shows the number of redo blocks written per instance and host.

#### host (Host CPU Utilization)
- **Submetric name:** `host`
- **Oracle View/Table:** `v$con_sysmetric`, `v$sysmetric`
- **Metrics Collected:**
  - `host_cpu_utilization_pct`: Percentage of total host CPU currently in use. This reflects the overall CPU load on the server hosting the Oracle instance, including all processes (not just Oracle). High values may indicate system-wide CPU contention.
  - `database_cpu_time_ratio`: Ratio of CPU time consumed by the Oracle database process compared to total host CPU time. This helps you understand how much of the host's CPU is being used by Oracle versus other processes. A high ratio means Oracle is the main CPU consumer.
  - `host_cpu_usage_per_sec`: Number of CPU seconds used per second on the host. This is a rate metric showing how much CPU time is being consumed each second, useful for tracking spikes or trends in CPU usage.

**Example Datadog Dashboard Query:**
```
avg:dbxplorer.oracle.database.health.instanceviewer.host.host_cpu_utilization_pct{*} by {instance_name,host_name}
```
This query shows the average host CPU utilization percentage per Oracle instance and host.

**Metric Explanations:**
- Use `host_cpu_utilization_pct` to monitor overall server CPU pressure. If this value is consistently high, consider scaling up hardware or tuning workloads.
- `database_cpu_time_ratio` helps you distinguish between Oracle-driven and non-Oracle-driven CPU usage. If this ratio is low but `host_cpu_utilization_pct` is high, other applications may be causing CPU contention.
- `host_cpu_usage_per_sec` is useful for visualizing CPU consumption trends and correlating with database activity spikes.

**Dashboard Tips:**
- Plot `host_cpu_utilization_pct` alongside Oracle-specific CPU metrics to quickly spot whether database or external processes are causing CPU bottlenecks.
- Use these metrics to set up alerts for high CPU usage, both at the host and Oracle process level.
- Group by `instance_name` and `host_name` to identify which database instances are most affected by host CPU load.

---

## Explanation of Collected Metrics

This section provides user-facing explanations for each collected metric, especially for the InstanceViewer "host" submetric, and general guidance for interpreting metrics in Datadog dashboards.

---

### SessionMonitor (Oracle Session Metrics)
- **SID, SERIAL#**: Unique identifiers for each Oracle session.
- **USERNAME**: The Oracle user associated with the session.
- **STATUS**: Indicates if the session is currently active or inactive.
- **SESSION_TYPE**: Distinguishes between user and background sessions.
- **SQL_ID, PREV_SQL_ID**: Identifiers for the current and previous SQL statements executed in the session.
- **PROGRAM, MODULE, ACTION**: Client application details for the session, useful for tracing workload sources.
- **CPU_USED**: Total CPU time consumed by the session.
- **DB_TIME**: Total database time spent by the session, including CPU and wait time.
- **SESSION_LOGICAL_READS**: Number of logical (buffer cache) reads performed by the session.
- **PHYSICAL_READS/WRITES**: Number of physical disk reads/writes by the session.
- **PARSE_COUNT_TOTAL**: Total number of SQL parses performed by the session.
- **SORTS_MEMORY/DISK**: Number of sorts performed in memory and on disk.
- **TABLE_SCANS_LONG/SHORT**: Counts of long and short table scans.
- **OPENED_CURSORS_CUM**: Cumulative number of opened cursors.
- **PDB_NAME**: Name of the pluggable database (if applicable).
- **INSTANCE_NAME, HOST_NAME**: Identifies the Oracle instance and host machine.
- **DB_UNIQUE_NAME, NAME**: Unique and display names for the database.
- **COLLECTION_TIMESTAMP**: When the metric was collected.

---

### OsStat (Oracle OS Statistics)
- **USER_TIME_IN_SECONDS**: Time spent executing user processes.
- **BUSY_TIME_IN_SECONDS**: Total time CPU was busy (user + system).
- **IDLE_TIME_IN_SECONDS**: Time CPU was idle.
- **PHYSICAL_MEMORY_BYTES**: Total physical memory available on the host.
- **FREE_MEMORY_BYTES**: Amount of free memory available.
- **VM_IN_BYTES/VM_OUT_BYTES**: Virtual memory paging in/out.
- **LOAD**: System load average.
- **SYS_TIME_IN_SECONDS**: Time spent executing system (kernel) processes.
- **IOWAIT_TIME_IN_SECONDS**: Time CPU spent waiting for I/O.
- **NUM_CPUS**: Number of CPU cores.
- **COLLECTION_TIMESTAMP**: When the metric was collected.

---

### AsmDiskGroup (Oracle ASM Disk Group Metrics)
- **total_mb, free_mb**: Raw total and free space in the disk group (not adjusted for redundancy).
- **usable_file_mb**: Usable space for files, after accounting for redundancy and overhead (recommended for monitoring).
- **hot_used_mb, cold_used_mb**: Space used by 'hot' and 'cold' files (Intelligent Data Placement feature).
- **required_mirror_free_mb**: Space required to restore redundancy after a failure.
- **type**: Redundancy type (EXTERNAL, NORMAL, HIGH, FLEX).
- **state**: Current state of the disk group.
- **name**: Name of the disk group.
- **collection_timestamp**: When the metric was collected.

---

### InstanceViewer (Oracle Instance Health & Performance)
Each submetric provides a focused view of instance health. For the `host` submetric:

#### Host Submetric (InstanceViewer)
- **host_cpu_utilization_pct**: Percentage of total host CPU in use. Reflects overall CPU load on the server hosting the Oracle instance, including all processes (not just Oracle). High values may indicate system-wide CPU contention.
- **database_cpu_time_ratio**: Proportion of host CPU time consumed by the Oracle database. Helps you understand how much of the host's CPU is being used by Oracle versus other processes. A high ratio means Oracle is the main CPU consumer.
- **host_cpu_usage_per_sec**: Host CPU usage rate per second. Shows how much CPU time is being consumed each second, useful for tracking spikes or trends in CPU usage.

**Interpretation Tips:**
- Use `host_cpu_utilization_pct` to monitor overall server CPU pressure. If this value is consistently high, consider scaling up hardware or tuning workloads.
- `database_cpu_time_ratio` helps distinguish between Oracle-driven and non-Oracle-driven CPU usage. If this ratio is low but `host_cpu_utilization_pct` is high, other applications may be causing CPU contention.
- `host_cpu_usage_per_sec` is useful for visualizing CPU consumption trends and correlating with database activity spikes.

**Dashboard Tips:**
- Plot `host_cpu_utilization_pct` alongside Oracle-specific CPU metrics to quickly spot whether database or external processes are causing CPU bottlenecks.
- Use these metrics to set up alerts for high CPU usage, both at the host and Oracle process level.
- Group by `instance_name` and `host_name` to identify which database instances are most affected by host CPU load.

---

These explanations help users understand what each metric means, how to use them in dashboards, and how to interpret their values for effective Oracle monitoring.

---

## How to Use Metrics in Datadog Dashboards

1. **Add a Query:**
   - Use the metric prefix (e.g., `dbxplorer.oracle.database.session.db_time`) in your Datadog dashboard widgets.
2. **Group/Filter:**
   - Group by tags such as `sql_id`, `username`, `instance_name`, or `host_name` for detailed breakdowns.
3. **Visualize Trends:**
   - Use timeseries, toplist, or heatmap widgets to analyze trends and outliers.
4. **Correlate Metrics:**
   - Combine session and OS metrics to correlate database workload with system resource usage.

**Example Datadog Query:**
```
avg:dbxplorer.oracle.database.session.cpu_used{databaseIdentifier:prod-db,instance_name:orcl1}
```

**Tip:** Refer to the provided dashboard JSONs in `assetes/dashboards/InstanceViewer/` for ready-to-use visualizations.

---

## Enabling Metric Collection

To enable metric collection for Oracle metrics in the dbxplorer agent, configure the following YAML files in your repository:

1. **Inventory Configuration**
   - Path: `inventory/oracle/oracle_instance.yml`
   - This file defines which Oracle entities (e.g., databases, instances) are monitored and their connection details.
   - Example:
     ```yaml
     # inventory/oracle/oracle_instance.yml
     - entityName: ext3adm1_dbicdb
       enabled: true
       type: oracle
       user: c##dbxplorer
       password: "<SECRET>"
       role: "normal"
       url: "jdbc:oracle:thin:@(DESCRIPTION=(SOURCE_ROUTE=yes)(ADDRESS=(PROTOCOL=TCP)(HOST=ext3adm1.itunified.io)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=dbicdb)))"
       tags:
         dbsys: "ext3"
         entityType: "oracle_instance"
         environment: "development"
         application: "dbi"
         service: "oracle"
     ```
   - Set `enabled: true` to activate monitoring for this entity.
   - The `entityName` value (e.g., `ext3adm1_dbicdb`) must match the name referenced in your monitoring configuration.

2. **Metric Collector Configuration**
   - Path: `monitoring/metrics/<entity_name>.yml`
   - This file controls which metric groups and collectors are enabled, their intervals, and which entities they apply to.
   - Example:
     ```yaml
     - metricGroup: Availability
       metricName: [Availability]
       intervalSeconds: 60
       enabled: false
       entityName: [ext3adm1_dbicdb]

     - metricGroup: Session
       metricName: [SessionMonitor]
       intervalSeconds: 30
       enabled: true
       entityName: [ext3adm1_dbicdb]

     - metricGroup: Os
       metricName: [OsStat]
       intervalSeconds: 30
       enabled: true
       entityName: [ext3adm1_dbicdb]

     - metricGroup: Health
       metricName: [InstanceViewer]
       intervalSeconds: 60
       enabled: true
       entityName: [ext3adm1_dbicdb]
     ```
   - Set `enabled: true` for each metric group/collector you want to activate for the entity.
   - Adjust `intervalSeconds` as needed for your monitoring requirements.

3. **Apply and Reload**
   - After editing these files, commit and push your changes to the repository if required by your deployment process.
   - The dbxplorer agent will automatically pick up changes or may require a restart depending on your setup.

4. **Verification**
   - Check the agent logs (`dbxagent.log`) for confirmation that the correct entities and metric collectors are active.
   - In Datadog, search for metrics with the relevant prefixes (e.g., `dbxplorer.oracle.database.session.*`) to confirm data is being sent.

**Tips:**
- Only enable the metric collectors you need for each entity to minimize overhead.
- Use the provided YAML templates as a reference for available options and structure.
- For more details, see the comments in the YAML files or refer to the project documentation.

---
