# DataVigil: MLOps and Deployment Guide

This document provides a beginner-friendly explanation of how the **DataVigil** application works, how it is packaged using Docker, and how it is deployed automatically to AWS using GitHub Actions.

---

## 1. How DataVigil Works (The Application Flow)

DataVigil is an autonomous business intelligence supervisor. It takes natural language questions from a user (e.g., *"Find anomalies in sales"*), translates them to SQL queries, executes them on a database, detects statistical outliers (anomalies), and plots the results.

### The System Architecture Flow:
```mermaid
graph TD
    User[1. User Interface] -->|Natural Language Query| API[2. FastAPI Backend]
    API -->|Prompt Injection Check| Guard[3. Security Guard]
    Guard -->|Sanitized Query| LLM[4. LangGraph / Gemini Agent]
    LLM -->|Generate & Validate| SQL[5. SQLite Database]
    SQL -->|Dataset Output| Outliers[6. Scikit-learn Outlier Model]
    Outliers -->|Anomalous Rows + Outlier Scores| Plotly[7. Dashboard Builder]
    Plotly -->|Interactive Plotly Dashboard| User
```

---

## 2. Code Structure

DataVigil is structured as a React web application (frontend) connected to a Python FastAPI microservice (backend).

```text
DataVigil/
├── backend/
│   ├── main.py          # FastAPI application entrypoint
│   ├── config.py        # Environment variables & API key loader
│   ├── agents/          # LangGraph SQL generation loop & prompts
│   ├── database/        # SQLite connection & database seeding
│   ├── security/        # HuggingFace prompt classifier & SQL sanitizer
│   └── Dockerfile       # Unified multi-stage container blueprint
└── frontend/            # React + TypeScript single-page application (SPA)
```

---

## 3. The Docker Blueprint (How We Containerize)

We use a **Multi-Stage Dockerfile** located at `backend/Dockerfile` to package the entire application on port `8000`:

```mermaid
graph LR
    subgraph Stage1[Stage 1: Node.js Builder]
        Node[Install Frontend Packages] --> Build[Compile React to dist/]
    end
    subgraph Stage2[Stage 2: Python Runner]
        Python[Install Python & Libraries] --> CopyCode[Copy FastAPI Backend]
        Build -->|Copy Static Files| Static[Copy dist/ to static/]
    end
    Stage2 --> Package[Container ready on Port 8000]
```

### Why we do this:
* **Single Port Utility:** By copying the built React files directly into the Python container, FastAPI can serve both the API backend and the static UI pages on a single port (`8000`). This avoids having to run Nginx separately.
* **Portability:** You do not need to compile code on the server. The runner starts instantly.

---

## 4. The GitHub Actions CD Pipeline (Continuous Deployment)

When you run `git push origin main`, GitHub starts a temporary virtual machine to execute the assembly line defined in `.github/workflows/deploy.yml`:

```mermaid
sequenceDiagram
    autonumber
    participant Local as Your Local Computer
    participant GH as GitHub Actions VM
    participant ECR as AWS ECR Registry
    participant EC2 as AWS EC2 Server

    Local->>GH: git push origin main
    Note over GH: Loads secrets: AWS keys, IP, Instance ID
    GH->>GH: Build Docker image (Stage 1 Node + Stage 2 Python)
    GH->>ECR: Login & Push image to 'datavigil' repo
    GH->>EC2: Send SSH public key (EC2 Instance Connect)
    GH->>EC2: SSH into instance and run deployment script
    Note over EC2: 1. Pull latest image from ECR<br/>2. Stop old DataVigil container<br/>3. Start new container on Port 8000
    EC2-->>Local: Live at http://98.89.32.36:8000
```

---

## 5. AWS Cloud Components

DataVigil relies on these core AWS services:
1. **AWS ECR (Elastic Container Registry):** A private cloud folder where your built Docker image is stored.
2. **AWS EC2 (Elastic Compute Cloud):** A virtual server (`t3.micro`) running Ubuntu 22.04 that downloads and hosts the Docker container.
3. **AWS Security Group:** An inbound firewall rule configured to open **Port 8000** (so you can view the dashboard UI) and **Port 22** (for secure SSH management).
4. **AWS S3 (Simple Storage Service):** Used by the application to persist reports and backups in the cloud.
