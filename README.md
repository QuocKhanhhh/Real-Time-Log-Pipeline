# Real-Time-Log-Pipeline


## Overview
A real-time log analysis pipeline for **ShopEasy**, an e-commerce platform. The pipeline processes website logs to track user behavior, detect bots, and support business decisions using **Kafka**, **Spark Structured Streaming**, **PostgreSQL**, and **Matplotlib**, deployed in **Docker**.

### Architecture
![Architecture Diagram](docs/architecture.png)
- **Producer**: Generates realistic logs using Faker and sends to Kafka.
- **Kafka**: Streams logs to Spark.
- **Spark**: Analyzes logs, saving results to PostgreSQL:
  - `product_views`: Product view counts.
  - `action_counts`: Action ratios.
- **PostgreSQL**: Stores results in tables, replacing multiple CSV files.
- **Matplotlib**: Visualizes data as charts.

### Technologies
- Kafka, Spark, PostgreSQL, Python (Faker, Pandas, Matplotlib, SQLAlchemy), Docker

### Prerequisites
- Docker, Docker Compose
- Python 3.8+
- Git

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/shopeasy-pipeline.git
   cd shopeasy-pipeline
2. Start Docker services:
3. 
