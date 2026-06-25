# Distributed Task Scheduler

A distributed task scheduling system built with **FastAPI**, **PostgreSQL**, **Redis (Valkey)**, and **Python**.

The system accepts tasks through a REST API, stores them in a PostgreSQL database, queues them using Redis, dispatches them through a scheduler, and processes them using one or more worker processes. A live monitoring dashboard provides real-time visibility into task execution, worker status, retries, and system health.

---

## Live Demo

**Dashboard**

https://distributed-task-scheduler-ce6c.onrender.com/dashboard

**API**

https://distributed-task-scheduler-ce6c.onrender.com/

> The deployed application currently hosts the API and monitoring dashboard. Scheduler and worker processes are designed to run as separate background services and are executed locally in this version due to Render free-tier limitations.

---

## Features

* REST API built with FastAPI
* PostgreSQL task persistence
* Redis (Valkey) priority queue
* Worker heartbeat monitoring
* Automatic task retries
* Dead-letter queue support
* Task leasing to prevent duplicate execution
* Round-robin worker dispatching
* Live monitoring dashboard
* Task submission interface
* Real-time worker discovery
* Environment-variable based configuration for deployment

---

## Technologies

* Python
* FastAPI
* PostgreSQL
* Redis / Valkey
* SQLAlchemy
* Docker
* Render
* HTML
* CSS
* JavaScript

---

## Project Structure

```
distributed-task-scheduler/
│
├── src/
│   ├── api/
│   ├── scheduler/
│   ├── worker/
│   └── ...
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Running Locally

### Start Docker

```bash
docker compose up -d
```

### Start the API

```bash
uvicorn src.api.main:app --reload
```

### Start the Scheduler

```bash
python -m src.scheduler.main
```

### Start the Worker

```bash
python -m src.worker.main
```

Open:

```
http://127.0.0.1:8000/dashboard
```

---

## API Endpoints

| Method | Endpoint    | Description          |
| ------ | ----------- | -------------------- |
| GET    | /           | Health check         |
| POST   | /tasks      | Submit a task        |
| GET    | /tasks      | List tasks           |
| GET    | /tasks/{id} | Retrieve a task      |
| GET    | /workers    | List active workers  |
| GET    | /stats      | Dashboard statistics |
| GET    | /dashboard  | Monitoring dashboard |

---

## Architecture

```
Browser
    │
FastAPI API
    │
 ├───────────────┐
 │               │
 ▼               ▼
PostgreSQL    Redis (Valkey)
                    │
             Scheduler Service
                    │
           Worker Processes
```

---

## Future Improvements

* Deploy scheduler as a managed background worker
* Deploy multiple worker instances for horizontal scaling
* User authentication
* Task filtering and search
* Historical analytics dashboard
* WebSocket live updates
* Task cancellation and scheduling

---

## Author

**Muhammad Selim**
