"""
Streamer Module
"""
import threading

class StreamerClient(threading.Thread):
    """
    Streamer Client Class
    """
    def __init__(self):
        threading.Thread.__init__(self)
