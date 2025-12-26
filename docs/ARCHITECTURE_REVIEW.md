# Backend Architecture Review

## Overview
This document summarizes observed architectural issues in the current backend and proposes a more modular, resilient design. The goal is to improve reliability, performance, security, and maintainability while enabling future extensions (e.g., persistent storage, richer domain logic, and observability).

## Observed Issues
- **In-memory persistence only**: Report and work type repositories store data in memory, so data is lost on restart and the API cannot scale horizontally. Filtering is done in Python after loading the full deque, which limits performance.
- **Blocking I/O inside async flow**: `StorageService.upload_to_yandex` calls the synchronous boto3 client directly inside an async endpoint. During uploads, the event loop will be blocked, reducing concurrency. There is no timeout or retry policy for storage operations.
- **Mixed concerns in dependency wiring**: `app/api/deps.py` constructs concrete implementations directly and caches them globally. This prevents per-request scoping for objects that should be short-lived (e.g., DB sessions) and couples the API to implementation details.
- **Validation gaps**: Pydantic schemas (`ReportOut`, `WorkTypeOut`, `RootInfo`) are used both as response models and internal entities. There are no input schemas for incoming report creation, so field constraints, required lists, and size limits are not enforced. `photos` is required but not validated for count, size, or content type.
- **Domain leakage into infrastructure**: The `ReportService` mixes domain logic (ID generation, timestamps) with infrastructure-specific storage uploads. This coupling makes it hard to swap storage backends or to test logic without hitting Yandex Object Storage.
- **ID handling inconsistencies**: `ReportRepository.next_id()` increments an integer, but `ReportOut.work_type_id` is coerced to `str`, creating inconsistent typing across the API. Filtering uses string equality, which may mismatch if callers send integers.
- **Logging and observability gaps**: The project uses only basic logging without structured fields, correlation IDs, or request/response logging. Storage operations lack diagnostics and metrics.
- **Configuration rigidity**: Settings are simple attributes without validation or defaults. Credentials are optional, but missing values are not checked before attempting uploads, leading to runtime failures.
- **Testability concerns**: Heavy use of singletons via `@lru_cache` and direct construction of boto3 clients makes unit testing difficult. There are no interfaces for storage lifecycles to allow mocking.

## Recommended Architecture
- **Layered modules**: Separate domain models (entities/value objects), DTOs (request/response schemas), application services (use cases), infrastructure adapters (DB, storage), and API composition. Keep dependency direction inward (API -> application -> domain -> infrastructure via interfaces).
- **Persistent storage**: Introduce a database-backed repository (e.g., PostgreSQL via async SQLAlchemy) for reports and work types. Define repository interfaces in a dedicated `app/domain/ports` module with async methods. Use connection pooling and per-request session scopes.
- **Async-safe I/O**: Wrap blocking storage calls in `asyncio.to_thread` or use an async-capable S3 client (e.g., aioboto3). Add retry/backoff and timeouts for uploads. Stream large file uploads instead of loading them fully into memory.
- **Input/Output schemas**: Create separate Pydantic models for input (e.g., `ReportCreate`) and output (`ReportRead`). Apply field constraints (lengths, enumerations, minimum counts), and validate `photos` for allowed MIME types and size limits. Provide consistent typing for IDs (UUIDs or integers) throughout the API and database.
- **Service boundaries**: Keep `ReportService` focused on orchestration by depending on interfaces (`ReportRepository`, `StoragePort`, `Clock`). Move storage-specific logic to an adapter (e.g., `YandexStorage`). Generate IDs at the repository/database level and expose timestamps from a clock abstraction for deterministic tests.
- **Dependency injection**: Replace global `@lru_cache` factories with a lightweight DI container or FastAPI dependencies that yield per-request resources (e.g., `get_db_session`). Use startup/shutdown events to initialize shared resources like S3 clients while keeping them injectable for tests.
- **Configuration management**: Use `pydantic-settings` to validate environment variables and provide clear error messages when required secrets are missing. Group settings by concern (app, storage, database, CORS).
- **Observability**: Introduce structured logging (JSON), request IDs, and middleware for HTTP access logs. Add metrics (e.g., Prometheus) for request latency and upload durations. Centralize logging configuration per module and environment.
- **Testing strategy**: Add unit tests for services using mocked ports, and integration tests for API endpoints with a temporary database. Provide factory fixtures for repositories and storage adapters.

## Suggested File/Directory Restructuring
- `app/domain/` — Entities, value objects, and domain services (pure business rules).
- `app/domain/ports/` — Interfaces for repositories, storage, and clock abstractions.
- `app/application/` — Use-case services (e.g., `ReportService`) orchestrating domain and ports.
- `app/infrastructure/` — Adapters for database repositories, S3 storage, and logging configuration.
- `app/api/` — FastAPI routers, request/response schemas, and dependency wiring using DI-friendly factories.
- `app/config/` — Strongly validated settings (via `pydantic-settings`) with separate modules for app, storage, and database.
- `tests/` — Unit and integration tests.

## Concrete Refactoring Steps
1. **Introduce validated settings**: Replace `Settings` with a `BaseSettings`-derived class in `app/config/settings.py`, splitting sections for app, storage, and database. Fail fast when required secrets are missing.
2. **Define ports and schemas**:
   - Add `app/domain/ports/report_repo.py` with async `add`, `list`, and `get_next_id` methods.
   - Add `app/domain/ports/storage.py` with `async upload(file: UploadFile) -> str`.
   - Add request/response schemas in `app/api/schemas/report.py` (`ReportCreate`, `ReportRead`) and `work_type.py` (`WorkTypeRead`).
3. **Implement infrastructure adapters**:
   - Create `app/infrastructure/storage/yandex.py` that wraps boto3 calls via `asyncio.to_thread` and includes retries/timeouts.
   - Add a database-backed `ReportRepository` using async SQLAlchemy, handling filtering in SQL and returning DTOs.
   - Provide an in-memory repository only for tests/dev in `app/infrastructure/repositories/memory.py`.
4. **Refactor services**:
   - Move `ReportService` to `app/application/report_service.py` to orchestrate port interfaces, generate timestamps via a clock port, and enforce input validation.
   - Keep file upload logic in the storage adapter; keep ID generation in the repository/database layer.
5. **Dependency wiring**:
   - Use FastAPI dependencies to yield per-request DB sessions (`async_sessionmaker`).
   - Register adapters in `app/api/deps.py` with clear lifetimes and avoid global caches; use startup to initialize shared pools.
6. **Observability and logging**:
   - Add logging config that supports structured output and request logging middleware.
   - Instrument storage and database operations with metrics and spans (e.g., OpenTelemetry).
7. **Testing**:
   - Add unit tests for services with mocked ports.
   - Add API tests using FastAPI `TestClient` and a temporary database; cover upload flow with a fake storage adapter.

Implementing these changes will produce a modular, testable backend that can scale, provide stronger guarantees around data persistence and resource usage, and support future features with minimal coupling.

## Implemented Changes (current iteration)
- Added validated configuration via `pydantic-settings` with bucket/credential checks and CORS parsing.
- Introduced domain entities and ports for reports, work types, storage, and clocks with async-friendly contracts.
- Refactored application services to consume DTOs and ports, isolating storage uploads from orchestration logic.
- Added async-safe in-memory repositories for development with ID generation locking.
- Replaced storage integration with an async-friendly Yandex adapter that wraps boto3 in `asyncio.to_thread` and uses retries/timeouts.
- Restructured FastAPI dependencies around a lightweight container initialized in the app lifespan instead of global singletons.
- Separated API schemas for input/output with validation helpers for multipart form submissions.
