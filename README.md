# Job Application Intelligence Dashboard

A REST API that tracks your job hunt and tells you what's actually working.
Built because job hunting felt completely random - this gives you real data on which platforms respond, which days get callbacks, and how long you're waiting to hear back.

---

## Features

- **Log applications** — track company, role, platform, application type, and stage
- **Update pipeline stages** — move applications from Applied → Recruiter → Technical → Final → Offer / Rejected
- **Platform analytics** — see which platform (LinkedIn, Naukri, etc.) gets the most responses
- **Day-of-week insights** — find out which day you apply on gets the most callbacks
- **Response time tracking** — average, fastest, and slowest days to hear back
- **Weekly summary** — full overview of your pipeline at a glance
- **Visual chart** — bar chart of applications by stage rendered directly in the browser

---

## Tech Stack

- **FastAPI** — Python web framework for building REST APIs
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM for database interaction
- **Pandas** — data aggregation for analytics endpoints
- **Matplotlib** — chart generation
- **Docker + Docker Compose** — containerised for easy local setup and deployment

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git

### Setup

**1. Clone the repository:**

```bash
git clone https://github.com/yourusername/job-tracker-api.git
cd job-tracker-api
```

**2. Create a `.env` file in the root:**

```
DATABASE_URL=postgresql://admin:password@db:5432/jobtracker
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=jobtracker
```

**3. Start the app:**

```bash
docker-compose up --build
```

**4. Open the API docs:**

```
http://localhost:8000/docs
```

That's it. The database is created automatically on first run.

---

## API Endpoints

### Applications

| Method | Endpoint             | Description                                             |
| ------ | -------------------- | ------------------------------------------------------- |
| POST   | `/applications`      | Log a new application                                   |
| GET    | `/applications`      | List all applications (filter by `stage` or `platform`) |
| PATCH  | `/applications/{id}` | Update stage or response date                           |
| DELETE | `/applications/{id}` | Delete an application                                   |

### Analytics

| Method | Endpoint                   | Description                                |
| ------ | -------------------------- | ------------------------------------------ |
| GET    | `/analytics/platform`      | Response rate by platform                  |
| GET    | `/analytics/days`          | Applications and responses by day of week  |
| GET    | `/analytics/response-time` | Average, fastest, slowest days to response |
| GET    | `/analytics/summary`       | Full weekly overview                       |
| GET    | `/analytics/chart/stages`  | Bar chart of applications by stage (PNG)   |

---

## Example Requests

**Log a new application:**

```bash
curl -X POST http://localhost:8000/applications \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Stripe",
    "role": "Backend Engineer",
    "platform": "linkedin",
    "app_type": "tailored",
    "stage": "applied",
    "applied_date": "2026-05-17"
  }'
```

**Get weekly summary:**

```bash
curl http://localhost:8000/analytics/summary
```

**Example response:**

```json
{
  "total_applied": 24,
  "total_responded": 6,
  "response_rate_%": 25.0,
  "stage_breakdown": {
    "applied": 15,
    "recruiter": 4,
    "technical": 3,
    "rejected": 2
  },
  "platform_breakdown": {
    "linkedin": 14,
    "naukri": 6,
    "company site": 4
  },
  "app_type_breakdown": {
    "easy": 10,
    "tailored": 12,
    "referral": 2
  }
}
```

**View stage chart:**

Open in browser:

```
http://localhost:8000/analytics/chart/stages
```

---

## Project Structure

```
job-tracker-api/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── database.py      # Database connection and session
│   ├── routers.py       # CRUD endpoints
│   └── analytics.py     # Analytics and chart endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                 # not committed — create locally
```

---

## Why I Built This

Job hunting felt like shouting into a void. No visibility into what was working, which platforms were worth the effort, or how long to wait before following up.

This API gives real answers - built it for myself, and it's in the testing phase.
