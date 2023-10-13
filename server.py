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

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
serv.bind((SERVER, PORT)) #bind socket using SERVER and PORT

def handle_client(conn,addr): #one per client
    thread = threading.Thread(target=handle_send, args= (conn,addr)) # start thread to handle sending
    thread.start()
    while True:
        msg = recieve(conn)
        if msg == DISCONNECT_MESSAGE: # client wants to disconnect
            break
        if msg == "SEND": # client wants to send a file
            recieve_file(conn)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(f"\r[{addr}][{current_time}] {msg}")
    close_client(conn, addr) # disconnect client

def send(conn, msg):
    message = msg.encode(FORMAT) # encode message
    msg_length = len(message) # get length of encoded message
    send_length = str(msg_length).encode(FORMAT) # encode length
    send_length += b' ' * (HEADER - len(send_length)) # pad send_length to be 64
    conn.send(send_length) # send length
    conn.send(message) # send message

def handle_send(conn, addr):
    while True:
        message = input()
        if (message == "END"): # server wants to disconnect
            serv.close()
            exit()
        if (message[:4] == "SEND"): # server wants to send file
            send_file(("./" + message[5:]), conn)
            continue
        try:
            send(conn, message)
        except:
            break

def start():
    serv.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    conn, addr = serv.accept() #connect to new client
    print(f"[NEW CONNECTION] {addr} connected.")
    handle_client(conn, addr)

def close_client(conn, addr):
    send(conn, "[CONNECTION TERMINATED]")
    conn.close()
    print(f"[CONNECTION] {addr} disconnected.")

def send_file(filename, conn):
    send(conn, "SEND")
    try:
        file = open (filename, "rb")
    except:
        print("File not found")
        return
    file_size = os.path.getsize(filename)
    send(conn,(filename))
    send(conn, str(file_size))

    data = file.read()
    conn.sendall(data)

def recieve_file(conn):
    # recieve file name
    file_name = recieve(conn)
    print("recieved " + file_name)

    # recieve file size
    file_size = recieve(conn)
    print(file_size + " bytes")

    file = open(file_name,"wb") # open file as write
    file_bytes = b"" # stores bytes
    file_bytes += conn.recv(int(file_size)) # receive bytes from server

    # write out and close
    file.write(file_bytes)
    file.close()

def recieve(conn):
    msg_length = int(conn.recv(HEADER).decode(FORMAT)) # get message size
    msg = conn.recv(msg_length).decode(FORMAT) # get message
    return msg

print("[STARTING] server is starting")
start()
