from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from geojson_pydantic import FeatureCollection
from stapi_fastapi.api import StapiException, StapiRouter
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.shared import Link

from stapi_fastapi_tle.infrastructure.satellite import TleDefinedSatellite
from stapi_fastapi_tle.infrastructure.settings import TleSettings
from stapi_fastapi_tle.service.product import (
    PRODUCTS,
    OpportunityCollection,
    OpportunityRequest,
)


def tle_defined_satellite(settings: Annotated[TleSettings, Depends(TleSettings.load)]):
    """
    FastAPI dependency to load the TLE defined satellite provider infrastructure
    """
    return TleDefinedSatellite(settings.src)


class StapiTleRouter(StapiRouter):
    def __init__(self, **kwargs):
        super().__init__(None, **kwargs)

    async def search_opportunities(
        self,
        search: OpportunityRequest,
        satellite: Annotated[TleDefinedSatellite, Depends(tle_defined_satellite)],
    ) -> OpportunityCollection:
        passes = satellite.passes(
            search.datetime[0],
            search.datetime[1],
            search.geometry.coordinates[1],
            search.geometry.coordinates[0],
        )

        opportunity_model = next(
            p.opportunity_schema for p in PRODUCTS if p.product.id == search.product_id
        )

        opportunities = [
            opportunity_model(
                geometry=p[1].__geo_interface__,
                properties={
                    "datetime": [p[0].t, p[0].t],
                    "product_id": search.product_id,
                    "azimuth": p[0].azimuth,
                    "incidence": p[0].incidence,
                    "off_nadir": p[0].view_angles.off_nadir,
                    "sun_azimuth": p[0].sun_azimuth,
                    "sun_elevation": p[0].sun_elevation,
                },
            )
            for p in passes
        ]

        rv = JSONResponse(
            jsonable_encoder(
                FeatureCollection[opportunity_model](
                    type="FeatureCollection",
                    features=opportunities,
                )
            ),
            media_type=TYPE_GEOJSON,
        )
        return rv

    # product endpoints, these should be all just done in the StapiRouter class, here
    # just done to show "look, no backend!"
    def products(self, request: Request) -> ProductsCollection:
        products = [
            p.product.model_copy(
                update={
                    "links": [
                        Link(
                            href=str(
                                request.url_for(
                                    f"{self.NAME_PREFIX}:get-product",
                                    product_id=p.product.id,
                                )
                            ),
                            rel="self",
                            type=TYPE_JSON,
                        )
                    ]
                }
            )
            for p in PRODUCTS
        ]

        return ProductsCollection(
            products=[products],
            links=[
                Link(
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    def product(self, product_id: str, request: Request) -> Product:
        try:
            product = next(p.product for p in PRODUCTS if p.product.id == product_id)
        except StopIteration:
            raise StapiException(status.HTTP_404_NOT_FOUND, "product not found")
        return product.model_copy(
            update={
                "links": [
                    Link(
                        href=str(
                            request.url_for(
                                f"{self.NAME_PREFIX}:get-product",
                                product_id=product.id,
                            )
                        ),
                        rel="self",
                        type=TYPE_JSON,
                    )
                ]
            }
        )

    # order endpoints, just throwing errors
    async def create_order(
        self, search: OpportunityRequest, request: Request
    ) -> JSONResponse:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)

    async def get_order(self, order_id: str, request: Request) -> Order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
