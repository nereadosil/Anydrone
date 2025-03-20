import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('locations.db')
cursor = conn.cursor()

# Clear existing records
cursor.execute('DELETE FROM coordinates')

# Reset the auto-increment counter
cursor.execute('DELETE FROM sqlite_sequence WHERE name="coordinates"')

# Insert only the required locations
sample_data = [
    (42.1697, -8.6883),   # Vigo
    (44.7980, 20.4692),   # Belgrade
]

cursor.executemany('INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)', sample_data)

# Commit and close
conn.commit()
conn.close()

print("Database updated. Only the required locations remain.")
