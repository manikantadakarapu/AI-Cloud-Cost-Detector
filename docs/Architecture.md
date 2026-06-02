# AI Cost Detective Architecture

## Overview

AI Cost Detective is an Azure FinOps platform designed to discover Azure resources, collect cost and operational signals, evaluate optimization opportunities, and present actionable findings through a dashboard.

The current implementation provides the FastAPI backend foundation, PostgreSQL persistence, Azure SDK authentication, Azure subscription/resource group discovery, Azure Resource Graph resource discovery, SQLAlchemy models, Alembic migrations, centralized error handling, and structured logging.

Future phases will add a Next.js frontend, Azure Cost Management integration, Azure Advisor integration, Azure Monitor metrics, Redis-backed asynchronous processing, a FinOps rules engine, and an OpenAI-powered explanation layer.

## System Context

```mermaid
flowchart LR
    User[User / FinOps Engineer]
    Frontend[Next.js Frontend<br/>Future]
    Backend[FastAPI Backend<br/>Implemented Foundation]
    Postgres[(PostgreSQL)]
    ResourceGraph[Azure Resource Graph]
    CostMgmt[Azure Cost Management API<br/>Future]
    Advisor[Azure Advisor API<br/>Future]
    Monitor[Azure Monitor<br/>Future]
    Redis[Redis Queue<br/>Future]
    Worker[Analysis Worker<br/>Future]
    OpenAI[OpenAI Analysis Layer<br/>Future]

    User --> Frontend
    Frontend --> Backend
    Backend --> Postgres
    Backend --> ResourceGraph
    Backend --> CostMgmt
    Backend --> Advisor
    Backend --> Monitor
    Backend -. enqueue long-running jobs .-> Redis
    Redis -. process async analysis .-> Worker
    Worker -. writes results .-> Postgres
    Worker -. enrich findings .-> OpenAI
    Backend --> Frontend
```

## Backend Architecture

The backend follows a clean architecture style with clear boundaries between API routing, services, repositories, schemas, database models, and core infrastructure.

```mermaid
flowchart TB
    Routes[API Routes<br/>app/api/v1]
    Dependencies[Dependency Providers<br/>app/api/dependencies.py]
    Services[Application Services<br/>app/services]
    Repositories[Repositories<br/>app/repositories]
    Schemas[Pydantic Schemas<br/>app/schemas]
    Models[SQLAlchemy Models<br/>app/models]
    DB[Database Session<br/>app/db]
    Core[Core Config, Logging, Errors<br/>app/core]
    AzureAuth[Azure Credential Provider]
    AzureSDK[Azure SDK Clients]
    Postgres[(PostgreSQL)]

    Routes --> Dependencies
    Routes --> Schemas
    Dependencies --> Services
    Services --> Repositories
    Services --> AzureAuth
    AzureAuth --> AzureSDK
    Repositories --> Models
    Repositories --> DB
    DB --> Postgres
    Core --> Routes
    Core --> Services
```

## Current Backend Modules

| Layer | Path | Responsibility |
| --- | --- | --- |
| API | `backend/app/api/v1` | Versioned REST endpoints for subscriptions, resource groups, and analysis creation. |
| Dependencies | `backend/app/api/dependencies.py` | FastAPI dependency wiring for settings, database sessions, Azure services, and analysis service. |
| Core | `backend/app/core` | Application settings, structured logging, custom exceptions, and centralized exception handlers. |
| Database | `backend/app/db` | SQLAlchemy base model, engine, session factory, and request-scoped session dependency. |
| Models | `backend/app/models` | SQLAlchemy persistence models for `Analysis` and `Resource`. |
| Schemas | `backend/app/schemas` | Pydantic v2 request and response models. |
| Repositories | `backend/app/repositories` | Database write/read boundary for analyses and resources. |
| Services | `backend/app/services` | Azure authentication, Azure resource discovery, and analysis orchestration. |
| Migrations | `backend/alembic` | Alembic migration environment and initial schema. |

## Data Model

```mermaid
erDiagram
    ANALYSES ||--o{ RESOURCES : contains

    ANALYSES {
        uuid id PK
        string subscription_id
        string resource_group
        string status
        timestamptz created_at
        timestamptz updated_at
    }

    RESOURCES {
        uuid id PK
        uuid analysis_id FK
        text resource_id
        string name
        string type
        string location
        string sku
        jsonb tags
        timestamptz created_at
    }
```

