from pydantic import ConfigDict
from stapi_fastapi.models.constraints import Constraints as BaseConstraints
from stapi_fastapi.models.product import Product


class TleConstraints(BaseConstraints):
    model_config = ConfigDict(extra="forbid")


tle_product = Product(id="tle", license="public", parameters=TleConstraints, links=[])
