import os
import socket
import threading
import random
import time

from neurosity import NeurositySDK

neurosity = NeurositySDK({
    "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
})

neurosity.login({
    "email": os.getenv("NEUROSITY_EMAIL"),
    "password": os.getenv("NEUROSITY_PASSWORD"),
})


def handle_client_connection(client_socket):

    current = "0,-100".encode('utf-8')
    def leftArm(data):
        print("data", data)
        p = data["predictions"].pop()["probability"]
        if p > 0.5:
            mapped_value = ((p - 0.5) / (1 - 0.5)) * 100
            sn = f"0,-{mapped_value}".encode('utf-8')
            client_socket.send(sn)
            print(sn)
        else:
            message = str(0).encode('utf-8')
            client_socket.send(message)
    
    def moveForward(data):
        print("data", data)
        p = data["predictions"].pop()["probability"]
        if p > 0.5:
            sn = f"{p},0".encode('utf-8')
            client_socket.send(sn)
            print(sn)
        else:
            message = str(0).encode('utf-8')
            client_socket.send(message)
    
    def mentalMath(data):
        print("data", data)
        p = data["predictions"].pop()["probability"]
        if p > 0.5:
            mapped_value = ((p - 0.5) / (1 - 0.5)) * 100
            sn = f"0,{mapped_value}".encode('utf-8')
            client_socket.send(sn)
            print(sn)
        else:
            message = str(0).encode('utf-8')
            client_socket.send(message)

    unsubscribe = neurosity.kinesis("leftArm", leftArm)
    unsubscribe = neurosity.kinesis("leftHandPinch", leftArm)
    unsubscribe2 = neurosity.kinesis("moveForward", moveForward)
    unsubscribe3 = neurosity.kinesis("mentalMath", mentalMath)
    # unsubscribe2 = neurosity.kinesis("leftHandPinch", callback)

    try:
        print('Client connected')
        while True:
            # Generate a random number between -1 and 1 and convert it to bytes
            print("waiting...")
            client_socket.send("0,0".encode('utf-8'))
            # Wait for 5 seconds before sending the next number
            time.sleep(1)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        client_socket.close()

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)  # max backlog of connections
    print(f"Listening on {host}:{port}")
    
    try:
        while True:
            client_sock, address = server.accept()
            print(f"Accepted connection from {address[0]}:{address[1]}")
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_sock,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8080
    start_server(HOST, PORT)
