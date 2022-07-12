"""
Estimate carbon emissions for air travel.
"""

import math
from collections import namedtuple
from enum import Enum
from typing import List, Union

import pandas as pd
from fastapi import HTTPException
from geopy.geocoders import Nominatim
from pydantic import BaseModel

Coord = namedtuple("Coord", "lat lon")


def load_airport_data(filename):
    airports = pd.read_csv(filename, header=0)
    airports = airports[airports["iata_code"].notnull()]
    airports.query(
        "(type in ['medium_airport', 'large_airport']) and (scheduled_service == 'yes')",
        inplace=True,
    )
    return airports


AIRPORTS = load_airport_data("resources/airports.csv")
IATA_CODES_LIST = sorted([str(iata_code) for iata_code in AIRPORTS["iata_code"]])
# Note: This takes a few seconds.
IATACodes = Enum("IATACodes", dict(zip(IATA_CODES_LIST, IATA_CODES_LIST)), type=str)

geolocator = Nominatim(user_agent="MyApp")


class PlaneTravelClasses(str, Enum):
    """
    Enum class describing possible travel classes for plane travel.
    """

    economy = "economy"
    business = "business"
    first = "first"


class PlaneEmissionResponse(BaseModel):
    from_coords: List[float] = []
    to_coords: List[float] = []
    from_location: str
    to_location: str
    from_iata: Union[IATACodes, None] = None
    to_iata: Union[IATACodes, None] = None
    travel_class: PlaneTravelClasses
    flight_distance: float
    emission: float


class PlaneTravel:
    def __init__(self, from_coords: Coord, to_coords: Coord, travel_class: PlaneTravelClasses):
        self.from_coords = from_coords
        self.to_coords = to_coords
        self.travel_class = travel_class

    def calculate_geodesic_distance(self):
        # Consider using geopy; https://stackoverflow.com/a/43211266
        earth_radius = 6371.009  # km mean earth radius (spherical approximation)

        from_coord = Coord(math.radians(self.from_coords.lat), math.radians(self.from_coords.lon))
        to_coord = Coord(math.radians(self.to_coords.lat), math.radians(self.to_coords.lon))

        delta_lambda = to_coord.lon - from_coord.lon

        A = (math.cos(to_coord.lat) * math.sin(delta_lambda)) ** 2
        B = (
            math.cos(from_coord.lat) * math.sin(to_coord.lat)
            - math.sin(from_coord.lat) * math.cos(to_coord.lat) * math.cos(delta_lambda)
        ) ** 2
        C = math.sin(from_coord.lat) * math.sin(to_coord.lat) + math.cos(from_coord.lat) * math.cos(
            to_coord.lat
        ) * math.cos(delta_lambda)

        # Vyncenty's formula
        delta_sigma = math.atan2(math.sqrt(A + B), C)
        self.flight_distance = earth_radius * delta_sigma
        return self.flight_distance

    def calculate_carbon_emission(self):
        """
        Formula follows myClimate estimation calculator
        emission parameters (short distance)
        """
        if self.flight_distance == 0:
            # TODO error handling?
            return
        em_short = {
            "a": 0,
            "b": 2.714,
            "c": 1166.52,
            "S": 153.51,
            "PLF": 0.82,
            "DC": 95,
            "CF": 0.07,
            "CW": {"economy": 0.96, "business": 1.26, "first": 2.4},
            "EF": 3.15,
            "M": 2,
            "P": 0.54,
            "AF": 0.00038,
            "A": 11.68,
        }
        # emission parameters (long distance)
        em_long = {
            "a": 0.0001,
            "b": 7.104,
            "c": 5044.93,
            "S": 280.21,
            "PLF": 0.82,
            "DC": 95,
            "CF": 0.23,
            "CW": {"economy": 0.8, "business": 1.54, "first": 2.4},
            "EF": 3.15,
            "M": 2,
            "P": 0.54,
            "AF": 0.00038,
            "A": 11.68,
        }

        emission = 0
        if self.flight_distance < 1500:
            # short distance
            self.emission = self.single_emission_calc(em_short)
            return self.emission
        elif self.flight_distance > 2500:
            # long distance
            self.emission = self.single_emission_calc(em_long)
            return self.emission
        else:
            # intermediate distance (interpolation)
            short_emission = self.single_emission_calc(em_short)
            long_emission = self.single_emission_calc(em_long)
            long_dist_factor = (self.flight_distance - 1500) / 1000  # 0@1500km, 1@2500km
            emission = (1 - long_dist_factor) * short_emission + long_emission * long_dist_factor
        self.emission = emission
        return self.emission

    def single_emission_calc(self, em: dict):
        emission = 0
        d = self.flight_distance + em["DC"]
        emission = (
            ((em["a"] * d * d + em["b"] * d + em["c"]) / (em["S"] * em["PLF"]))
            * (1 - em["CF"])
            * em["CW"][self.travel_class]
            * (em["EF"] * em["M"] + em["P"])
            + em["AF"] * d
            + em["A"]
        )
        emission /= 1000  # from kg to tonnes
        return emission


