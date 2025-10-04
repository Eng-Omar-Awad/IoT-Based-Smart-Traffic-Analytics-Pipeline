import csv
import random
import time
from datetime import datetime

# Define locations
locations = ["Highway A1", "Highway A2", "City Center", "Airport Road", "Downtown"]

# Open CSV file in append mode
with open("traffic_data.csv", mode="a", newline="") as file:
    writer = csv.writer(file)

    # Write header if file is empty
    if file.tell() == 0:
        writer.writerow(["vehicle_id", "speed", "location", "timestamp"])

    # Simulate data every 5 seconds
    for i in range(20):  # generates 20 rows, change as needed
        vehicle_id = f"V{random.randint(100,999)}"
        speed = random.randint(0, 140)  # km/h
        location = random.choice(locations)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        writer.writerow([vehicle_id, speed, location, timestamp])
        print(f"Logged: {vehicle_id}, {speed}, {location}, {timestamp}")

        time.sleep(2.5)  # wait 5 seconds before next record

# Rush hour effect
hour = datetime.now().hour
if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
    speed = random.randint(0, 60)
else:
    speed = random.randint(30, 140)
