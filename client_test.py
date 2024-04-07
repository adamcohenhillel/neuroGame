import socket

def receive_noise_status(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        while True:
            # Receive data from the server
            noise_status = client.recv(1024).decode('utf-8')
            if not noise_status:
                print("Server closed the connection.")
                break
            print(f"Noise Status: {noise_status}")
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    HOST, PORT = '127.0.0.1', 8080  # Server address and port
    receive_noise_status(HOST, PORT)
