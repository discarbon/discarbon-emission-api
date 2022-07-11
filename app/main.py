from textwrap import dedent

from fastapi import FastAPI

import app.plane_emissions as plane_emissions

description = dedent(
    """disCarbon's carbon emission API currently allows clients to request
estimated emissions for plane travel."""
)

emission_api = FastAPI(
    title="disCarbon Carbon Emission API",
    description=description,
    version="0.0.1",
    contact={
        "name": "dan",
        "email": "danceratopz@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@emission_api.get("/emissions/travel/planeByIATA/{from_airport}/{to_airport}/{travel_class}")
async def plane_emissions_by_iata(
    from_airport: plane_emissions.IATACodes,
    to_airport: plane_emissions.IATACodes,
    travel_class: plane_emissions.PlaneTravelClasses,
):
    response = plane_emissions.calculate_emission(from_airport, to_airport, travel_class)
    return response


@emission_api.get("/emissions/travel/planeByCity/{from_city}/{to_city}/{travel_class}")
async def plane_emissions_by_city(
    from_city, to_city, travel_class: plane_emissions.PlaneTravelClasses
):
    response = plane_emissions.calculate_emission_from_city(from_city, to_city, travel_class)
    return response
