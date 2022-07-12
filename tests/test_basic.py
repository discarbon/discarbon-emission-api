import pytest
from fastapi.testclient import TestClient

from app.main import emission_api

client = TestClient(emission_api)


def test_health():
    """
    Test health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"alive": True}


def test_plane_by_iata():
    """
    Test a valid planByIATA request.
    """
    from_airport = "LAX"
    to_airport = "BOG"
    endpoint = f"/emissions/travel/planeByIATA/{from_airport}/{to_airport}/economy"
    response = client.get(endpoint)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["from_iata"] == from_airport
    assert response_json["to_iata"] == to_airport
    assert response_json["emission"] == pytest.approx(0.908, 0.05)
    assert response_json["flight_distance"] == pytest.approx(5600, 1)


def test_plane_by_iata_invalid_iata_code():
    from_airport = "LAX"
    to_airport = "ZZZZ"  # invalid
    endpoint = f"/emissions/travel/planeByIATA/{from_airport}/{to_airport}/economy"
    response = client.get(endpoint)
    assert response.status_code == 422


def test_plane_by_iata_invalid_plane_travel_class_code():
    from_airport = "LAX"
    to_airport = "BOG"
    travel_class = "luxury"
    endpoint = f"/emissions/travel/planeByIATA/{from_airport}/{to_airport}/{travel_class}"
    response = client.get(endpoint)
    assert response.status_code == 422
