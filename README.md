# DataVigil -- Autonomous ReAct Data Intelligence and Anomaly Detection Agent

DataVigil is an autonomous **ReAct Data Agent** built with **LangGraph**, **SQLite**, **Scikit-learn**, and **Plotly**. It converts natural language business queries into verified SQL statements, executes ML anomaly detection pipelines (Isolation Forest and Local Outlier Factor), and generates interactive real-time visual dashboards -- guarded by HuggingFace prompt injection protection.

---

## Architecture Topology

```mermaid
graph TB
    subgraph USER_INTERFACE["Interface and Dashboard"]
        NL_IN["Natural Language Query Input"]
        PLOTLY["Plotly Interactive Charts and Visuals"]
        REST["FastAPI REST API and Web App"]
    end

    subgraph SECURITY_GUARD["Security and Injection Guardrail"]
        HF_GUARD["HuggingFace Prompt Injection Classifier"]
        SQL_SAN["SQL Sanitizer and Read-Only Enforcer"]
    end

    subgraph REACT_ENGINE["LangGraph ReAct Agent Loop"]
        PLANNER["Query Planner Node"]
        SQL_GEN["SQL Generator Agent"]
        EXEC["Database Execution Engine"]
        ML_ANOM["ML Anomaly Detector Node"]
        SYNTH["Dashboard Synthesizer"]
    end

    subgraph DATA_STORAGE["Data Storage and ML Engines"]
        SQLITE[("SQLite / PostgreSQL Database")]
        SKLEARN["Scikit-learn Isolation Forest / LOF"]
    end

    NL_IN --> HF_GUARD
    HF_GUARD -->|sanitized| PLANNER
    PLANNER --> SQL_GEN
    SQL_GEN --> SQL_SAN
    SQL_SAN --> EXEC
    EXEC <--> SQLITE
    EXEC --> ML_ANOM
    ML_ANOM <--> SKLEARN
    ML_ANOM --> SYNTH
    SYNTH --> PLOTLY
    SYNTH --> REST

    style USER_INTERFACE fill:#18181b,stroke:#a1a1aa,color:#fff
    style SECURITY_GUARD fill:#18181b,stroke:#ffffff,color:#fff
    style REACT_ENGINE fill:#000000,stroke:#ffffff,color:#fff
    style DATA_STORAGE fill:#18181b,stroke:#e4e4e7,color:#fff
```

---

## Autonomous ReAct Execution Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User / Analytics Interface
    participant Guard as Security Guardrail
    participant Agent as LangGraph ReAct Agent
    participant DB as SQL Database Engine
    participant ML as Scikit-Learn Anomaly Model

    User->>Guard: Natural Language Query (e.g. Detect unusual sales spikes)
    Guard->>Guard: Verify prompt injection safety
    Guard->>Agent: Pass safe natural language query
    Agent->>Agent: Plan SQL query and anomaly parameters
    Agent->>DB: Execute dynamically generated SQL
    DB-->>Agent: Return structured tabular dataset
    Agent->>ML: Run Isolation Forest / LOF outlier detection
    ML-->>Agent: Tag anomalous rows and confidence scores
    Agent->>Agent: Build interactive Plotly chart JSON
    Agent-->>User: Render Plotly dashboard + Anomaly report
```

---

## Core Capabilities and Security Features

- **Natural Language to SQL**: Converts complex business questions into ANSI SQL queries with schema validation.
- **Machine Learning Anomaly Detection**: Unsupervised Isolation Forest and Local Outlier Factor (LOF) models identify outliers in temporal and multi-variate business metrics.
- **Prompt Injection Protection**: HuggingFace classifier and SQL AST parser block destructive statements (DROP, DELETE, UPDATE) and jailbreak attempts.
- **Interactive Visualization**: Generates Plotly JSON chart specifications directly rendered in frontend dashboards.

---

## Directory Structure

```
DataVigil/
|-- docker-compose.yml          # Container orchestration (Backend + Frontend)
|-- README.md                   # ASCII Architecture and User Documentation
|-- backend/
|   |-- Dockerfile              # Python FastAPI & Scikit-learn container
|   |-- requirements.txt        # FastAPI, LangGraph, Scikit-Learn, Plotly dependencies
|   |-- main.py                 # FastAPI server entry point
|   |-- config.py               # Environment & database settings
|   |-- agents/                 # ReAct agent implementation & prompt templates
|   |-- database/               # SQL engine & schema inspector
|   |-- security/               # Prompt injection classifier & SQL sanitizer
|   `-- tests/                  # Pytest unit & integration tests
`-- frontend/                   # Dashboard Web UI
```

---

## Quick Start Guide

### Prerequisites
- Python 3.10+
- SQLite or PostgreSQL database instance
- Docker and Docker Compose (Optional)

### Running Locally

1. **Clone Repository**:
   ```bash
   git clone https://github.com/siddarth1872004/DataVigil.git
   cd DataVigil
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Access Dashboard API**:
   Navigate to `http://localhost:8000/docs`.

---

## License

Distributed under the **MIT License**. See `LICENSE` for details.
