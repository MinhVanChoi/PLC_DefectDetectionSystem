import snap7
from snap7.util import get_bool, set_bool
import threading
import time

class PLCHandler:  # Đảm bảo tên Class đúng như thế này
    def __init__(self, ip="192.168.0.1", db_number=1):
        self.ip = ip
        self.db_number = db_number
        self.client = snap7.client.Client()
        self.lock = threading.Lock()
        self.connected = False

    def connect(self):
        try:
            if not self.client.get_connected():
                self.client.connect(self.ip, 0, 1)
                self.connected = self.client.get_connected()
            return self.connected
        except:
            self.connected = False
            return False

    def read_all_data(self):
        if not self.connected: 
            self.connect()
            return None
        try:
            with self.lock:
                data = self.client.db_read(self.db_number, 0, 3)
            in_bits = [get_bool(data, 0, i) for i in range(8)]
            out_bits = [get_bool(data, 1, i) for i in range(8)] + [get_bool(data, 2, i) for i in range(3)]
            return in_bits, out_bits
        except:
            self.connected = False
            return None

    def disconnect(self):
        if self.client.get_connected():
            self.client.disconnect()