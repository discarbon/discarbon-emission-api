"""
Estimate carbon emissions.
"""

from enum import Enum

class PlaneTravelClasses(str, Enum):
    """
    Enum class describing possible travel classes for plane travel.
    """
    economy = "economy"
    business = "business"
    first = "first"


def flight_emission(from_airport, to_airport, travel_class):
    """
    Dummy function.
    """
    emissions = 1.23
    if travel_class.name == PlaneTravelClasses.business:
        emissions *= 2
    elif travel_class.name == PlaneTravelClasses.first:
        emissions *= 3
    return emissions