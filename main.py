from ThermalPrinter import ThermalPrinter
import struct

rawData = open("ThermalPrinter.py", "rb").read()        # Read the file as a binary
unpacked = struct.unpack('B' * len(rawData), rawData)   # Unpack it to a tuple of bytes
printer = ThermalPrinter("COM5", baud=115200)           # Declare the printer


def main():
    global unpacked
    global printer
    printer.initialize()                # Initialize printer
    printer.selectFontB()               # Select smaller font
    printer.addLineFeed()               # Add a smidgen of space
    printer.addRaw(b'\x1B\x33\x00')     # Set line spacing to zero (ESC 3 0)
    printer.flush()                     # Send that all to the printer

    createHeader(len(unpacked), "PRINTR")   # Create the header (length of file, and a name)

    while len(unpacked) % 6 != 0:       # Make sure file length is a multiple of 6
        unpacked += (0, )

    for ii in range(0, len(unpacked), 6):   # Create each line from the data
        ourSlice = unpacked[ii:ii+6]
        createLine(ourSlice)

    printer.flush()     # Send it to print!


def computeParity(num):
    parity = 0
    while(num != 0):
        if((num & 1) == 1):
            parity ^= 1
        num >>= 1
    return parity


def createHeader(dataLen, fName):
    global printer
    header = b''                                                # Temp object
    lenStr = format(dataLen, "048b")                            # The length field is 48 bits wide

    for char in lenStr:                                         # Replace the 0's and 1s with spaces and blocks
        header += b'\xDB' if char == '1' else b' '

    header += b'\xDF'                                           # Add clock track
    header += b'\xDB' if computeParity(dataLen) else b' '       # Add parity bit

    header += fName[0:6].encode('cp437')                        # Encode the tape name

    printer.addRaw(header)                                      # Append it to the buffer
    printer.addLineFeed()


def createLine(slice):
    global printer
    line = b''                                              # Temp object
    parity = 0                                              # No bits have been read, so null parity

    for byte in slice:                                      # For each byte in the line
        strByte = format(byte, "08b")                           # Get it as a string of 1s and 0s
        parity <<= 8                                            # Shift parity over 8
        parity += byte                                          # Add the new byte
        for char in strByte:                                    # Replace the 0's and 1s with spaces and blocks
            line += b'\xDB' if char == '1' else b' '

    line += b'\xDF'                                         # Add clock track
    line += b'\xDB' if computeParity(parity) else b' '      # Add parity bit

    for byte in slice:                                      # For each byte in the line
        if byte >= 32 and byte != 127:                          # If the byte isn't an ASCII control character
            line += byte.to_bytes(1, 'little')                      # Append the character representation
        else: line += b' '                                      # Otherwise, fill in a space.

    printer.addRaw(line)                                    # Append it to the printbuffer
    printer.addLineFeed()


if __name__ == "__main__":
    main()
