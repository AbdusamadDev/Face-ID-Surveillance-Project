from math import radians, sin, cos, sqrt, atan2


def haversine_distance(coord1, coord2):
    R = 6371  # Radius of the Earth in km

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Example usage:
locations = [
    (40.7128, -74.0060),  # New York
    (34.0522, -118.2437),  # Los Angeles
    (41.8781, -87.6298),  # Chicago
]

reference_location = (37.7749, -122.4194)  # San Francisco

# Find the nearest location
nearest_location = min(
    locations, key=lambda x: haversine_distance(x, reference_location)
)
print(f"The nearest location to the reference is {nearest_location}")
