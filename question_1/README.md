# Payment Service API

## Introduction

This is a FastAPI-based payment service that provides a RESTful API for processing payments with built-in idempotency support. The service ensures that duplicate payment requests are handled gracefully, preventing accidental duplicate transactions.

### Key Features

- **Payment Processing**: Create and process payment transactions
- **Idempotency Support**: Prevents duplicate payment processing using idempotency keys
- **Async Architecture**: Built with FastAPI and async SQLAlchemy for high performance
- **Database Migrations**: Automatic database migrations using Alembic
- **Caching**: Redis integration for efficient caching and idempotency key management

### Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## Instructions

### Prerequisites

Before starting, ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)

### Starting the Project

1. **Clone or navigate to the project directory**:
   ```bash
   cd home-test/question_1
   ```

2. **Start all services using Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Verify the services are running**:
   - The API will be available at: `http://localhost:8000`
   - API documentation (Swagger UI): `http://localhost:8000/docs`
   - PostgreSQL: `localhost:5432`
   - Redis: `localhost:6379`

### Running in Detached Mode

To run the services in the background:

```bash
docker-compose up -d --build
```

### API Usage

Once the services are running, you can interact with the API:

1. **View API Documentation**: Navigate to `http://localhost:8000/docs` in your browser
2. **Create a Payment**: Use the `/payments` endpoint with a POST request
3. **Idempotency**: Include an `Idempotency-Key` header in your requests to ensure idempotent operations

Example request:
```bash
curl -X POST "http://localhost:8000/payments" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: <your-unique-key>" \
  -d '{
    "amount": 100.00
  }'
```

