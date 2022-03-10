from ThermalPrinter import ThermalPrinter
import struct

rawData = open("Combat.A26", "rb").read()
unpacked = struct.unpack('B' * len(rawData), rawData)
printer = ThermalPrinter("COM5", baud=115200)


def main():
    global unpacked
    global printer
    printer.initialize()
    printer.selectFontB()
    printer.addLineFeed()
    printer.addRaw(b'\x1B\x33\x00')    # Set line spacing (ESC 3 60)
    printer.flush()

    createHeader(len(unpacked), "COMBAT")

    while len(unpacked) % 6 != 0:
        unpacked += (0, )

    for ii in range(0, len(unpacked), 6):
        ourSlice = unpacked[ii:ii+6]
        createLine(ourSlice)

    printer.flush()


def computeParity(num):
    parity = 0
    while(num != 0):
        if((num & 1) == 1):
            parity ^= 1
        num >>= 1
    return parity


def createHeader(dataLen, fName):
    global printer
    header = b''
    lenStr = format(dataLen, "048b")
    for char in lenStr:
        header += b'\xDB' if char == '1' else b' '
    header += b'\xDF'
    header += b'\xDB' if computeParity(dataLen) else b' '
    header += fName[0:6].encode('cp437')
    printer.addRaw(header)
    printer.addLineFeed()


def createLine(slice):
    global printer
    line = b''
    parity = 0

    for byte in slice:
        strByte = format(byte, "08b")
        parity <<= 8
        parity += byte
        for char in strByte:
            line += b'\xDB' if char == '1' else b' '

    line += b'\xDF'
    line += b'\xDB' if computeParity(parity) else b' '

    for byte in slice:
        if byte >= 32 and byte != 127:
            line += byte.to_bytes(1, 'little')

    printer.addRaw(line)
    printer.addLineFeed()


if __name__ == "__main__":
    main()
