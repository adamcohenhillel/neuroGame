from neurosity import NeurositySDK
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


neurosity = NeurositySDK({
    "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
})

neurosity.login({
    "email": os.getenv("NEUROSITY_EMAIL"),
    "password": os.getenv("NEUROSITY_PASSWORD"),
})


# Initialize plotting
fig, axs = plt.subplots(8, 1, figsize=(10, 10))  # 8 subplots for 8 channels
plt.ion()  # Turn on interactive mode

sampling_rate = 256  # Samples per second
window_duration = 3  # Duration in seconds for noise detection
samples_per_window = sampling_rate * window_duration
buffer = [[] for _ in range(8)]  # Initialize buffer for each channel

def detect_noise_in_window(window):
    noise_threshold = 100  # Define your noise threshold
    return np.std(window) > noise_threshold

def on_noise_detected_all_channels():
    print("Noise detected across all channels!")

def update_plot(i):
    noise_detected_in_all_channels = True
    for idx, ax in enumerate(axs):
        ax.clear()
        ax.plot(buffer[idx])
        if len(buffer[idx]) == samples_per_window:
            noise_detected = detect_noise_in_window(buffer[idx])
            if noise_detected:
                ax.axvspan(0, samples_per_window, color='red', alpha=0.3)
            noise_detected_in_all_channels &= noise_detected
        else:
            noise_detected_in_all_channels = False
        ax.set_title(f"Channel {idx+1}")
    if noise_detected_in_all_channels:
        on_noise_detected_all_channels()

def callback(data):
    global buffer
    for i, channel_data in enumerate(data['data']):
        buffer[i].extend(channel_data)
        buffer[i] = buffer[i][-samples_per_window:]  # Keep only the latest samples

unsubscribe = neurosity.brainwaves_raw(callback)

ani = FuncAnimation(fig, update_plot, interval=1000)  # Update the plot every second
plt.show(block=True)  # Show the plot in blocking mode