def get_coords_from_iata(airport_iata_code):
    """
    Get the latitudinal and longitudinal coordinates for the airport specified by
    provided IATA code.
    """
    coords = AIRPORTS.query(f"iata_code == '{airport_iata_code}'")[
        ["latitude_deg", "longitude_deg"]
    ]
    return Coord(coords.iloc[0]["latitude_deg"], coords.iloc[0]["longitude_deg"])


def calculate_emission_from_iata(
    from_iata: IATACodes, to_iata: IATACodes, travel_class: PlaneTravelClasses
):
    from_coords = get_coords_from_iata(from_iata)
    to_coords = get_coords_from_iata(to_iata)
    plane_travel = PlaneTravel(from_coords, to_coords, travel_class)
    plane_travel.calculate_geodesic_distance()
    plane_travel.calculate_carbon_emission()
    # complete the response
    from_location = geolocator.reverse(f"{from_coords.lat}, {from_coords.lon}").address
    to_location = geolocator.reverse(f"{to_coords.lat}, {to_coords.lon}").address
    response = {
        "from_iata": from_iata,
        "to_iata": to_iata,
        "from_coords": from_coords,
        "to_coords": to_coords,
        "from_location": from_location,
        "to_location": to_location,
        "travel_class": plane_travel.travel_class,
        "flight_distance": plane_travel.flight_distance,
        "emission": plane_travel.emission,
    }
    return response


def calculate_emission_from_coordinates(from_coords, to_coords, travel_class):
    plane_travel = PlaneTravel(from_coords, to_coords, travel_class)
    plane_travel.calculate_geodesic_distance()
    plane_travel.calculate_carbon_emission()
    # complete the response
    from_location = geolocator.reverse(f"{from_coords.lat}, {from_coords.lon}")
    if not from_location:
        raise HTTPException(
            status_code=404,
            detail=f"no address could be determined from the from_coords '{from_coords}'",
        )
    to_location = geolocator.reverse(f"{to_coords.lat}, {to_coords.lon}")
    if not to_location:
        raise HTTPException(
            status_code=404,
            detail=f"no address could be determined from the to_coords '{to_coords}'",
        )
    response = {
        "from_coords": from_coords,
        "to_coords": to_coords,
        "from_location": from_location.address,
        "to_location": to_location.address,
        "travel_class": plane_travel.travel_class,
        "flight_distance": plane_travel.flight_distance,
        "emission": plane_travel.emission,
    }
    return response


def calculate_emission_from_city(from_city, to_city, travel_class):
    from_location = geolocator.geocode(from_city)
    if not from_location:
        raise HTTPException(status_code=404, detail=f"from_city '{from_city}' not found")
    to_location = geolocator.geocode(to_city)
    if not to_location:
        raise HTTPException(status_code=404, detail=f"to_city '{to_city}' not found")
    from_coords = Coord(from_location.latitude, from_location.longitude)
    to_coords = Coord(to_location.latitude, to_location.longitude)
    plane_travel = PlaneTravel(from_coords, to_coords, travel_class)
    plane_travel.calculate_geodesic_distance()
    plane_travel.calculate_carbon_emission()
    response = {
        "from_coords": from_coords,
        "to_coords": to_coords,
        "from_location": from_location.address,
        "to_location": to_location.address,
        "travel_class": plane_travel.travel_class,
        "flight_distance": plane_travel.flight_distance,
        "emission": plane_travel.emission,
    }
    return response


if __name__ == "__main__":

    resp = calculate_emission_from_iata("ZRH", "LAX", PlaneTravelClasses.economy)
    print(resp)
