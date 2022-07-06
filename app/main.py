from fastapi import FastAPI
import app.emissions as emissions

description = """disCarbon's carbon emission API currently allows clients to request estimated emissions for plane travel."""

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
async def plane_emissions_by_iata(from_airport: str, to_airport: str, travel_class: emissions.PlaneTravelClasses):
    tco2 = emissions.flight_emission(from_airport, to_airport, travel_class)
    return {"emissions": tco2}
