# pip install sqlite3 in cmd
import sqlite3 

from geopy.geocoders import Nominatim

def get_location(latitude, longitude):
    geolocator = Nominatim(user_agent="geo_locator", timeout=10)  # Increase timeout to 10 seconds
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        return location.address if location else "Location not found"
    except Exception as e:
        return f"Error: {e}"

def fetch_coordinates_from_db():
    conn = sqlite3.connect('locations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT latitude, longitude FROM coordinates')
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_coordinates_to_db(latitude, longitude):
    conn = sqlite3.connect('locations.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)', (latitude, longitude))
    conn.commit()
    conn.close()
    print(f"Coordinates ({latitude}, {longitude}) saved successfully.")

if __name__ == "__main__":
    # Fetch and display existing coordinates
    coordinates = fetch_coordinates_from_db()
    if coordinates:
        print("\nExisting locations in database:")
        for lat, lon in coordinates:
            address = get_location(lat, lon)
            print(f"Coordinates: ({lat}, {lon}) -> Location: {address}")
    else:
        print("No locations found in the database.")

    # Allow user to input new coordinates
    while True:
        try:
            lat = float(input("\nEnter latitude (or type 'exit' to quit): "))
            lon = float(input("Enter longitude: "))
            address = get_location(lat, lon)
            print(f"Coordinates: ({lat}, {lon}) -> Location: {address}")

            # Save to database
            insert_coordinates_to_db(lat, lon)

        except ValueError:
            print("Invalid input. Please enter numerical values or type 'exit' to quit.")
            break
