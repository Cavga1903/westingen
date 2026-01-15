# WESTINGEN Engineering Rationale

## 1. What is WESTINGEN?

WESTINGEN is a job-application demo that simulates an industrial sensor data monitoring system. It is a small Flask application that ingests sensor readings, stores them in PostgreSQL, and displays them on a web dashboard.

This project is NOT:
- A production-ready system
- A full-stack application with modern frontend frameworks
- A microservices architecture
- A comprehensive IoT platform

It is a focused demonstration of backend development skills using Python and Flask, designed to be runnable and understandable in under five minutes.

## 2. What Problem Does It Simulate?

Sensor data monitoring is a common requirement in industrial and IoT contexts. Manufacturing facilities, warehouses, and robotic systems generate continuous streams of telemetry data that must be collected, stored, and visualized.

This project simulates a scenario where multiple robotic devices report temperature, acceleration, and GPS coordinates. The system must handle high-frequency data ingestion, reliable storage, real-time visualization, and basic statistical analysis.

This domain was chosen because it is realistic and commonly encountered in industry, requires handling structured time-series data, demonstrates both data ingestion and retrieval patterns, and provides clear, measurable metrics. The problem is intentionally simplified but representative of real-world sensor monitoring systems found in manufacturing, logistics, and automation environments.

## 3. Feature Overview

**Backend Capabilities:**
- RESTful API with four endpoints for health checks, data ingestion, retrieval, and statistics
- Input validation that rejects malformed or missing data
- Database persistence with indexed queries for efficient retrieval
- Statistical aggregation (counts, averages, min/max values)

**Data Model:**
The system handles sensor readings containing:
- Device identification
- Temperature measurements (Celsius)
- Three-axis acceleration data
- GPS coordinates (latitude/longitude)
- Timestamps for temporal analysis

**Dashboard:**
- Key performance indicators (total records, latest temperature, last update time)
- Line chart showing temperature trends over time
- Tabular view of the most recent 50 readings
- Auto-refresh every 5 seconds using vanilla JavaScript

The dashboard is intentionally simple. It demonstrates data visualization without requiring complex frontend tooling.

## 4. Key Engineering Decisions

### Flask Instead of Django or FastAPI

**Decision:** Use Flask as the web framework.

**Alternatives Considered:**
- Django: More batteries-included, heavier framework
- FastAPI: Modern async framework with automatic OpenAPI documentation

**Why This Choice:**
Flask provides minimal structure without imposing architectural decisions. For a small demo, Django's ORM, admin panel, and middleware are unnecessary overhead. FastAPI's async features are unnecessary for this problem and would increase cognitive load without practical benefit.

Flask allows explicit control over routing, database connections, and response formatting. The code is straightforward and easy to follow, which is important for a job application demo where clarity matters more than framework sophistication.

**Trade-off:** Flask requires more manual setup than Django, but this makes the application structure more transparent.

### Server-Rendered HTML Instead of React or SPA Frameworks

**Decision:** Use Jinja2 templates with Bootstrap and Chart.js via CDN.

**Alternatives Considered:**
- React with a separate frontend application
- Next.js for server-side rendering
- Vue.js or other SPA frameworks

**Why This Choice:**
A single Flask application is simpler to run, understand, and deploy. Server-rendered HTML eliminates the need for a separate frontend build process, API authentication tokens, or CORS configuration. The dashboard requirements (KPI cards, a line chart, and a table) are achievable with vanilla JavaScript and Chart.js.

The dashboard exists to validate backend behavior, not to showcase frontend engineering. For a job application focused on backend skills, a complex frontend framework adds unnecessary complexity without demonstrating relevant expertise.

**Trade-off:** The UI is less interactive than a modern SPA, but it serves the demo's purpose and keeps the project focused.

### PostgreSQL

**Decision:** Use PostgreSQL as the database.

**Alternatives Considered:**
- SQLite: Simpler setup, no separate database server
- MongoDB: NoSQL document store
- In-memory storage: No persistence

**Why This Choice:**
PostgreSQL is a standard choice for production applications and demonstrates familiarity with relational databases. It provides proper data types, indexing, and ACID guarantees. SQLite would be simpler for a demo, but PostgreSQL better represents real-world backend development.

The migration file uses plain SQL, making the schema explicit and easy to understand. No ORM is used to keep database interactions transparent.

**Trade-off:** Requires a separate database server, but this is standard in production environments and demonstrates proper database setup.

### No Authentication

**Decision:** Omit authentication and authorization.

