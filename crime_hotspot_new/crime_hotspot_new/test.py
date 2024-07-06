import googlemaps

def get_route_coordinates(api_key, source, destination):
    gmaps = googlemaps.Client(key=api_key)
    directions = gmaps.directions(source, destination, mode="driving")

    if len(directions) == 0:
        print("No route found.")
        return

    route = directions[0]['legs'][0]['steps']
    coordinates = []

    for step in route:
        polyline = step['polyline']['points']
        decoded_polyline = googlemaps.convert.decode_polyline(polyline)
        for point in decoded_polyline:
            coordinates.append((point[0], point[1]))

    return coordinates

# Example usage
api_key = "AIzaSyDVktjjBzkWVn7sAO55StbkXS3L1cx-vjI"
source = "Palakkarai, Trichy"
destination = "Thillai Nagar, Trichy"
route_coordinates = get_route_coordinates(api_key, source, destination)

# Print the coordinates
for coordinate in route_coordinates:
    print(coordinate)
