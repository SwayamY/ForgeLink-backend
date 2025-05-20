# 🔗 ForgeLink Backend

> 🚫 **Proprietary License** – Not open source.  
> You may **not** clone, copy, mirror, modify, distribute, or otherwise use this code except for review in a hiring context.  
> See [LICENSE](./LICENSE) for full terms.

---

## 📖 Project Overview

**ForgeLink** is a **backend + DevOps** showcase: a containerized URL-shortener system engineered for production readiness, real-world DDoS protection, and cloud deployment.  
All services run as Docker containers—no single-service compromises.

- **Frontend** live at: https://github.com/SwayamY/ForgeLink-frontend  
- **Backend** responsibilities:
  - Redirect endpoint with toggleable protection modes  
  - Internal DDoS attacker simulating real attacks on the redirect endpoint  
  - Rate-limiting, IP-blocking, CAPTCHA modes  
  - Redis for rate metrics & analytics  
  - PostgreSQL for persistent link storage & access logs  
  - Locust for distributed load-testing  

---

## 🏗️ Architecture & Infrastructure
```
  [ Netlify Frontend ]
           │
           ▼ (HTTPS)
 ┌───────────────────────┐
 │   NGINX Reverse Proxy │
 │       (SSL/TLS)       │
 └────────────┬──────────┘
              │
              ▼
 ┌──────────────────────────┐
 │     Docker Network       │
 │ ┌───────────┐ ┌───────┐  │
 │ │  FastAPI  │ │ Locust│  │
 │ │ (API &    │ │ UI &  │  │
 │ │ DDoS Attk)│ │Tests  │  │
 │ └───────────┘ └───────┘  │
 │ ┌───────────┐ ┌─────────┐│
 │ │   Redis   │ │Postgres ││
 │ │           │ │(Storage)││
 │ └───────────┘ └─────────┘│
 └──────────────────────────┘
```
- DNS for the backend is managed via **DuckDNS** (dynamic A-record) pointing to the GCP VM  
- All services communicate over an isolated Docker network; only the redirect endpoint (`/simulate-ddos/{short_url}`) is targeted   by the internal DDoS simulator  

---

## 🌐 Cloud Deployment 

- **Infrastructure**:
  - **GCP e2-medium VM** (2 vCPU, 4 GB RAM) running Ubuntu LTS  
  - **DuckDNS** dynamic DNS provides a subdomain (`linkforge.duckdns.org`) 
  - **NGINX** reverse proxy handles SSL termination via Let’s Encrypt (Certbot auto-renewal)  
- **Security & Reliability**:
  - HTTPS enforced end-to-end (Netlify → NGINX → FastAPI)  
  - Built-in DDoS protection modes (rate limit, IP block, CAPTCHA) toggled via the `PROTECTION_MODE` environment variable.  
    The logic is implemented on the `/simulate-ddos/{short_url}` endpoint to demonstrate how each protection mode works in practice.
- **DevOps Practices**:
  - **Docker Compose** for multi-container orchestration and resource profiles (`.override.low.yml` / `.override.high.yml`)  
  - Suggest **Infrastructure as Code** (Terraform/GCP Deployment Manager) to provision VMs, firewall rules, and DNS records  
  - **Cost Optimization**: VM auto-stop scripts, low-resource mode for off-hours, monitoring of CPU/RAM to right-size instance  
- **Monitoring & Scaling**:
  - Real-time Redis metrics exported to Prometheus/GCP Monitoring (future integration)  
  - PostgreSQL logs shipped to Stackdriver or ELK stack for audit and analytics  
  - Plan for **horizontal scaling** with Kubernetes or Cloud Run once user load grows  

This setup showcases not only backend engineering but full cloud-consultancy skills—secure DNS management, SSL lifecycle, container orchestration.

---

## 🔧 Local Setup Instructions

> ⚠️ This project is **not open source**. Please read the [LICENSE](./LICENSE) before proceeding.
> _Recruiters & reviewers: follow these steps to validate functionality locally._


📁 1. Clone the Backend Repository
    ```bash
    git clone https://github.com/SwayamY/ForgeLink-backend.git
    cd LinkForge-Backend
    ```


🧪 2. Fill Out Environment Variables
```bash
    cp .envtemplate .env
```
    Update the values in `.env` with your own.  
    For local testing, only `DB_USER` and `DB_PASSWORD` are required.


🐳 3. Start Docker Containers
    Ensure Docker and Docker Compose are installed.
```bash
    docker compose up --build
```
    This will launch:
    FastAPI API at http://localhost:8000
    Redis for metrics tracking
    PostgreSQL for persistent DB storage
    Locust (for DDoS simulation + UI load testing)

🧪 4. Test the Setup
    Once the services are running:
    Visit http://localhost:8000/docs to view the API Swagger UI.
    Visit http://localhost:8089 to open the Locust web UI.
    ℹ️ Note: All containers communicate over an isolated internal Docker network.


🛡️ 5. Set Protection Mode

- Options: 'rate_limit', 'ip-block', 'captcha', 'none' 

🔄 6. Resource Profiles (optional)

- Low resourcemode ->
    ```bash    
    docker compose -f docker-compose.yml -f docker-compose.override.low.yml up
    ```    
- High resource mode ->
    ```bash    
    docker compose -f docker-compose.yml -f docker-compose.override.high.yml up
    ```

---

## 📌 Conclusion

This backend project exemplifies a production-ready, containerized architecture designed with modern DevOps, cloud, and backend principles. Built using FastAPI, PostgreSQL, Redis, and Locust, and orchestrated via Docker Compose, the system simulates a real-world environment for secure, scalable web services. Key components like rate-limiting, protection-mode-based redirect logic, and internal DDoS testing demonstrate not only backend development but also performance monitoring and security enforcement.

From a DevOps and cloud consultancy perspective, this project reflects hands-on experience with:
- Container orchestration
- Service health separation and isolation
- Dynamic .env-based deployments
- Reverse proxy setups (NGINX)
- Domain routing via DuckDNS
- Secure multi-service communication over HTTPS
- It’s a portfolio-grade project built with deployment, observability, and protection in mind—ideal for roles involving DevOps   automation, backend security architecture, and cloud-native systems.

---

## 📌 Summary for Recruiters

I'm applying for cloud consultancy, DevOps, and backend+DevOps internship roles, and this project demonstrates my readiness for those domains.
ForgeLink simulates a real-world, production-grade backend system featuring:
- Containerized infrastructure with Docker Compose
- NGINX-based reverse proxying and SSL (Let’s Encrypt)
- GCP cloud deployment with dynamic DNS (DuckDNS)
- Built-in DDoS protection modes (rate-limit, IP-block, CAPTCHA)
- Real-time metrics via Redis, database logging with PostgreSQL, and internal load-testing using Locust
The project reflects hands-on work across the stack—from cloud setup to secure service communication and traffic protection—aligned with what’s expected in modern DevOps and backend roles.
[Portfolio](https://swayamy.github.io/)
---

🔗 For further inquiries, collaboration opportunities, or DevOps/backend roles, feel free to connect with me on 
[LinkedIn](https://www.linkedin.com/in/swayam-yadav-50b741283/) or reach out via email at swayam.science777@gmail.com.