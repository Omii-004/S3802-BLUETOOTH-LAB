import serial
import time

ser = serial.Serial(
    port="COM5",
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=2
)

print("Connected to COM5")

tests = [
    b"ABC123",
    b"TEST-987654321",
    bytes([0x00, 0x01, 0x02, 0x03, 0xAA, 0x55]),
]

for data in tests:
    print("\nTX:", data)
    print("TX HEX:", data.hex())

    ser.reset_input_buffer()
    ser.write(data)
    ser.flush()

    time.sleep(1)

    response = ser.read(1024)

    if response:
        print("RX:", response)
        print("RX HEX:", response.hex())
    else:
        print("RX: <nothing>")

ser.close()