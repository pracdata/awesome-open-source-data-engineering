# Awesome Open Source Data Engineering [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)
A curated list of open source tools used in analytical stacks and data engineering ecosystem 
![Open Source Data Engineering Landscape 2024](https://github.com/pracdata/awesome-open-source-data-engineering/assets/2711465/2a59a1a3-2f82-4e78-939e-2f9228b4892f)
For more information about the above compiled landscape for 2024, please read the published blog post on [Substack](https://open.substack.com/pub/practicaldataengineering/p/open-source-data-engineering-landscape?r=23jwn&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true) or [Medium](https://alirezasadeghi1.medium.com/open-source-data-engineering-landscape-2024-8a56d23b7fdb)

## Table of contents
- [Storage Systems](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#storage-systems)
- [Data Lake Platform](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#data-lake-platform)
- [Data Integration](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#data-integration)
- [Data Processing & Computation](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#data-processing-and-computation)
- [Workflow Management & DataOps](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#workflow-management--dataops)
- [Data Infrastructure](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#data-infrastructure)
- [Metadata Management](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#metadata-management)
- [Analytics & Visualisation](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#analytics--visualisation)
- [ML/AI Platform](https://github.com/pracdata/awesome-open-source-data-engineering?tab=readme-ov-file#mlai-platform)

## STORAGE SYSTEMS

### Relational DBMS
- [PostgreSQL](https://github.com/postgres/postgres) - Advanced object-relational database management system
- [MySQL](https://github.com/mysql/mysql-server) - One of the most popular open Source Databases
- [MariaDB](https://github.com/MariaDB/server) - A popular MySQL server fork
- [Supabase](https://github.com/supabase/supabase) - An open source Firebase alternative
- [SQlite](https://github.com/sqlite/sqlite) - Most popular embedded database engine

### Distributed SQL DBMS
- [Citus](https://github.com/citusdata/citus) - A popular distributed PostgreSQL as an extension
- [CockroachDB](https://github.com/cockroachdb/cockroach) - A cloud-native distributed SQL database
- [YugabyteDB](https://github.com/yugabyte/yugabyte-db) - A cloud-native distributed SQL database
- [TiDB](https://github.com/pingcap/tidb) - A cloud-native, distributed, MySQL-Compatible database
- [OceanBase](https://github.com/oceanbase/oceanbase) - A scalable distributed relational database
- [ShardingSphere](https://github.com/apache/shardingsphere) - A Distributed SQL transaction & query engine
- [Neon](https://github.com/neondatabase/neon) - A serverless open-source alternative to AWS Aurora Postgres

### Cache Store
- [Redis](https://github.com/redis/redis) - A popular key-value based cache store
- [Memcached](https://github.com/memcached/memcached) - A high performance multithreadedkey-value cache store
- [Dragonfly](https://github.com/dragonflydb/dragonfly) - A modern cache store compatible with Redis and Memcached APIs

### In-memory SQL Database
- [Apache Ignite](https://github.com/apache/ignite) - A distributed, ACID-compliant in-memory DBMS 
- [ReadySet](https://github.com/readysettech/readyset) - A MySQL and Postgres wire-compatible caching layer
- [VoltDB](https://github.com/voltdb/voltdb/) - A distributed, horizontally-scalable, ACID-compliant database 

### Document Store
- [MongoDB](https://github.com/mongodb/mongo) - A cross-platform, document-oriented NoSQL database
- [RavenDB](https://github.com/ravendb/ravendb) - An ACID NoSQL document database
- [RethinkDB](https://github.com/rethinkdb/rethinkdb) - A distributed document-oriented database for real-time applications
- [CouchDB](https://github.com/apache/couchdb) - A Scalable document-oriented NoSQL database
- [Couchbase](https://github.com/couchbase) - A modern cloud-native NoSQL distributed database
- [FerretDB](https://github.com/FerretDB/FerretDB) - A truly Open Source MongoDB alternative!

### NoSQL Multi-model
- [OrientDB](https://github.com/orientechnologies/orientdb) - A Multi-model DBMS supporting Graph, Document, Reactive, Full-Text and Geospatial models
- [ArrangoDB](https://github.com/arangodb/arangodb) - A  Multi-model database with flexible data models for documents, graphs, and key-values
- [SurrealDB](https://github.com/surrealdb/surrealdb) - A scalable, distributed, collaborative, document-graph database
- [EdgeDB](https://github.com/edgedb/edgedb) - A graph-relational database with declarative schema

### Graph Database
- [Neo4j](https://github.com/neo4j/neo4j) - A high performance leading graph database
- [JunasGraph](https://github.com/JanusGraph/janusgraph) - A highly scalable distributed graph database
- [HugeGraph](https://github.com/apache/incubator-hugegraph) - A fast-speed and highly-scalable graph database
- [NebulaGraph](https://github.com/vesoft-inc/nebula) - A distributed, horizontal scalability, fast open-source graph database
- [Cayley](https://github.com/cayleygraph/cayley) - Inspired by the graph database behind Google's Knowledge Graph
- [Dgraph](https://github.com/dgraph-io/dgraph) -  A horizontally scalable and distributed GraphQL database with a graph backend

### Distributed Key-value Store
- [Riak](https://github.com/basho/riak) - A decentralized key-value datastore from Basho Technologies
- [FoundationDB](https://github.com/apple/foundationdb) - A distributed, transactional key-value store from Apple
- [etcd](https://github.com/etcd-io/etcd) - A distributed reliable key-value store written in Go
- [TiKV](https://github.com/tikv/tikv) - A distributed transactional key-value database, originally created to complement TiDB
- [Immudb](https://github.com/codenotary/immudb) - A database with built-in cryptographic proof and verification

### Wide-column Key-value Store
- [Apache Cassandra](https://github.com/apache/cassandra) - A highly-scalable LSM-Tree based partitioned row store
- [Apache Hbase](https://github.com/apache/hbase) - A distributed wide column-oriented store modeled after Google' Bigtable
- [Scylla](https://github.com/scylladb/scylladb) - LSM-Tree based wide-column API-compatible with Apache Cassandra and Amazon DynamoDB
- [Apache Accumulo]() - A distributed key-value store with scalable data storage and retrieval, on top of Hadoop

### Embedded Key-value Store
- [LevelDB](https://github.com/google/leveldb) - A fast key-value storage library written at Google
- [RocksDB](https://github.com/facebook/rocksdb) - An embeddable, persistent key-value store developed by Meta (Facebook)
- [MyRocks](https://github.com/facebook/mysql-5.6) - A RocksDB storage engine for MySQL
- [BadgerDB](https://github.com/dgraph-io/badger) - An embeddable, fast key-value database written in pure Go

### Search Engine
- [Apache Solr](https://github.com/apache/solr) - A fast distributed search database built on Apache Lucene
- [Elastic Search](https://github.com/elastic/elasticsearch) - A distributed, RESTful search engine optimized for speed
- [Sphinx](https://github.com/sphinxsearch/sphinx) -  A fulltext search engine with high speed of indexation
- [Meilisearch](https://github.com/meilisearch/meilisearch) - A fast search API with great integration support
- [OpenSearch](https://github.com/opensearch-project/OpenSearch) - A community-driven, open source fork of Elasticsearch and Kibana
- [Quickwit](https://github.com/quickwit-oss/quickwit) - A fast cloud-native search engine for observability data

### Streaming Database
- [RasingWave](https://github.com/risingwavelabs/risingwave) - A scalable Postgres for stream processing, analytics, and management
- [Materialize](https://github.com/MaterializeInc/materialize) - A real-time data warehouse purpose-built for operational workloads
- [EventStoreDB](https://github.com/EventStore/EventStore) - An event-native database designed for event sourcing and event-driven architectures
- [KsqlDB](https://github.com/confluentinc/ksql) - A database for building stream processing applications on top of Apache Kafka

### Time-Series Database
- [Influxdb](https://github.com/influxdata/influxdb) - A scalable datastore for metrics, events, and real-time analytics
- [TimeScaleDB](https://github.com/timescale/timescaledb) - A fast ingest time-series SQL database packaged as a PostgreSQL extension
- [Apache IoTDB](https://github.com/apache/iotdb) - An Internet of Things database with seamless integration with the Hadoop and Spark ecology
- [Netflix Atlas](https://github.com/Netflix/atlas) - An n-memory dimensional time series database developed and open sourced by Netflix
- [QuestDB](https://github.com/questdb/questdb) - A time-series database for fast ingest and SQL queries
- [TDEngine](https://github.com/taosdata/TDengine) - A high-performance, cloud native time-series database optimized for Internet of Things (IoT)
- [KairosDB](https://github.com/kairosdb/kairosdb) - A scalable time series database written in Java

### Columnar OLAP Database
- [Apache Kudu](https://github.com/apache/kudu) -  A column-oriented data store for the Apache Hadoop ecosystem
- [Greeenplum](https://github.com/greenplum-db/gpdb) -  A column-oriented massively parallel PostgreSQL for analytics
- [MonetDB](https://github.com/MonetDB/MonetDB) - A high-performance columnar database originally developed by the CWI database research group
- [DuckDB](https://github.com/duckdb/duckdb) - An in-process SQL OLAP Database Management System
- [Databend](https://github.com/datafuselabs/databend) - An lastic, workload-aware cloud-native data warehouse built in Rust
- [ByConity](https://github.com/ByConity/ByConity) - A cloud-native data warehouse forked from ClickHouse
- [hydra](https://github.com/hydradatabase/hydra) - A fast column-oriented Postgres extension

### Real-time OLAP Engine
- [ClickHouse](https://github.com/ClickHouse/ClickHouse) - A real-time column-oriented database originally developed at Yandex
- [Apache Pinot](https://github.com/apache/pinot) - A a real-time distributed OLAP datastore open sourced by LinkedIn
- [Apache Druid](https://github.com/apache/druid) - A high performance real-time OLAP engine developed and open sourced by Metamarkets
- [Apache Kylin](https://github.com/apache/kylin) - A distributed OLAP engine designed to provide multi-dimensional analysis on Hadoop
- [Apache Doris](https://github.com/apache/doris) - A high-performance and real-time analytical database based on MPP architecture
- [StarRocks](https://github.com/StarRocks/StarRocks) -  A sub-second OLAP database supporting multi-dimensional analytics (Linux Foundation project)


## DATA LAKE PLATFORM

### Distributed File System
- [Apache Hadoop HDFS](https://github.com/apache/hadoop) - A highly scalable distributed block-based file system 
- [GlusterFS](https://github.com/gluster/glusterfs) - A scalable distributed storage that can scale to several petabytes
- [JuiceFS](https://github.com/juicedata/juicefs) - A distributed POSIX file system built on top of Redis and S3
- [Lustre](https://github.com/lustre) - A distributed parallel file system purpose-built to provide global POSIX-compliant namespace

### Distributed Object Store
- [Apache Ozone](https://github.com/apache/ozone) - A scalable, redundant, and distributed object store for Apache Hadoop 
- [Ceph](https://github.com/ceph/ceph) - A distributed object, block, and file storage platform
- [Minio](https://github.com/minio/minio) - A high performance object storage being API compatible with Amazon S3 

### Serialisation Framework
- [Apache Parquet](https://github.com/apache/parquet-format) - An efficient columnar binary storage format that supports nested data
- [Apache Avro](https://github.com/apache/avro) - An efficient and fast row-based binary serialisation framework
- [Apache ORC](https://github.com/apache/orc) - A self-describing type-aware columnar file format designed for Hadoop 

### Open Table Format
- [Apache Hudi](https://github.com/apache/hudi) - An open table format desined to support incremental data ingestion on cloud and Hadoop
- [Apache Iceberg](https://github.com/apache/iceberg) -  A high-performance table format for large analytic tables developed at Netflix
- [Delta Lake](https://github.com/delta-io/delta) - A storage framework for building Lakehouse architecture developed by Databricks
- [Apache Paimon](https://github.com/apache/incubator-paimon) - An Apache inclubating project to support streaming high-speed data ingestion
- [OneTable](https://github.com/onetable-io/onetable) - A unified framework supporting interoperability across multiple open-source table formats


## DATA INTEGRATION

### Data Integration Platform
- [Airbyte](https://github.com/airbytehq/airbyte) - A data integration platform for ETL / ELT data pipelines with wide range of connectors 
- [Apache Nifi](https://github.com/apache/nifi) - A reliable, scalable low-code data integration platform with good enterprise support
- [Apache Camel](https://github.com/apache/camel) - An embeddable integration framework supporting many enterprise integration patterns
- [Apache Gobblin](https://github.com/apache/gobblin) - A distributed data integration framework built by LinkedIn supporting both streaming and batch data
- [Apache Inlong](https://github.com/apache/Inlong) - An integration framework for supporting massive data, originally built at Tencent
- [Meltano](https://github.com/meltano/meltano) - A declarative code-first data integration engine 
- [Apache SeaTunnel](https://github.com/apache/seatunnel) - A high-performance, distributed data integration tool supporting vairous ingestion patterns

### CDC Tool
- [Debezium](https://github.com/debezium/debezium) - A change data capture framework supporting variety of databases
- [Kafka Connect](https://github.com/apache/kafka) - A streaming data integration framework and runtime on top of Apache Kafka supporting CDC
- [Flink CDC Connectors](https://github.com/ververica/flink-cdc-connectors) - CDC Connectors for Apache Flink engine supporting different databases
- [Brooklin](https://github.com/linkedin/brooklin) - A distributed platform for streaming data between various heterogeneous source and destination systems
- [RudderStack](https://github.com/rudderlabs/rudder-server) - A headless Customer Data Platform to build data pipelines, open alternative to Segment

### Log & Event Collection
- [CloudQuery](https://github.com/cloudquery/cloudquery) - An ETL tool for syncing data from cloud APIs to variety of supported destinations 
- [Snowplow](https://github.com/snowplow/snowplow) - A cloud-native engine for collecting behavioral data and load into various cloud storage systems
- [EventMesh](https://github.com/apache/eventmesh) - A serverless event middlewar for collecting and loading event data into various targets
- [Apache Flume](https://github.com/apache/flume) - A scalable distributed log aggregation service
- [Steampipe](https://github.com/turbot/steampipe) - A zero-ETL solution for getting data directly from APIs and services

### Event Hub
- [Apache Kafka](https://github.com/apache/kafka) - A highly scalable distributed event store and streaming platform
- [NSQ](https://github.com/nsqio/nsq) - A realtime distributed messaging platform designed to operate at scale
- [Apache Pulsar](https://github.com/apache/pulsar) - A scalable distributed pub-sub messaging system
- [Apache RocketMQ](https://github.com/apache/rocketmq) - A a cloud native messaging and streaming platform
- [Redpanda](https://github.com/redpanda-data/redpanda) - A high performance Kafka API compatible streaming data platform 
- [Memphis](https://github.com/memphisdev/memphis) - A scalable data streaming platform for building event-driven applications


## DATA PROCESSING AND COMPUTATION

### Unified Processing
- [Apache Beam](https://github.com/apache/beam) - A unified programming model supporting execution on popular distributed processing backends 
- [Apache Spark](https://github.com/apache/spark) - A unified analytics engine for large-scale data processing 
- [Dinky](https://github.com/DataLinkDC/dinky) - A unified streaming & batch computation platform based on Apache Flink

### Batch processing
- [Hadoop MapReduce](https://github.com/apache/hadoop) - A  highly scalable distributed batch processing framework from Apache Hadoop project
- [Apache Tez](https://github.com/apache/tez) - A distributed data processing pipeline built for Apache Hive and Hadoop


### Stream Processing
- [Apache Flink](https://github.com/apache/flink) - A scalable high throughput stream processing framework 
- [Apache Samza](https://github.com/apache/samza) - A distributed stream processing framework which uses Kafka and Hadoop, originally developed by LinkedIn
- [Apache Storm](https://github.com/apache/storm) - A distributed realtime computation system based on  Actor Model framework
- [Benthos](https://github.com/benthosdev/benthos) - A high performance declarative stream processing engine 
- [Akka](https://github.com/akka/akka) - A highly concurrent, distributed, message-driven processing system based on Actor Model 
- [Bytewax](https://github.com/bytewax/bytewax) - A Python stream processing framework with a Rust distributed processing engine

### Parallel Python Execution
- [Vaex](https://github.com/vaexio/vaex) - A high performance Python library for  big tabular datasets.
- [Dask](https://github.com/dask/dask) - A flexible parallel computing library for analytics
- [Polars](https://github.com/pola-rs/polars) - A multithreaded Dataframe with vectorized query engine, written in Rust
- [PySpark](https://github.com/apache/spark) - An interface for Apache Spark in Python
- [RAY](https://github.com/ray-project/ray) - A unified framework with distributed runtime for scaling python applications
- [Apache Arrow](https://github.com/apache/arrow) - An efficient in-memory data format


## WORKFLOW MANAGEMENT & DATAOPS

### Workflow Orchestration
- [Apache Airflow](https://github.com/apache/airflow) - A plaform for creating and scheduling workflows as directed acyclic graphs (DAGs) of tasks
- [Prefect](https://github.com/PrefectHQ/prefect) - A Python based workflow orchestration tool 
- [Argo](https://github.com/argoproj/argo-workflows) - A container-native workflow engine for orchestrating parallel jobs on Kubernetes 
- [Azkaban](https://github.com/azkaban/azkaban) - A batch workflow job scheduler created at LinkedIn to run Hadoop jobs
- [Cadence](https://github.com/uber/cadence) - A distributed, scalable available orchestration supporting different language client libraries
- [Dagster](https://github.com/dagster-io/dagster) - A cloud-native data pipeline orchestrator written in Python
- [Apache DolpinScheduler](https://github.com/apache/dolphinscheduler) - A low-code high performance workflow orchestration platform
- [Luigi](https://github.com/spotify/luigi) - A python library for building complex pipelines of batch jobs
- [Flyte](https://github.com/flyteorg/flyte) - A scalable and flexible workflow orchestration platform for both data and ML workloads
- [Kestra](https://github.com/kestra-io/kestra) - A declarative language-agnostic worfklow orchestration and scheduling platform
- [Mage.ai](https://github.com/mage-ai/mage-ai) - A platform for integrating, cheduling and managing data pipelines
- [Temporal](https://github.com/temporalio/temporal) - A resilient workflow management system, originated as a fork of Uber's Cadence
- [Windmill](https://github.com/windmill-labs/windmill) - A fast workflow engine, and open-source alternative to Airplane and Retool

### Data Quality
- [Data-diff](https://github.com/datafold/data-diff) - A tool for comparing tables within or across databases 
- [Great Expectations](https://github.com/great-expectations/great_expectations) - A data validation and profiling tool written in Python
- [DataKitchen Open Source Data Observability](https://docs.datakitchen.io/articles/?readerUiPreview=1#!open-source-data-observability/data-observability-overview) - End to end Data Journey Observability plus data profiling, anomaly detection, and auto created data quality validation tests.  With UI. Apache 2.0 license

### Data Versioning
- [LakeFS](https://github.com/treeverse/lakeFS) - A data version control for data stored in data lakes
- [Project Nessie](https://github.com/projectnessie/nessie) - A transactional Catalog for Data Lakes with Git-like semantics

### Data Modeling
- [dbt](https://github.com/dbt-labs/dbt-core) - A data modeling and transformation tool for data pipelines
- [SQLMesh](https://github.com/TobikoData/sqlmesh) - A data transformation and modeling framework that is backwards compatible with dbt.

## DATA INFRASTRUCTURE

### Resource Scheduling
- [Apache Yarn](https://github.com/apache/hadoop) - The default Resource Scheduler for Apache Hadoop clusters
- [Apache Mesos](https://github.com/apache/mesos) - A resource scheduling and cluster resource abstraction framework developed by Ph.D. students at UC Berkeley
- [Kubernetes](https://github.com/kubernetes/kubernetes) - A production-grade container scheduling and management tool
- [Docker](https://github.com/docker) - The popular OS-level virtualization and containerization software

### Cluster Administration
- [Apache Ambari](https://github.com/apache/ambari) - A tool for provisioning, managing, and monitoring of Apache Hadoop clusters 
- [Apache Helix](https://github.com/apache/helix) - A generic cluster management framework developed at LinkedIn

### Security
- [Apache Knox](https://github.com/apache/knox) - A gateway and SSO service for managing access to Hadoop clusters
- [Apache Ranger](https://github.com/apache/ranger) - A security and governance platform for Hadoop and other popular services
- [Kerberos](https://github.com/krb5/krb5) - A popular enterprise network authentication protocol

### Metrics Store
- [Influxdb](https://github.com/influxdata/influxdb) - A scalable datastore for metrics and events
- [Mimir](https://github.com/grafana/mimir) - A scalable long-term metrics storage for Prometheus, developed by Grafana Labs
- [OpenTSDB](https://github.com/OpenTSDB/opentsdb) - A distributed, scalable Time Series Database written on top of Apache Hbase
- [M3](https://github.com/m3db/m3) - A distributed TSDB and metrics storage and aggregator

### Observability Framework
- [Prometheus](https://github.com/prometheus/prometheus) - A popular metric collection and management tool
- [ELK](https://www.elastic.co/elastic-stack) - A poular observability stack comprsing of Elasticsearch, Kibana, Beats, and Logstash
- [Graphite](https://github.com/graphite-project) - An established infrastructure monitoring and observability system
- [OpenTelemetry](https://github.com/open-telemetry) - A collection of APIs, SDKs, and tools for managing and monitoring metrics
- [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics/) - An scalable monitoring solution with a time series database
- [Zabbix](https://github.com/zabbix/zabbix) - A real-time infrastructure and application monitoring service

### Monitoring Dashboard
- [Grafana](https://github.com/grafana/grafana) - A popular open and composable observability and data visualization platform
- [Kibana](https://github.com/elastic/kibana) - The visualistion and search dashboard for Elasticsearch
- [RConsole](https://github.com/redpanda-data/console) - A UI for monitoring and managing Apache Kafka and Redpanda workloads.

### Log & Metrics Pipeline
- [Fluentd](https://github.com/fluent/fluentd) - A metric collection, buffering and router service
- [Fluent Bit](https://github.com/fluent/fluent-bit) - A fast log processor and forwarder, and part of the Fluentd ecosystem
- [Logstash](https://github.com/elastic/logstash) - A server-side log and metric transport and processor, as part of the ELK stack
- [Telegraf](https://github.com/influxdata/telegraf) - A plugin-driven server agent for collecting & reporting metrics developed by Influxdata
- [Vector](https://github.com/vectordotdev/vector) - A  high-performance, end-to-end (agent & aggregator) observability data pipeline
- [StatsD](https://github.com/statsd/statsd) - A network daemon for collection, aggregation and routing of metrics


## METADATA MANAGEMENT

### Metadata Platform
- [Amundsen](https://github.com/amundsen-io/amundsen) - A data discovery and metadata engine developed by Lyft engineers
- [Apache Atlas](https://github.com/apache/atlas) - A data observability platform for Apache Hadoop ecosystem
- [DataHub](https://github.com/datahub-project/datahub) - A metadata platform for the modern data stack developed at Netflix
- [Marquez](https://github.com/MarquezProject/marquez) - A metadata service for the collection, aggregation, and visualization of metadata
- [ckan](https://github.com/ckan/ckan) - A data management system  for cataloging, managing and accessing data
- [Open Metadata](https://github.com/open-metadata/OpenMetadata) - A unified platform for discovery and governance, using a central metadata repository

### Open Standards
- [Open Lineage](https://github.com/OpenLineage/OpenLineage) - An open standard for lineage metadata collection 
- [Open Metadata](https://github.com/open-metadata/OpenMetadata) - A unified metadata platform providing open stadards for managing metadata
- [Egeria](https://github.com/odpi/egeria) - Open metadata and governance standards to facilitate metadata exchange

### Schema Service
- [Hive Metastore](https://github.com/apache/hive) - A popular schema management and metastore service as part of the Apache hive project
- [Confluent Schema Registry](https://github.com/confluentinc/schema-registry) - A schema registry for Kafka, developed by Confluent 

## ANALYTICS & VISUALISATION

### BI & Dashboard
- [Apache Superset](https://github.com/apache/superset) - A poular open source data visualization and data exploration platform 
- [Metabase](https://github.com/metabase/metabase) - A simple data visualisation and exploration dashboard
- [Redash](https://github.com/getredash/redash) - A tool to explore, query, visualize, and share data with many data source connectors
- [Streamlit](https://github.com/streamlit/streamlit) - A python tool to package and share data as web apps

### Query & Collaboration
- [Hue](https://github.com/cloudera/hue) - A query and data exploration tool with Hadoop ecosystem support, developed by Cloudera
- [Apache Zeppelin](https://github.com/apache/zeppelin) - A web-base Notebook for interactive data analytics and collaboration for Hadoop
- [Querybook](https://github.com/pinterest/querybook) - A simple query and notebook UI developed by Pinterest
- [Jupyter](https://github.com/jupyter/notebook) - A popular interactive web-based notebook application

### MPP Query Engine
- [Apache Hive](https://github.com/apache/hive) - A data warehousing and MPP engine on top of Hadoop
- [Apache Implala](https://github.com/apache/impala) - A MPP engine mainly for Hadoop clusters, developed by Cloudera 
- [Presto](https://github.com/prestodb/presto) - A distributed SQL query engine for big data
- [Trino](https://github.com/trinodb/trino) - The former PrestoSQL distributed SQL query engine
- [Apache Drill](https://github.com/apache/drill) - A distributed MPP query engine against NoSQL and Hadoop data storage systems

### Semantic Layer
- [Alluxio](https://github.com/Alluxio/alluxio) - A data orchestration and virtual distributed storage system
- [Cube](https://github.com/cube-js/cube) - A semantic layer for building data applications supporting popular databse engines
- [Apache Linkis](https://github.com/apache/linkis) - A computation middleware to facilitate connection and orchestration between applications and data engines 

## ML/AI PLATFORM

### Vector Storage
- [milvus](https://github.com/milvus-io/milvus) -  A cloud-native vector database, storage for AI applications 
- [qdrant](https://github.com/qdrant/qdrant) - A high-performance, scalable Vector database for AI
- [chroma](https://github.com/chroma-core/chroma) - An AI-native embedding database for building LLM apps
- [marqo](https://github.com/marqo-ai/marqo) - An end-to-end vector search engine for both text and images
- [LanceDB](https://github.com/lancedb/lancedb) - A serverless vector database for AI applications written in Rust
- [weaviate](https://github.com/weaviate/weaviate) - A scalable, cloud-native supporting storage of both objects and vectors
- [deeplake](https://github.com/activeloopai/deeplake) -  A storage format optimized AI database for deep-learning applications
- [Vespa](https://github.com/vespa-engine/vespa) - A storage to organize vectors, tensors, text and structured data
- [vald](https://github.com/vdaas/vald) - A scalable distributed approximate nearest neighbor (ANN) dense vector search engine
- [pgvector](https://github.com/pgvector/pgvector) - A vector similarity search as a Postgres extension

### MLOps
- [mlflow](https://github.com/mlflow/mlflow) - A a platform to streamline machine learning development and lifecycle management
- [Metaflow](https://github.com/Netflix/metaflow) - A tool to build and manage ML/AI, and data science projects, developed at Netflix
- [SkyPilot](https://github.com/skypilot-org/skypilot) - A framework for running LLMs, AI, and batch jobs on any cloud
- [Jina](https://github.com/jina-ai/jina) - A tool to build multimodal AI applications with cloud-native stack
- [NNI](https://github.com/microsoft/nni) - An autoML toolkit for automate machine learning lifecycle, from Microsoft
- [BentoML](https://github.com/bentoml/BentoML) - A framework for building reliable and scalable AI applications
- [Determined AI](https://github.com/determined-ai/determined) - An ML platform that simplifies distributed training, tuning and experiment tracking
- [RAY](https://github.com/ray-project/ray) - A unified framework for scaling AI and Python applications
- [kubeflow](https://github.com/kubeflow/kubeflow) - A cloud-native platform for ML operations - pipelines, training and deployment
