from fastapi.testclient import TestClient

from main import APP

client = TestClient(APP)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>OpenBard - ReDoc</title>" in response.text