## Azure Integration

The backend uses Azure SDKs exclusively. The current implementation includes:

- `DefaultAzureCredential` with service principal fallback support.
- `SubscriptionClient` for subscription discovery.
- `ResourceManagementClient` for resource group discovery.
- `ResourceGraphClient` for Azure resource discovery.

The platform is designed to expand with:

- Azure Cost Management API for cost and usage data.
- Azure Advisor API for optimization recommendations.
- Azure Monitor for utilization and performance metrics.

```mermaid
flowchart LR
    Backend[FastAPI Backend]
    Credential[Azure Credential Provider]
    SubClient[SubscriptionClient]
    RmClient[ResourceManagementClient]
    GraphClient[ResourceGraphClient]
    CostClient[Cost Management Client<br/>Future]
    AdvisorClient[Advisor Client<br/>Future]
    MonitorClient[Monitor Client<br/>Future]

    Backend --> Credential
    Credential --> SubClient
    Credential --> RmClient
    Credential --> GraphClient
    Credential -.-> CostClient
    Credential -.-> AdvisorClient
    Credential -.-> MonitorClient
```

## Planned Analysis Architecture

Prompt 2 and later phases should evolve the current synchronous request path into a durable analysis pipeline.

```mermaid
flowchart TB
    API[FastAPI API]
    Queue[Redis Queue<br/>Future]
    Worker[FinOps Analysis Worker<br/>Future]
    Resources[Resource Discovery]
    Costs[Cost Retrieval<br/>Future]
    Advisor[Advisor Retrieval<br/>Future]
    Metrics[Monitor Metrics Retrieval<br/>Future]
    Engine[FinOps Engine<br/>Future]
    AI[OpenAI Explanation Layer<br/>Future]
    DB[(PostgreSQL)]

    API --> DB
    API -. enqueue .-> Queue
    Queue -. consume .-> Worker
    Worker --> Resources
    Worker --> Costs
    Worker --> Advisor
    Worker --> Metrics
    Worker --> Engine
    Engine --> DB
    Engine -. enrich .-> AI
    AI -. explanations .-> DB
```

## Production Considerations

- Long-running Azure discovery and FinOps evaluation should move to Redis-backed workers.
- Analysis state should be persisted through each stage: created, discovering resources, retrieving costs, retrieving recommendations, retrieving metrics, evaluating, completed, and failed.
- Azure exceptions should be logged internally and sanitized before returning responses.
- Resource Graph queries should support paging and bounded result collection.
- PostgreSQL should enforce useful indexes and uniqueness constraints for analysis-resource relationships.
- Swagger/OpenAPI exposure should be configurable by environment.
- Future frontend authentication and authorization should protect all tenant/subscription data.


## Authentication

The platform is secured using Azure Entra ID (OIDC) through the OpenID Connect Authorization Code Flow. Access is managed through a JSON Web Token (JWT) provided by Azure Entra ID, ensuring no local passwords or standalone authentication systems are required. The FastAPI backend validates these tokens globally across all /api/v1 routes.

```mermaid
flowchart LR
    User[User / Client]
    Entra[Azure Entra ID]
    API[FastAPI Backend]
    Swagger[Swagger UI]

    User -->|Logs in| Entra
    Entra -->|Returns JWT| User
    User -->|Bearer Token| API
    Swagger -->|OAuth2 Flow| Entra
    API -->|Validates Token| API
```

## Authorization

Role-Based Access Control (RBAC) is implemented on top of the Authentication layer. Users are assigned one of three roles: `Admin`, `Analyst`, or `Viewer`.

```mermaid
flowchart LR
    API[FastAPI Endpoint]
    Auth[get_current_user]
    RBAC[require_permission]
    DB[(PostgreSQL)]

    API -->|Depends| Auth
    Auth -->|Loads User & Role| DB
    API -->|Depends| RBAC
    RBAC -->|Evaluates Role/Permission| API
    API -.->|403 Forbidden| Client
    API -.->|200 OK| Response
```

The authorization is evaluated per route using the `require_permission` dependency. Admin actions, role changes, and permission denials are audited using an internal `AuditService`.
