from textwrap import dedent

from fastapi import FastAPI

import app.plane_emissions as plane_emissions

description = dedent(
    """disCarbon's carbon emission estimation API.
       Currently, estimated emissions for plane travel are implemented.
    """
)

tags_metadata = [
    {"name": "Auxiliary", "description": "Auxiliary endpoints"},
    {
        "name": "Plane Emissions",
        "description": "Plane travel carbon emission estimates",
    },
]

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
    openapi_tags=tags_metadata,
)


@emission_api.get("/", tags=["Auxiliary"])
async def root():
    """
    Return a helpful docstring pointing to the API's Swagger documentation if no
    valid endpoint is provided.
    """
    return {
        "message": (
            """Welcome to the disCarbon flight and event emission API. Documentation is """
            """available at https://api.discarbon.earth/docs"""
        )
    }


# If we have dependencies on other services, consider https://github.com/Kludex/fastapi-health
@emission_api.get("/health", tags=["Auxiliary"])
async def app_health():
    """
    Basic health check to verify the API is still running.
    """
    return {"alive": True}


@emission_api.get(
    "/emissions/travel/supportedIATACodes",
    tags=["Plane Emissions"],
)
async def supported_iata_codes():
    """
    Return a list of supported airport IATA codes.
    """
    response = {"iata_codes": plane_emissions.IATA_CODES_LIST}
    return response


@emission_api.get(
    "/emissions/travel/planeByIATA/{from_airport}/{to_airport}/{travel_class}",
    response_model=plane_emissions.PlaneEmissionResponse,
    tags=["Plane Emissions"],
)
async def plane_emissions_by_iata(
    from_airport: plane_emissions.IATACodes,
    to_airport: plane_emissions.IATACodes,
    travel_class: plane_emissions.PlaneTravelClasses,
):
    """
    Estimate the carbon emissions for a single person flying between two airports
    as specified by IATA codes.

    The emission returned is for a one-way trip.

    Example: <a href="https://api.discarbon.earth/emissions/travel/planeByIATA/LAX/BOG/economy">
    LAX-BOG</a> - <br>
    <a href="https://api.discarbon.earth/emissions/travel/planeByIATA/LAX/BOG/economy">
    https://api.discarbon.earth/emissions/travel/planeByIATA/LAX/BOG/economy</a>

    See also: <br>
    <a href=
    "https://api.discarbon.api/docs#/supported_iata_codes_emissions_travel_supportedIATACodes_get">
    /emissions/travel/supportedIATACodes</a>
    """
    response = plane_emissions.calculate_emission_from_iata(from_airport, to_airport, travel_class)
    return response


@emission_api.get(
    "/emissions/travel/planeByCoordinates/{from_lat}/{from_lon}/{to_lat}/{to_lon}/{travel_class}",
    response_model=plane_emissions.PlaneEmissionResponse,
    tags=["Plane Emissions"],
)
async def plane_emissions_by_lat_lon_coordinates(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    travel_class: plane_emissions.PlaneTravelClasses,
):
    """
    Estimate the carbon emissions for a single person flying between two locations
    as specified by a decimal representation of its latitude and longitude coordinates.

    As long as an address can be determined from the coordinates, they are taken literally,
    i.e., it is not guaranteed that there is an airport located at the specified coordinates.
    If no address can be determined, then the 404 status code is returned.

    The emission returned is for a one-way trip.

    Example, from (57.15,2.11) to (47.37,8.54) (LAX-BOG) - <br>
    <a href=
    "https://api.discarbon.earth/emissions/travel/planeByCoordinates/33.94/-118.42/4.70/-74.15/economy">
    https://api.discarbon.earth/emissions/travel/planeByCoordinates/33.94/-118.42/4.70/-74.15/economy
    </a>
    """
    from_coords = plane_emissions.Coord(from_lat, from_lon)
    to_coords = plane_emissions.Coord(to_lat, to_lon)
    response = plane_emissions.calculate_emission_from_coordinates(
        from_coords, to_coords, travel_class
    )
    return response


@emission_api.get(
    "/emissions/travel/planeByCity/{from_city}/{to_city}/{travel_class}",
    response_model=plane_emissions.PlaneEmissionResponse,
    tags=["Plane Emissions"],
)
async def plane_emissions_by_city(
    from_city, to_city, travel_class: plane_emissions.PlaneTravelClasses
):
    """
    Estimate the carbon emissions for a single person flying between two airports
    as specified by a location string.

    The emission returned is for a one-way trip.

    If no address from the provided string can be determined, then the 404 status code
    is returned.

    Example: From "Los Angeles International Airport" to "El Dorado International Airport"
    (LAX-BOG) <br>
    <a href=
    "https://api.discarbon.earth/emissions/travel/planeByCity/Los%20Angeles%20International%20Airport/El%20Dorado%20International%20Airport/economy">
    https://api.discarbon.earth/emissions/travel/planeByCity/Los%20Angeles%20International%20Airport/El%20Dorado%20International%20Airport/economy
    </a>
    """
    response = plane_emissions.calculate_emission_from_city(from_city, to_city, travel_class)
    return response
