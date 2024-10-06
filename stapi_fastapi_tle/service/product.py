"""
this file shows how to define products and their parameters first and then schema models
for fully OpenAPI typed endpoints.

Tried making it more reusable with pydantic's `create_model` method, but:
1. code became less readable
2. lost typing support for these dynamically created models (at least in VSCode)

Therefore showing the _explicit_ way here, even if the models feel anemic. Could write
an code generator for this chore.
"""

from dataclasses import dataclass
from typing import Annotated, Generic, Literal, Type, Union

from annotated_types import Ge, Le
from geojson_pydantic import Feature, FeatureCollection, Point, Polygon
from geojson_pydantic.features import Geom
from pydantic import BaseModel, ConfigDict
from stapi_fastapi.models.product import Product
from stapi_fastapi.types.datetime_interval import DatetimeInterval
from stapi_fastapi.types.filter import CQL2Filter


# Step 0a: define some mixins, should be moved to `stapi_fastapi` TODO
class OpportunityPropertiesMixin(BaseModel):
    datetime: DatetimeInterval


class OpportunityRequestGenericMixin(BaseModel):
    """
    base mixin allowing additional attributes for when no explicit OpenAPI is
    desired (maybe that shouldn't be a thing, but expect implementors to do the
    models? TODO).
    """

    filter: CQL2Filter | None = None

    model_config = ConfigDict(extra="allow")


class OpportunityRequestMixin(OpportunityRequestGenericMixin, Generic[Geom]):
    """
    base requiring being explicit.
    """

    geometry: Geom

    model_config = ConfigDict(extra="forbid")


# Step 0b: define a helper container to keep things tidy
@dataclass
class ProductSchema:
    product: Product
    opportunity_schema: Type[Feature]


# Step 1: For each product, define parameters model
class Product0Parameters(BaseModel):
    max_off_nadir: Annotated[float, Ge(0), Le(45)] = 30


class Product1Parameters(BaseModel):
    max_off_nadir: Annotated[float, Ge(0), Le(30)] = 15


# Step 2a: Define opportunity properties models for each product parameter model.
class Product0OpportunityProperties(Product0Parameters, OpportunityPropertiesMixin):
    product_id: Literal["tle1"] = "tle1"  # would be nice to enfore presence of this?


class Product1OpportunityProperties(Product1Parameters, OpportunityPropertiesMixin):
    product_id: Literal["tle2"] = "tle2"


# Step 2b: Define opportunity request model for each product parameter model; and their
# union
class Product0OpportunityRequest(
    Product0OpportunityProperties, OpportunityRequestMixin[Point]
):
    """"""


class Product1OpportunityRequest(
    Product1OpportunityProperties, OpportunityRequestMixin[Point]
):
    """"""


OpportunityRequest = Union[Product0OpportunityRequest, Product1OpportunityRequest]


# Step 2c: Define opportunity model for each product parameter model. Special trick: use
# additional attributes for the response vs request.
class Product0OpportunityResponseProperties(Product0OpportunityProperties):
    azimuth: float
    incidence: float
    off_nadir: float
    sun_azimuth: float
    sun_elevation: float


class Product0Opportunity(Feature[Polygon, Product0OpportunityResponseProperties]):
    type: Literal["Feature"] = "Feature"


class Product1OpportunityResponseProperties(Product1OpportunityProperties):
    azimuth: float
    incidence: float
    off_nadir: float
    sun_azimuth: float
    sun_elevation: float


class Product1Opportunity(Feature[Polygon, Product1OpportunityResponseProperties]):
    type: Literal["Feature"] = "Feature"


# Step 2d: Define opportunity collections union using all opportunity models
class Product0OpportunityCollection(FeatureCollection[Product0Opportunity]):
    """"""


class Product1OpportunityCollection(FeatureCollection[Product1Opportunity]):
    """"""


OpportunityCollection = Union[
    Product0OpportunityCollection,
    Product1OpportunityCollection,
]

# Step 3: Define products
PRODUCTS = (
    ProductSchema(
        product=Product(
            id="tle1",
            title="TLE defined satellite",
            license="",
            links=[],
            parameters=Product0Parameters,
        ),
        opportunity_schema=Product0Opportunity,
    ),
    ProductSchema(
        product=Product(
            id="tle2",
            title="Another TLE defined satellite",
            license="",
            links=[],
            parameters=Product1Parameters,
        ),
        opportunity_schema=Product1Opportunity,
    ),
)
