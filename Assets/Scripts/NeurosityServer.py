import socket
import threading
import random
import time

def handle_client_connection(client_socket):
    try:
        print('Client connected')
        while True:
            # Generate a random number and convert it to bytes
            random_number = random.randint(1, 100)
            message = str(random_number).encode('utf-8')
            client_socket.send(message)
            # Wait for a second before sending the next number
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
    HOST, PORT = '127.0.0.1', 8080
    start_server(HOST, PORT)