**Alternatives Considered:**
- JWT-based authentication
- Session-based authentication
- API key authentication

**Why This Choice:**
Authentication adds complexity (user models, token management, password hashing) that doesn't demonstrate core backend data handling skills. For a demo that must run in under five minutes, authentication is unnecessary overhead.

This is a conscious simplification. In production, authentication would be mandatory, but for a job application demo, it distracts from the core functionality.

**Trade-off:** The system is not secure, but this is acceptable for a local demo environment.

### No Docker

**Decision:** Provide setup instructions instead of Docker containers.

**Alternatives Considered:**
- Docker Compose with Flask and PostgreSQL containers
- Single Dockerfile for the application

**Why This Choice:**
Docker solves deployment problems. This demo focuses on understanding, not deployment. For a job application, showing direct Python and PostgreSQL setup demonstrates understanding of the underlying technologies. Setup instructions are clear and take less than five minutes.

**Trade-off:** Manual setup is required, but this makes the technology stack transparent.

### Intentionally Small System

**Decision:** Limit to 10 API endpoints, 20 dependencies, and a single application.

**Alternatives Considered:**
- Microservices architecture
- More endpoints and features
- Additional services (message queues, caching layers)

**Why This Choice:**
A small, focused system is easier to understand, run, and evaluate. It demonstrates core backend skills without overwhelming complexity. The goal is to show competence in data ingestion, storage, retrieval, and basic visualization—not to build a comprehensive platform.

A recruiter or interviewer can understand the entire system in minutes. Adding microservices, message queues, or caching would make the demo more impressive but less comprehensible.

**Trade-off:** The system is limited in scope, but this limitation is intentional and serves the demo's purpose.

## 5. What Is Intentionally NOT Included

The following features are consciously excluded:

**Authentication and Authorization:** Not included because they add complexity without demonstrating core data handling skills. In production, these would be mandatory.

**Unit Tests:** Not included because the demo focuses on functionality over test coverage. Tests would be valuable in production but are not necessary for a runnable demo.

**CI/CD Pipelines:** Not included because the project is designed for local execution. Continuous integration would be standard in production but adds setup complexity.

**Production Hardening:** Security headers, rate limiting, HTTPS, and monitoring are not included. These are important in production but not relevant for a local demo.

**Docker Containerization:** Not included because manual setup demonstrates understanding of the technology stack. Docker would simplify deployment but add abstraction.

**Advanced Error Handling, Caching, and Message Queues:** Basic error handling is present, but comprehensive error recovery, retry logic, and circuit breakers are not included. No Redis, RabbitMQ, or Kafka is used. PostgreSQL queries and direct database writes are sufficient for the demo's scale and throughput requirements. These components are important in production but unnecessary for a demo.

These omissions are not gaps in knowledge but conscious decisions to keep the demo focused and runnable.

## 6. How This Project Should Be Evaluated

**What to Evaluate:**
- Code clarity and organization
- Proper use of Flask patterns (blueprints, configuration)
- Database schema design and query efficiency
- API design (RESTful endpoints, error handling, validation)
- Ability to make appropriate trade-offs
- Understanding of when to keep things simple

**What NOT to Expect:**
- Production-ready security or scalability
- Comprehensive test coverage
- Modern frontend frameworks or complex UI interactions
- Microservices architecture
- Advanced DevOps tooling

This project demonstrates backend development fundamentals, not full-stack engineering or production system design. It should be evaluated as a focused demo of Python/Flask skills, not as a complete application.

## 7. What This Project Demonstrates About the Developer

WESTINGEN demonstrates several engineering qualities:

**Focus on Delivery:** The project is complete and runnable. It prioritizes working software over theoretical perfection.

**Appropriate Simplification:** The developer understands when to omit features that don't serve the demo's purpose. Not every system needs authentication, microservices, or Docker.

**Clear Communication:** The code, README, and documentation are straightforward. The developer can explain technical decisions without relying on buzzwords.

**Understanding of Trade-offs:** Every technical decision involves trade-offs. This project shows awareness of alternatives and explicit reasoning for choices.

**Practical Skills:** The developer can build a working backend system with database integration, API design, and basic data visualization.

**Engineering Mindset:** The project follows the principle that simple, explicit code is preferable to clever abstractions. The developer values clarity over sophistication.

This project does not demonstrate expertise in React, Kubernetes, or distributed systems—and it is not intended to. It demonstrates competence in Python backend development, database design, and making appropriate technical decisions for a given context. This is a conscious junior-level demonstration, not an attempt to showcase senior-level architecture.
