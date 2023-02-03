#!/usr/bin/python3 -u

# @file unlock_tool
# @author Frederich Stine
# @brief host tool for monitoring an unlock
# @date 2023
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!
#
# @copyright Copyright (c) 2023 The MITRE Corporation

import time
import argparse
import serial


# @brief Function to monitor unlocking car
# @param car_bridge, bridged serial connection to car
def unlock(serial_port):

    # Connect to car serial
    car_connection = serial.Serial(serial_port, 115200, timeout=1)
    car_connection.reset_input_buffer()

    # Begin time tracking
    delta_time = 0
    time_last = time.time()

    # Try to receive data while unlocking - if empty, unlock failed
    unlock_received: bytes = b""
    while True:
        try:
            # Update delta time
            new_time = time.time()
            delta_time += new_time - time_last
            time_last = new_time

            if (delta_time >= 5):
                # Exit loop after 5 seconds
                print("finished receiving")
                break

            # Read 1 byte from serial
            unlock_received += car_connection.read()
        except serial.SerialTimeoutException:
            print("Serial timeout - finished receiving")
            break

    # If no data receive, unlock failed
    if len(unlock_received) == 0:
        print("Failed to unlock")
    # If data received, print out unlock message and features
    else:
        print(unlock_received)

    return 0


# @brief Main function
#
# Main function handles parsing arguments and passing them to unlock
# function.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--car-bridge", help="Serial port for the car", required=True,
    )

    args = parser.parse_args()

    unlock(args.car_bridge)


if __name__ == "__main__":
    main()
