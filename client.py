import socket
import threading
import os
from datetime import datetime

HEADER = 64
PORT = 8080
SERVER = '0.0.0.0'
ADDR = SERVER,PORT
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ADDR))

def send(msg):
    message = msg.encode(FORMAT) # encode the message
    msg_length = len(message) # find the length of the encoded message
    send_length = str(msg_length).encode(FORMAT) # encode the length
    send_length += b' ' * (HEADER - len(send_length)) # pad send_length to be 64
    client.send(send_length) # send length 
    client.send(message) # send message

def receive():
    msg_length = int(client.recv(HEADER).decode(FORMAT)) # get size of message
    msg = client.recv(msg_length).decode(FORMAT) # get actual message
    return msg

def start():
    thread = threading.Thread(target=handle_receive) # create thread to handle listening for messages
    thread.start()

    # continously look for user input to send
    while True:
        message = input()
        if (message[:4] == "SEND"): # client wants to send file
            send_file(("./" + message[5:]))
            continue
        send(message)
        if (message == DISCONNECT_MESSAGE): # client wants to disconnect
            thread.join() # stop listening to server
            break

def handle_receive():
    #continously receive from server
    while True:
        msg = receive()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(f"\r[{ADDR}][{current_time}] {msg}") # display Address, Time and message
        if (msg == "[CONNECTION TERMINATED]"): # server disconnected client
            break
        if (msg == "SEND"): # server is sending file
            recieve_file()

def recieve_file():
    # receive file name
    file_name = receive()
    print("received " + file_name)

    # receive file size
    file_size = receive()
    print(file_size + " bytes")

    file = open(file_name,"wb") # open file as write
    file_bytes = b"" # stores bytes
    file_bytes += client.recv(int(file_size)) # receive bytes from server

    # write out and close
    file.write(file_bytes)
    file.close()

def send_file(filename):
    send("SEND") #alert server file is being sent

    #attempt to open the file
    try:
        file = open (filename, "rb")
    except:
        print("File not found")
        return
    
    file_size = os.path.getsize(filename) # get file size
    send((filename)) # send file name
    send(str(file_size)) # send file size

    data = file.read() # get data from file
    client.sendall(data) # send data from file

start()