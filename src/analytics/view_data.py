import sqlite3

# Connect to the database
conn = sqlite3.connect("traffic.db")
cursor = conn.cursor()

# Select first 10 rows
cursor.execute("SELECT * FROM traffic_data LIMIT 10;")
rows = cursor.fetchall()

# Print the results
print("=== First 10 records in traffic_data ===")
for row in rows:
    print(row)

# Close the connection
conn.close()