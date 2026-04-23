import servidor
import threading
import time
import json
import socket
from typing import Dict
from servidor.maquina.lista_clientes import ListaClientes
from dados.dados import Dados

class ThreadBroadcast(threading.Thread):
    def __init__(self, lista_clientes: ListaClientes, dados: Dados, intervalo: int = 10):
        super().__init__(daemon=True)
        self.lista_clientes = lista_clientes
        self.dados = dados
        self.intervalo = intervalo
        self.running = True
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_object_udp(self, udp_address, obj):
        data = json.dumps(obj).encode('utf-8')
        self.udp_socket.sendto(data, udp_address)

    def broadcast_object(self, obj: Dict) -> None:
        destinos = self.lista_clientes.obter_destinos_udp()
        for address, udp_address in destinos.items():
            try:
                self.send_object_udp(udp_address, obj)
                print(f"Broadcast UDP enviado para {address} -> {udp_address}")
            except Exception as e:
                print(f"Erro ao enviar para {address}: {e}")

    def run(self):
        print("ThreadBroadcast ativa")
        while self.running:
            try:
                time.sleep(self.intervalo)
                _hist = self.dados.get_operacoes()
                self.broadcast_object(_hist)
            except Exception as e:
                print(f"Erro: {e}")
                continue
        print("ThreadBroadcast terminada")