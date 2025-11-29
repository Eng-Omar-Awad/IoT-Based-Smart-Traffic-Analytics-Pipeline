import csv
import random
from datetime import datetime
import os

# Locations list
LOCATIONS = ["Highway A1", "Highway A2", "City Center", "Airport Road", "Downtown"]


def simulate_traffic_record():
    """Generate one traffic sensor record."""
    vehicle_id = f"V{random.randint(100, 999)}"

    current_hour = datetime.now().hour
    # Rush hour: slower speeds
    if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
        speed = random.randint(0, 60)
    else:
        speed = random.randint(30, 140)

    location = random.choice(LOCATIONS)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "vehicle_id": vehicle_id,
        "speed": speed,
        "location": location,
        "timestamp": timestamp
    }


def generate_traffic_data(output_path: str, num_records: int = 20):
    """Generate multiple traffic records and save them into a CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    header = ["vehicle_id", "speed", "location", "timestamp"]

    # Append mode
    file_exists = os.path.isfile(output_path)

    with open(output_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=header)

        if not file_exists or os.path.getsize(output_path) == 0:
            writer.writeheader()

        for _ in range(num_records):
            record = simulate_traffic_record()
            writer.writerow(record)
            print(f"Logged: {record}")

    return output_path


if __name__ == "__main__":
    # Default execution (local)
    generate_traffic_data(output_path="data/raw/traffic_data.csv")
