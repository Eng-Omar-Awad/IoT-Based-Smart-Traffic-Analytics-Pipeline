from datetime import datetime
import random
import json
import os

# Try importing KafkaProducer; provide a graceful fallback when not installed
try:
    from kafka import KafkaProducer  # kafka-python package
    KAFKA_AVAILABLE = True
except Exception:
    KafkaProducer = None
    KAFKA_AVAILABLE = False

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "traffic_data"

# Locations list
LOCATIONS = ["Highway A1", "Highway A2", "City Center", "Airport Road", "Downtown"]

def simulate_traffic_record():
    vehicle_id = f"V{random.randint(100, 999)}"
    current_hour = datetime.now().hour

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

def produce_traffic_data(num_records=20):
    if KAFKA_AVAILABLE:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

            for _ in range(num_records):
                record = simulate_traffic_record()
                producer.send(TOPIC, value=record)
                print(f"Sent to Kafka: {record}")

            producer.flush()
            producer.close()
        except Exception as e:
            # Likely no brokers available (or other connection issue). Fall back to file output.
            print(f"⚠️ Kafka producer failed to connect ({e}). Falling back to JSONL output.")
            KAFKA_FALLBACK = True
        else:
            KAFKA_FALLBACK = False
    else:
        # Graceful fallback: write records to a local JSONL file so ETL can consume it
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw"))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "traffic_data_out.jsonl")
        print("⚠️ Kafka not available — writing simulated records to:", out_path)

        with open(out_path, "a", encoding="utf-8") as fh:
            for _ in range(num_records):
                record = simulate_traffic_record()
                fh.write(json.dumps(record) + "\n")
                print(f"Wrote record: {record}")
        return

    # If Kafka was available but failed to connect, run the same JSONL fallback
    if 'KAFKA_FALLBACK' in locals() and KAFKA_FALLBACK:
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Data", "raw"))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "traffic_data_out.jsonl")
        with open(out_path, "a", encoding="utf-8") as fh:
            for _ in range(num_records):
                record = simulate_traffic_record()
                fh.write(json.dumps(record) + "\n")
                print(f"Wrote record (fallback): {record}")

if __name__ == "__main__":
    produce_traffic_data()
