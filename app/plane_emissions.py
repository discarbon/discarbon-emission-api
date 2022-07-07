"""
Estimate carbon emissions for air travel.
"""

import math
from enum import Enum
from collections import namedtuple
import pandas as pd
from geopy.geocoders import Nominatim

Coord = namedtuple('Coord', 'lat lon')

def load_airport_data(filename):
    airports = pd.read_csv(filename, header=0)
    airports = airports[airports["iata_code"].notnull()]
    airports = airports.query("(type in ['medium_airport', 'large_airport']) and (scheduled_service == 'yes')")
    return airports


AIRPORTS = load_airport_data("resources/airports.csv")
IATA_CODES_LIST = sorted([str(iata_code) for iata_code in AIRPORTS["iata_code"]])
# IATA_CODES_LIST = ["ZRH", "ABZ"]  # sorted([str(iata_code) for iata_code in AIRPORTS["iata_code"]])

# TODO: This is slow and perhaps stupid? But it does provide excellent error checking and doc.
IATACodes = Enum('IATACodes', dict(zip(IATA_CODES_LIST, IATA_CODES_LIST)), type=str)

class PlaneTravelClasses(str, Enum):
    """
    Enum class describing possible travel classes for plane travel.
    """
    economy = "economy"
    business = "business"
    first = "first"


def calculate_emission(from_airport, to_airport, travel_class):
    flight_distance = calculate_flight_distance(from_airport, to_airport)
    emission = calculate_carbon_emission(flight_distance, travel_class)
    response = {
        'from_airport': from_airport,
        'to_airport': to_airport,
        'flight_distance': flight_distance,
        'emission': emission
        }
    return response

def calculate_emission_from_city(from_city, to_city, travel_class):
    geolocator = Nominatim(user_agent="MyApp")
    from_location = geolocator.geocode(from_city)
    to_location = geolocator.geocode(to_city)
    from_coord = Coord(from_location.latitude, from_location.longitude)
    to_coord = Coord(to_location.latitude, to_location.longitude)
    flight_distance = calculate_geodesic_distance(from_coord, to_coord)
    emission = calculate_carbon_emission(flight_distance, travel_class)
    response = {
        'from_location': repr(from_location.address),
        'to_location': repr(to_location.address),
        'flight_distance': flight_distance,
        'emission': emission
        }
    return response



def calculate_flight_distance(from_airport, to_airport):
    """
    Get flight distance from the two airport input fields
    """
    from_location = AIRPORTS.query(f"iata_code == '{from_airport}'")[["latitude_deg", "longitude_deg"]]
    to_location = AIRPORTS.query(f"iata_code == '{to_airport}'")[["latitude_deg", "longitude_deg"]]

    from_coord = Coord(
        from_location.iloc[0]["latitude_deg"],
        from_location.iloc[0]["longitude_deg"]
        )
    to_coord = Coord(
        to_location.iloc[0]["latitude_deg"],
        to_location.iloc[0]["longitude_deg"]
        )

    return calculate_geodesic_distance(from_coord, to_coord)

def calculate_geodesic_distance(from_location, to_location):
    # Consider using geopy; https://stackoverflow.com/a/43211266
    earth_radius = 6371.009  # km mean earth radius (spherical approximation)

    from_coord = Coord(
        math.radians(from_location.lat),
        math.radians(from_location.lon)
        )
    to_coord = Coord(
        math.radians(to_location.lat),
        math.radians(to_location.lon)
        )

    delta_lambda = to_coord.lon - from_coord.lon

    A = (math.cos(to_coord.lat) * math.sin(delta_lambda))**2
    B = (math.cos(from_coord.lat) * math.sin(to_coord.lat) -
         math.sin(from_coord.lat) * math.cos(to_coord.lat) *
         math.cos(delta_lambda))**2
    C = (math.sin(from_coord.lat) * math.sin(to_coord.lat) +
         math.cos(from_coord.lat) * math.cos(to_coord.lat) *
         math.cos(delta_lambda))

    # Vyncenty formula
    delta_sigma = math.atan2(math.sqrt(A + B), C)
    distance = earth_radius * delta_sigma
    return distance

def calculate_carbon_emission(flight_distance: float, travel_class: PlaneTravelClasses):
    """
    Formula follows myclimate estimation calculator
    emission parameters (short distance)
    """
    if flight_distance == 0:
        # TODO error handling?
        return
    em_short = {
        'a': 0,
        'b': 2.714,
        'c': 1166.52,
        'S': 153.51,
        'PLF': 0.82,
        'DC': 95,
        'CF': 0.07,
        'CW': {
            'economy': 0.96,
            'business': 1.26,
            'first': 2.4
        },
        'EF': 3.15,
        'M': 2,
        'P': 0.54,
        'AF': 0.00038,
        'A': 11.68
    }
    # emission parameters (long distance)
    em_long = {
        'a': 0.0001,
        'b': 7.104,
        'c': 5044.93,
        'S': 280.21,
        'PLF': 0.82,
        'DC': 95,
        'CF': 0.23,
        'CW': {
            'economy': 0.8,
            'business': 1.54,
            'first': 2.4
        },
        'EF': 3.15,
        'M': 2,
        'P': 0.54,
        'AF': 0.00038,
        'A': 11.68
    }

    emission = 0
    if flight_distance < 1500:
        # short distance
        return single_emission_calc(em_short, flight_distance, travel_class)
    elif flight_distance > 2500:
        # long distance
        return single_emission_calc(em_long, flight_distance, travel_class)
    else:
        # intermediate distance (interpolation)
        short_emission = single_emission_calc(em_short, flight_distance, travel_class)
        long_emission = single_emission_calc(em_long, flight_distance, travel_class)
        long_dist_factor = (flight_distance - 1500) / 1000  # 0@1500km, 1@2500km
        emission = (1 - long_dist_factor) * short_emission + long_emission * long_dist_factor
    return emission


def single_emission_calc(em: dict, flight_distance: float, travel_class: PlaneTravelClasses):
    emission = 0
    d = flight_distance + em['DC']
    emission = ( ((em['a'] * d * d + em['b'] * d + em['c']) / (em['S'] * em['PLF'])) * (1 - em['CF']) *
                 em['CW'][travel_class] * (em['EF'] * em['M'] + em['P']) + em['AF'] * d + em['A'] )
    emission /= 1000  # from kg to tonnes
    return emission

if __name__ == "__main__":
    resp = calculate_emission("ZRH", "LAX",PlaneTravelClasses.economy)
    print(resp)
