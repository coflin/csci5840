#!/bin/bash

COMMUNITY="public"
OID="1.3.6.1.2.1.25.3.3.1.2"
LOG_FILE="/var/log/netman/cpu_utilization.log"
DB_FILE="/var/log/netman/logs.db"
HOSTS=(
    "192.168.100.5"
    "192.168.100.6"
    "192.168.100.3"
    "192.168.100.4"
    "192.168.100.7"
    "192.168.100.8"
)
INTERVAL=300  # Interval in seconds

# Create the database and table if they don't exist
sqlite3 "$DB_FILE" <<EOF
CREATE TABLE IF NOT EXISTS cpu_utilization (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    utilization REAL NOT NULL
);
EOF

echo "-----------------------------------------------------------" >> "$LOG_FILE"
echo "CPU Utilization Monitoring - $(date)" >> "$LOG_FILE"
echo "-----------------------------------------------------------" >> "$LOG_FILE"

while true; do
    for HOST in "${HOSTS[@]}"; do
        echo "Fetching CPU utilization for $HOST..."
        
        OUTPUT=$(snmpwalk -v2c -c "$COMMUNITY" "$HOST" "$OID" 2>/dev/null)
        
        if [ $? -ne 0 ]; then
            echo "Failed to retrieve data from $HOST" >> "$LOG_FILE"
        else
            echo "****$HOST****" >> "$LOG_FILE"
            
            # Extract utilization values and calculate the average
            UTILIZATIONS=($(echo "$OUTPUT" | awk -F'INTEGER: ' '{print $2}'))
            TOTAL=0
            COUNT=0
            
            for VALUE in "${UTILIZATIONS[@]}"; do
                TOTAL=$((TOTAL + VALUE))
                COUNT=$((COUNT + 1))
            done
            
            if [ "$COUNT" -ne 0 ]; then
                AVERAGE=$(echo "scale=2; $TOTAL / $COUNT" | bc)
            else
                AVERAGE=0
            fi
            
            TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
            echo "$TIMESTAMP - Average CPU Utilization: $AVERAGE%" >> "$LOG_FILE"
            
            # Insert the average utilization into the SQLite database
            sqlite3 "$DB_FILE" <<EOF
            INSERT INTO cpu_utilization (host, timestamp, utilization) 
            VALUES ('$HOST', '$TIMESTAMP', $AVERAGE);
EOF
        fi
        echo "" >> "$LOG_FILE"
    done
    sleep "$INTERVAL"
done

