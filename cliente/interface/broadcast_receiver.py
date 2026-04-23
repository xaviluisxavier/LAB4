import threading
import json
import socket

class BroadcastReceiver(threading.Thread):
    def __init__(self, udp_socket): 
        super().__init__(daemon=True)
        self.udp_socket = udp_socket

    def receive_object(self):
        # Recebe pacotes de datagrama até 65535 bytes
        data, addr = self.udp_socket.recvfrom(65535)
        obj = json.loads(data.decode('utf-8'))
        return obj, addr

    def run(self):
        print("Receiver de broadcasts UDP ativa...")
        while True:
            try:
                hist, addr = self.receive_object()
                print("\n--- Broadcast do servidor ---")
                print(f"Recebido de: {addr}")
                print(f"Histórico: {hist}")
                print("-----------------------------")
            except Exception as e:
                print(f"Receiver UDP desconectado: {e}")
