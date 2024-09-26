#!/bin/bash

DB_FILE="/var/log/netman/logs.db"

# Create the database and table if they don't exist
sqlite3 "$DB_FILE" <<EOF
CREATE TABLE IF NOT EXISTS snmp_traps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    host TEXT,
    interface TEXT,
    interface_status TEXT
);
EOF


/usr/bin/tcpdump -i any port 162 -l | while read -r line; do
    if echo "$line" | grep -q 'interfaces.ifTable.ifEntry.ifAdminStatus'; then
        TIMESTAMP=$(echo "$line" | awk '{print $1}')
        HOST=$(echo "$line" | awk '{print $5}' | cut -d '.' -f1-4)
        INTERFACE=$(echo "$line" | grep -oP 'interfaces.ifTable.ifEntry.ifDescr\.\d+=\K"[^"]+"' | tr -d '"')
        IF_ADMIN_STATUS=$(echo "$line" | grep -oP 'interfaces.ifTable.ifEntry.ifAdminStatus\.\d+=\K\d+')

        if [[ "$IF_ADMIN_STATUS" == "1" ]]; then
            STATUS="UP"  # Down
        else
            STATUS="DOWN"  # Up
        fi

        sqlite3 "$DB_FILE" <<EOF
INSERT INTO snmp_traps (timestamp, host, interface, interface_status)
VALUES ('$TIMESTAMP', '$HOST', '$INTERFACE', '$STATUS');
EOF

        # Optional: Log to the snmp_traps.log file
        echo "$line" >> /var/log/netman/snmp_traps.log
    fi
done

