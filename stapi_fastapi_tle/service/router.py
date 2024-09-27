from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from stapi_fastapi.api import StapiException, StapiRouter
from stapi_fastapi.constants import TYPE_GEOJSON, TYPE_JSON
from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityCollection,
    OpportunityRequest,
)
from stapi_fastapi.models.order import Order
from stapi_fastapi.models.product import Product, ProductsCollection
from stapi_fastapi.models.shared import Link

from stapi_fastapi_tle.infrastructure.satellite import TleDefinedSatellite
from stapi_fastapi_tle.infrastructure.settings import TleSettings
from stapi_fastapi_tle.service.product import tle_product


def tle_defined_satellite(settings: Annotated[TleSettings, Depends(TleSettings.load)]):
    return TleDefinedSatellite(settings.src)


class StapiTleRouter(StapiRouter):
    def __init__(self):
        super().__init__(None, docs_endpoint_name="redoc_ui_html")

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

        opportunities = [
            Opportunity(
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

        return JSONResponse(
            jsonable_encoder(OpportunityCollection(features=opportunities)),
            media_type=TYPE_GEOJSON,
        )

    # product endpoints, these should be all just done in the StapiRouter class, here
    # just done to show "look, no backend!"
    def products(self, request: Request) -> ProductsCollection:
        tle_product.links.append(
            Link(
                href=str(
                    request.url_for(
                        f"{self.NAME_PREFIX}:get-product", product_id=tle_product.id
                    )
                ),
                rel="self",
                type=TYPE_JSON,
            )
        )
        return ProductsCollection(
            products=[tle_product],
            links=[
                Link(
                    href=str(request.url_for(f"{self.NAME_PREFIX}:list-products")),
                    rel="self",
                    type=TYPE_JSON,
                )
            ],
        )

    def product(self, product_id: str, request: Request) -> Product:
        if product_id != tle_product.id:
            raise StapiException(status.HTTP_404_NOT_FOUND, "product not found")
        tle_product.links.append(
            Link(
                href=str(
                    request.url_for(
                        f"{self.NAME_PREFIX}:get-product", product_id=tle_product.id
                    )
                ),
                rel="self",
                type=TYPE_JSON,
            )
        )
        return tle_product

    # order endpoints, just throwing errors
    async def create_order(
        self, search: OpportunityRequest, request: Request
    ) -> JSONResponse:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)

    async def get_order(self, order_id: str, request: Request) -> Order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
