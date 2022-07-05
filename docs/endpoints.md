# Emission API Endpoint Specification

The disCarbon Emission API allows clients to retrieve emission estimates for travel, events and other specific activities.

The API will be available at:
`https://api.discarbon.earth/emissions/{version}/`

- `version`: The version of the API to use, e.g. `v1.1`

TODO: We could consider versioning by component, i.e., 
`https://api.discarbon.earth/emissions/travel/{version}/`
`https://api.discarbon.earth/emissions/event/{version}/`

## Travel Emission Estimates

Each GET request retrieves an emission estimate (in TCO2) for a *single* person travelling by the specified mode of transport.

### GET `travel/planeByIata/{from}/{to}/{class}`

Retrieve an emission estimate for a single person travelling by plane.

- `from`: The IATA code of the departure airport.
- `to`: The IATA code of the destination airport.
- `class`: The class travelled by the passenger. Must be one of `["economy", "business", "first"]`.  

### GET `travel/planeByCoordinates/{fromX}/{fromY}/{toX}/{toY}/{class}`

TODO: Add this endpoint to retrieve estimate specifying lat/long coordinates?

### GET `travel/planeByCity/{from}/{to}/{class}`

TODO: Add this endpoint to retrieve estimate specifying cities? Cities are ambiguous.

### GET `travel/trainByCoordinates/{fromX}/{fromY}/{toX}/{toY}/{class}`

Retrieve an emission estimate for a single person travelling by train.

- `fromX`: The lat coordinate of the departure station.
- `fromY`: The lon coordinate fo the departure station.
- `toX`: The lat coordinate of the destination station.
- `toY`: The lon coordinate of the destination station.
- `class`: The class travelled by the passenger. Must be one of `["second", "first"]`.


### GET `travel/busByCoordinates/{fromX}/{fromY}/{toX}/{toY}/{class}`

Retrieve an emission estimate for a single person travelling by bus.

Parameters as specified by train.

### GET `travel/carByCoordinates/{fromX}/{fromY}/{toX}/{toY}/{class}`

Retrieve an emission estimate for a single person travelling by car.

Parameters as specified by train.
- `num_passengers`: The number of passengers in the car.


## Event emissions

TODO

### GET `events/bbq/{numCarnivores}/{numVegetarians}`

Retrieve an emission estimate for a BBQ.

- `numCarnivores`: The number of meat-eating guests.
- `numVegetarians`: The number of vegetarian guests.

TODO: This makes it more easily extendable for new categories and is perhaps less error prone:
GET `events/bbq/{numCarnivores}`
GET `events/bbq/{numVegetarians}`
GET `events/bbq/{numCarbonConsciousShoppers}`

## Other Activities

TODO

TODO: Should these endpoints retrieve on a single person basis where possible (more consistent with travel endpoints).

