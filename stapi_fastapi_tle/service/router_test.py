from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from pytest import mark


@mark.parametrize("product_id", ("tle1", "tle2"))
def test_search_opportunities(client: TestClient, product_id: str):
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=7)

    rv = client.post(
        "/opportunities",
        json={
            "product_id": product_id,
            "datetime": f"{start.isoformat()}/{end.isoformat()}",
            "geometry": {
                "type": "Point",
                "coordinates": [0, 0],
            },
        },
    )

    assert (
        rv.status_code == 200
    ), f"unexpected status code {rv.status_code} with response: {rv.text}"
