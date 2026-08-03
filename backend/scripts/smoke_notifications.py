"""Smoke test: escaneo compartido → notificación perito (API en vivo)."""
import io
import sys
import uuid

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


def _jpeg() -> bytes:
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd5\xff\xd9"
    )


def main() -> None:
    client = httpx.Client(base_url=BASE, timeout=30.0)

    admin = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "admin1234"})
    admin.raise_for_status()
    admin_token = admin.json()["access_token"]
    admin_h = {"Authorization": f"Bearer {admin_token}"}

    email = f"smoke_{uuid.uuid4().hex[:10]}@example.com"
    farmer = client.post(
        "/api/v1/auth/register",
        json={"name": "Smoke Farmer", "email": email, "password": "testpass1"},
    )
    farmer.raise_for_status()
    farmer_h = {"Authorization": f"Bearer {farmer.json()['access_token']}"}

    before = client.get("/api/v1/tech/notifications/unread-count", headers=admin_h)
    before.raise_for_status()
    pending_before = before.json()["pending_scans"]

    files = {"image": ("leaf.jpg", io.BytesIO(_jpeg()), "image/jpeg")}
    data = {
        "crop": "Tomate",
        "plague": "tuta absoluta",
        "severity": "Moderado",
        "confidence": "0.66",
        "share_with_tech": "true",
    }
    created = client.post("/api/v1/scans/with-image", headers=farmer_h, data=data, files=files)
    created.raise_for_status()
    scan_id = created.json()["id"]

    after = client.get("/api/v1/tech/notifications/unread-count", headers=admin_h)
    after.raise_for_status()
    body = after.json()
    assert body["pending_scans"] >= pending_before + 1, body
    assert body["unread_count"] >= 1, body

    notifs = client.get("/api/v1/tech/notifications?unread_only=true", headers=admin_h)
    notifs.raise_for_status()
    assert any(n["scan_id"] == scan_id for n in notifs.json()), notifs.json()

    print(f"OK smoke @ {BASE}: scan_id={scan_id}, pending={body['pending_scans']}, unread={body['unread_count']}")


if __name__ == "__main__":
    main()
