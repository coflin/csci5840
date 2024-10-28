#!/usr/bin/python3

from loguru import logger
import csv

def sshInfo():
    try:
        csv_file = "/home/student/git/csci5840/scripts/sshInfo.csv"
        data = {}

        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                router_name = row["Routers"]
                router_data = {
                    "Device_Type": row["Device_Type"],
                    "IP": row["IP"],
                    "Username": row["Username"],
                    "Password": row["Password"] 
                }
                data[router_name] = router_data

        return data 

    except Exception as e:
        logger.error(f"Unable to open sshInfo.csv file: {e}")

if __name__ == "__main__":
    print(sshInfo())
