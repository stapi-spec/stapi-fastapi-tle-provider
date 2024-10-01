from fastapi.testclient import TestClient
from pytest import fixture

from stapi_fastapi_tle.service.app import factory


@fixture
def client():
    app = factory()
    yield TestClient(app)
