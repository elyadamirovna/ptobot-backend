"""Verify role-based access flow against the local FastAPI app."""
from __future__ import annotations

import io
import sys

sys.path.insert(0, ".")

from fastapi.testclient import TestClient

from app.api.deps import get_storage
from app.config import get_settings
from app.main import app


class FakeStorage:
    async def upload(self, file):  # pragma: no cover - helper script
        return f"https://example.test/{file.filename or 'photo.jpg'}"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(client: TestClient, phone: str, password: str = "demo") -> tuple[str, dict]:
    response = client.post(
        "/auth/login",
        json={"phone": phone, "password": password},
    )
    response.raise_for_status()
    body = response.json()
    return body["access_token"], body["user"]


def main() -> None:
    settings = get_settings()
    print(f"Database: {settings.database_url}")

    app.dependency_overrides[get_storage] = lambda: FakeStorage()
    client = TestClient(app)

    admin_token, admin_user = login(client, "+7 (900) 000-00-00")
    contractor_token, contractor_user = login(client, "+7 (900) 000-00-01")

    admin_sites = client.get("/sites", headers=bearer(admin_token))
    contractor_sites = client.get("/sites", headers=bearer(contractor_token))

    print("Admin:", admin_user)
    print("Admin sites:", admin_sites.json())
    print("Contractor:", contractor_user)
    print("Contractor sites:", contractor_sites.json())

    contractor_site_id = contractor_sites.json()[0]["id"]
    report_response = client.post(
        "/reports",
        headers=bearer(contractor_token),
        data={
            "site_id": contractor_site_id,
            "work_type_id": "1",
            "report_date": "2026-04-09",
            "description": "Тестовый отчет",
            "people": "4",
            "volume": "12",
            "machines": "1",
        },
        files={"photos": ("photo.jpg", io.BytesIO(b"fake-image"), "image/jpeg")},
    )
    print("Create report status:", report_response.status_code)
    print("Create report body:", report_response.json())

    forbidden_response = client.post(
        "/reports",
        headers=bearer(admin_token),
        data={
            "site_id": contractor_site_id,
            "work_type_id": "1",
            "report_date": "2026-04-09",
            "description": "Запрещенный отчет",
            "people": "1",
            "volume": "1",
            "machines": "0",
        },
        files={"photos": ("photo.jpg", io.BytesIO(b"fake-image"), "image/jpeg")},
    )
    print("Admin create report status:", forbidden_response.status_code)
    print("Admin create report body:", forbidden_response.json())


if __name__ == "__main__":
    main()
