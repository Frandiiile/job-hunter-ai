# Stock Market Real-Time Analysis
- Built a real-time data pipeline collecting live stock data using yfinance.
- Streamed data through Kafka producers and consumers for event-driven architecture.
- Processed streaming data using Python applications.
- Stored processed data in Google BigQuery for analytical querying.
- Deployed services using Docker and docker-compose.
- Built reporting dashboards in Looker Studio using BigQuery datasets.
- Designed the pipeline with modular ingestion, processing, and storage layers.

# Weather Dashboarding (Big Data Weather Analysis)
- Collected meteorological data from NOAA for large-scale processing.
- Implemented distributed data processing using Hadoop and MapReduce.
- Orchestrated ETL workflows using Apache Airflow.
- Developed Python scripts for extraction, transformation, and analysis.
- Designed data preparation layers for analytics consumption.
- Built analytical dashboards in Power BI.

# Job Hunter AI (Personal Job Intelligence & Automation Platform)

- Built a multi-source job ingestion system integrating Adzuna, Jooble API, and France Travail API.
- Designed connector-based architecture to normalize job postings into a unified schema.
- Implemented rule-based filtering engine for junior Data Engineer roles (<=2 years experience).
- Developed deterministic skill-overlap scoring system based on structured profile knowledge base (YAML).
- Integrated LLM-based resume and cover letter tailoring engine using personal bullet banks.
- Automated Google Sheets job tracking workflow with status management (NEW / APPLIED / REJECTED).
- Orchestrated workflows using n8n for scheduling, execution, and notifications.
- Implemented automated email reminders and daily summary reports for high-match roles.
- Designed modular architecture separating ingestion, scoring, enrichment, and document generation layers.
- Built system as reproducible, API-driven automation platform.

# Modern Data Warehouse with dbt & Snowflake 
- Design and implement a cloud data warehouse using Snowflake.
- Build ELT pipelines transforming raw data into analytics-ready models.
- Implement dimensional modeling (star and snowflake schemas).
- Use dbt for modular transformations and automated data testing.
- Integrate CI/CD pipelines for automated testing and deployment.
- Implement data quality validation and documentation generation.
- Optimize warehouse performance and cost efficiency.

# Real-Time Streaming Pipeline with Kafka & Spark
- Build event-driven architecture using Kafka producers and consumers.
- Process streaming data using Spark Structured Streaming.
- Implement checkpointing and exactly-once processing guarantees.
- Store streaming outputs into Delta Lake tables.
- Handle schema evolution in streaming pipelines.
- Deploy services using Docker and Kubernetes (basic orchestration).
- Monitor streaming jobs and implement failure recovery mechanisms.

# Data Quality & Lineage Framework
- Implement data validation framework using Great Expectations.
- Integrate automated data quality checks into CI/CD workflows.
- Track data lineage using OpenLineage.
- Design data contracts between ingestion and transformation layers.
- Implement schema drift detection and anomaly monitoring.
- Build alerting mechanisms for pipeline integrity issues.

# Data Product REST API
- Build RESTful API exposing curated analytical datasets.
- Develop API using FastAPI for high-performance data serving.
- Connect API to data warehouse (Snowflake / BigQuery / Delta Lake).
- Implement authentication and role-based access control.
- Design pagination, filtering, and query parameterization for scalable consumption.
- Containerize API using Docker and deploy to cloud environment.
- Implement logging, monitoring, and basic rate limiting.
- Document endpoints using OpenAPI / Swagger.
- Design API as a data product layer separating storage and consumption.
