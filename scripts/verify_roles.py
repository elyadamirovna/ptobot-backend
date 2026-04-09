"""Verify role-based access flow against the local FastAPI app.

The script no longer assumes that demo contractor users have assigned sites.
Instead, it:
1. logs in as admin,
2. fetches all sites,
3. finds a contractor with assigned sites in the current database,
4. logs in as that contractor,
5. verifies that the contractor sees only their own sites,
6. creates a report for one allowed site,
7. checks that admin cannot create reports.
"""
from __future__ import annotations

import io
import sys
from collections import defaultdict

sys.path.insert(0, ".")

from fastapi.testclient import TestClient

from app.api.deps import get_storage
from app.config import get_settings
from app.main import app
from app.infrastructure.database import SessionLocal
from app.infrastructure.users.models import UserModel


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


def assert_ok(response, action: str) -> list[dict] | dict:
    if response.status_code >= 400:
      raise RuntimeError(f"{action} failed: {response.status_code} {response.text}")
    return response.json()


def get_user_phone(user_id: str) -> str:
    session = SessionLocal()
    try:
        user = session.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise RuntimeError(f"User {user_id} not found in database")
        return user.phone
    finally:
        session.close()


def pick_assigned_contractor(admin_sites: list[dict]) -> tuple[str, str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for site in admin_sites:
        contractor_id = site.get("contractor_id")
        if contractor_id:
            grouped[contractor_id].append(site)

    if not grouped:
        raise RuntimeError(
            "No assigned contractor sites found in the current database. "
            "Assign at least one site to a contractor before running smoke verification."
        )

    contractor_id, contractor_sites = max(
        grouped.items(),
        key=lambda item: len(item[1]),
    )
    contractor_phone = get_user_phone(contractor_id)
    return contractor_id, contractor_phone, contractor_sites


def main() -> None:
    settings = get_settings()
    print(f"Database: {settings.database_url}")

    app.dependency_overrides[get_storage] = lambda: FakeStorage()
    client = TestClient(app)

    admin_token, admin_user = login(client, "+7 (900) 000-00-00")
    admin_sites_response = client.get("/sites", headers=bearer(admin_token))
    admin_sites = assert_ok(admin_sites_response, "admin /sites")

    contractor_id, contractor_phone, expected_contractor_sites = pick_assigned_contractor(admin_sites)
    contractor_token, contractor_user = login(client, contractor_phone)
    contractor_sites_response = client.get("/sites", headers=bearer(contractor_token))
    contractor_sites = assert_ok(contractor_sites_response, "contractor /sites")

    print("Admin:", admin_user)
    print("Admin sites count:", len(admin_sites))
    print("Picked contractor:", contractor_user)
    print("Picked contractor expected sites:", [site["id"] for site in expected_contractor_sites])
    print("Picked contractor actual sites:", [site["id"] for site in contractor_sites])

    expected_site_ids = {site["id"] for site in expected_contractor_sites}
    actual_site_ids = {site["id"] for site in contractor_sites}
    if contractor_user["id"] != contractor_id:
        raise RuntimeError(
            f"Picked contractor mismatch: expected id {contractor_id}, got {contractor_user['id']}"
        )
    if actual_site_ids != expected_site_ids:
        raise RuntimeError(
            f"Contractor /sites mismatch: expected {sorted(expected_site_ids)}, got {sorted(actual_site_ids)}"
        )

    contractor_site_id = contractor_sites[0]["id"]
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
    if report_response.status_code not in {200, 201}:
        raise RuntimeError(f"Contractor report creation failed: {report_response.status_code} {report_response.text}")

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
    if forbidden_response.status_code not in {403, 422}:
        raise RuntimeError(
            f"Unexpected admin report creation response: {forbidden_response.status_code} {forbidden_response.text}"
        )

    history_response = client.get(
        f"/sites/{contractor_site_id}/reports",
        headers=bearer(contractor_token),
    )
    history_items = assert_ok(history_response, "contractor site history")
    print("Contractor history count:", len(history_items))

    print("\nSmoke verification passed.")


if __name__ == "__main__":
    main()
