from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    # Convert latitude and longitude from degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


namangan = (40.9983, 71.67257)
new_york = (40.7128, -74.0060)
moscow = (55.7558, 37.6176)
tashkent = (41.2995, 69.2401)

distances = {
    "Arabsiton": haversine(namangan[1], namangan[0], 45.0000, 24.0000),
    "Moscow": haversine(namangan[1], namangan[0], moscow[1], moscow[0]),
}

nearest_city = min(distances, key=distances.get)
print(nearest_city)
