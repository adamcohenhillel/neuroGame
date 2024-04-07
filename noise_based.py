import os
import socket
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from neurosity import NeurositySDK

# Initialize Neurosity SDK
neurosity = NeurositySDK({
    "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
})

neurosity.login({
    "email": os.getenv("NEUROSITY_EMAIL"),
    "password": os.getenv("NEUROSITY_PASSWORD"),
})

# Global variables
sampling_rate = 256  # Samples per second
window_duration = 3  # Duration in seconds for noise detection
samples_per_window = sampling_rate * window_duration
buffer_lock = threading.Lock()
buffer = [[] for _ in range(8)]  # Initialize buffer for each channel
is_left = False
last_forward_num = 1

def standardize_data(data):
    return (data - np.mean(data)) / np.std(data)

def detect_noise_in_window(window):
    noise_threshold = 3.5  # Noise threshold after standardization
    standardized_window = standardize_data(window)
    return np.abs(standardized_window).max() > noise_threshold

def update_plot(i, axs, fig):
    global buffer, noise_status, is_left, last_forward_num
    with buffer_lock:
        temp_buffer = [list(channel) for channel in buffer]  # Copy buffer for safe use

    # Initialize a flag to track noise status in channels 3 and 4
    noise_detected_in_channels_3 = False
    noise_detected_in_channels_4 = False

    for idx, ax in enumerate(axs):
        ax.clear()
        if len(temp_buffer[idx]) >= samples_per_window:
            standardized_data = standardize_data(np.array(temp_buffer[idx][-samples_per_window:]))
            ax.plot(standardized_data)
            noise_detected = detect_noise_in_window(standardized_data)
            
            # Check for noise in channel 3 and 4 (note: channel indexing starts from 0)
            if idx == 3 and noise_detected:
                noise_detected_in_channels_3 = True
                ax.axvspan(0, samples_per_window, color='red', alpha=0.3)  # Visualize noise in the plot
            
            if idx == 4 and noise_detected:
                noise_detected_in_channels_4 = True
                ax.axvspan(0, samples_per_window, color='red', alpha=0.3)  # Visualize noise in the plot

        ax.set_title(f"Channel {idx + 1}")

    
    noise = noise_detected_in_channels_3 and noise_detected_in_channels_4
    if noise:
        last_forward_num = 1
        if is_left:
            noise_status = "0,-50"
        else:
            noise_status = "0,50"
        is_left = not is_left
    else:
        last_forward_num += 0.005
        noise_status = f"{last_forward_num},0"

def callback(data):
    global buffer
    with buffer_lock:
        for i, channel_data in enumerate(data['data']):
            buffer[i].extend(channel_data)
            buffer[i] = buffer[i][-samples_per_window:]  # Keep only the latest samples
        # data['data'][3]
        # buffer[3].extend(data['data'][3])
        # buffer[3] = buffer[3][-samples_per_window:]  # Keep only the latest samples
        # data['data'][4]
        # buffer[4].extend(data['data'][4])
        # buffer[4] = buffer[4][-samples_per_window:]  # Keep only the latest samples

def server_thread_function():
    HOST, PORT = '0.0.0.0', 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    try:
        while True:
            client_sock, address = server.accept()
            client_handler = threading.Thread(target=lambda: handle_client_connection(client_sock))
            client_handler.start()
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        server.close()


def handle_client_connection(client_socket):
    global noise_status
    try:
        while True:
            # Send the current noise status to the client
            client_socket.send(noise_status.encode('utf-8'))
            time.sleep(1)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    # Start the EEG data stream
    unsubscribe = neurosity.brainwaves_raw(callback)


    # Start the server in a separate thread
    server_thread = threading.Thread(target=server_thread_function)
    server_thread.start()

    # Main thread for Matplotlib plotting
    fig, axs = plt.subplots(8, 1, figsize=(10, 10))
    ani = FuncAnimation(fig, update_plot, fargs=(axs, fig), interval=1)
    plt.show()
