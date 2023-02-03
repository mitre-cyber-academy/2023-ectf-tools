#!/usr/bin/python3 -u

# @file pair_tool
# @author Frederich Stine
# @brief host tool for pairing a new key fob
# @date 2023
#
# This source file is part of an example system for MITRE's 2023 Embedded
# CTF (eCTF). This code is being provided only for educational purposes for the
# 2023 MITRE eCTF competition, and may not meet MITRE standards for quality.
# Use this code at your own risk!
#
# @copyright Copyright (c) 2023 The MITRE Corporation

import serial
import argparse


# @brief Function to send commands to pair
# a new fob.
# @param unpairmed_fob_bridge, bridged serial connection to unpairmed fob
# @param pairmed_fob_bridge, bridged serial connection to pairmed fob
# @param pair_pin, pin used to pair a new fob
def pair(unpaired_fob_bridge, paired_fob_bridge, pair_pin):

    # Connect to both serial ports
    unpaired_connection = serial.Serial(unpaired_fob_bridge, 115200, timeout=5)
    unpaired_connection.reset_input_buffer()

    paired_connection = serial.Serial(paired_fob_bridge, 115200, timeout=5)
    paired_connection.reset_input_buffer()

    # Send pair commands to both fobs
    unpaired_connection.write(b"pair\n")
    paired_connection.write(b"pair\n")

    # Send pin to the paired fob
    pair_pin_bytes = str.encode(pair_pin + "\n")
    paired_connection.write(pair_pin_bytes)

    # Try to receive data - if failed, pairing failed
    try:
        pair_success = unpaired_connection.read(6)
        while len(pair_success) != 6:
            pair_success += unpaired_connection.read(6 - len(pair_success))

        print(pair_success)
    except serial.SerialTimeoutException:
        print("Failed to pair fob")

    return 0


# @brief Main function
#
# Main function handles parsing arguments and passing them to pair
# function.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--unpaired-fob-bridge",
        help="Serial port for the unpaired fob",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--paired-fob-bridge",
        help="Serial port for the paired fob",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--pair-pin", help="Program PIN", type=str, required=True,
    )

    args = parser.parse_args()

    pair(args.unpaired_fob_bridge, args.paired_fob_bridge, args.pair_pin)


if __name__ == "__main__":
    main()
