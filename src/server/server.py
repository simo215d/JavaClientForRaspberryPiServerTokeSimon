import time
import board
import adafruit_dht
import socket
import time

#Server IP and port used
HOST = "192.168.0.114"
PORT = 8000

#Container from sensor reads
temperature_c=0
humidity=0

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT11(board.D4, use_pulseio=False)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Server socket created')

try:
    sock.bind((HOST, PORT))
except socket.error as err:
    print('Bind failed. Error Code : '.format(err))
sock.listen(10)
print("Waiting for client to connect")
clientSocket, address = sock.accept()
print("Client connected:")
print(address)

#Loop to keep the server connection alive
while True:

    try:
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        #print(
        #    "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
        #        temperature_f, temperature_c, humidity
        #    )
        #)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)

    message = "T{}M{}\n".format(temperature_c, humidity)
    clientSocket.sendto(message.encode(),(HOST, PORT))
    print("message sent!")
    time.sleep(5)