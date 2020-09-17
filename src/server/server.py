import time
import board
import adafruit_dht
import socket
import threading
import base64
import hashlib
from Crypto.Cipher import AES

#AES block size 
BLOCK_SIZE=16
key="Just a key123456"
IV="Just an IV123456"

#encrypt function
def encrypt(msg):
    cipher = AES.new(key, AES.MODE_CBC, IV)
    return cipher.encrypt(msg)
    return base64.b64encode(cipher.encrypt(msg))

#decrypt function
def decrypt(msg):
    cipher = AES.new(key, AES.MODE_CBC, IV)
    #return cipher.decrypt(msg)
    return base64.b64decode(cipher.decrypt(msg))

def setFixedStringLength(msg):
    newmsg=msg
    msglength=len(msg)
    msgex=msglength%BLOCK_SIZE
    for i in range(0,msgex):
        newmsg+=" "
    return newmsg

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket=clientsocket
        print("New connection: ",clientAddress)
    def run(self):
        connLoop=True
        #Loop to keep the server connection alive
        while connLoop:

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

            message = "T{}M{}          ".format(temperature_c, humidity)
            print(message)
            cryptmsg=encrypt(message.encode("utf-8"))
            print(cryptmsg)
            try:
                self.csocket.sendto(cryptmsg,(HOST, PORT))
                self.csocket.sendto("\n".encode("utf-8"),(HOST, PORT))
                print("message sent!")
            except self.csocket.error:
                print("Client have disconnected")
                connLoop=False
            time.sleep(5)
        

#Server IP and port used
HOST = "192.168.0.114"
PORT = 8080

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
#sock.listen(10)
#print("Waiting for client to connect")
#clientSocket, address = sock.accept()
#print("Client connected:")
#print(address)

while True:
    sock.listen(1)
    clientsock, clientAddress=sock.accept()
    nThread=ClientThread(clientAddress,clientsock)
    nThread.start()

# connLoop=True
# 
# #Loop to keep the server connection alive
# while connLoop:
# 
#     try:
#         # Print the values to the serial port
#         temperature_c = dhtDevice.temperature
#         humidity = dhtDevice.humidity
#         #print(
#         #    "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
#         #        temperature_f, temperature_c, humidity
#         #    )
#         #)
# 
#     except RuntimeError as error:
#         # Errors happen fairly often, DHT's are hard to read, just keep going
#         print(error.args[0])
#         time.sleep(2.0)
#         continue
#     except Exception as error:
#         dhtDevice.exit()
#         raise error
# 
#     time.sleep(2.0)
# 
#     message = "T{}M{}          ".format(temperature_c, humidity)
#     print(message)
#     cryptmsg=encrypt(message.encode("utf-8"))
#     print(cryptmsg)
#     try:
#         clientSocket.sendto(cryptmsg,(HOST, PORT))
#         clientSocket.sendto("\n".encode("utf-8"),(HOST, PORT))
#         print("message sent!")
#     except socket.error:
#         print("Client have disconnected")
#         connLoop=False
#     time.sleep(5)
