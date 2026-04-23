import threading
import servidor
from servidor.operacoes.somar import Somar
from servidor.operacoes.subtrair import Subtrair
from servidor.operacoes.dividir import Dividir

class ProcessaCliente(threading.Thread):
    def __init__(self, connection, address, dados, clientes):
        super().__init__()
        self.connection = connection
        self.address = address
        self.sum = Somar()
        self.sub = Subtrair()
        self.div = Dividir()
        self.dados = dados
        self.clientes = clientes
        self.udp_port = None 

    def receive_int(self, connection, n_bytes: int) -> int:
        data = connection.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_int(self, connection, value: int, n_bytes: int) -> None:
        connection.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_str(self, connection, n_bytes: int) -> str:
        data = connection.recv(n_bytes)
        return data.decode()

    def send_str(self, connection, value: str) -> None:
        connection.send(value.encode())

    def run(self):
        print(self.address, "Thread iniciada")
        last_request = False
        while not last_request:
            request_type = self.receive_str(self.connection, servidor.COMMAND_SIZE)
            
            # NOVO: Regista o porto UDP do cliente
            if request_type == servidor.UDP_PORT:
                self.udp_port = self.receive_int(self.connection, servidor.INT_SIZE)
                print(f"[{self.address}] Porto UDP do cliente recebido: {self.udp_port}")
                self.clientes.adicionar(self.address, self.connection, self.udp_port)
            
            elif request_type == servidor.ADD_OP:
                x = self.receive_int(self.connection, servidor.INT_SIZE)
                y = self.receive_int(self.connection, servidor.INT_SIZE)
                print(f"[{self.address}] Somar: {x} + {y}")
                result = self.sum.execute(x, y)
                self.dados.registar_oper('soma', x, y, result, self.address)
                print(self.address, ": registada uma soma")
                self.send_int(self.connection, result, servidor.INT_SIZE)
                
            elif request_type == servidor.SUB_OP:
                x = self.receive_int(self.connection, servidor.INT_SIZE)
                y = self.receive_int(self.connection, servidor.INT_SIZE)
                print(f"[{self.address}] Subtrair: {x} - {y}")
                result = self.sub.execute(x, y)
                self.dados.registar_oper('subtrair', x, y, result, self.address)
                print(self.address, ": registada uma subtracao")
                self.send_int(self.connection, result, servidor.INT_SIZE)

            elif request_type == servidor.DIV_OP:
                x = self.receive_int(self.connection, servidor.INT_SIZE)
                y = self.receive_int(self.connection, servidor.INT_SIZE)
                print(f"[{self.address}] Dividir: {x} / {y}")
                result = self.div.execute(x, y)
                self.dados.registar_oper('dividir', x, y, result, self.address)
                print(self.address, ": registada uma divisao")
                self.send_int(self.connection, result, servidor.INT_SIZE)

            elif request_type == servidor.END_OP:
                last_request = True
                
        print(self.address, "Thread terminada")
        print("Dicionário guardado nos dados:", self.dados.operacoes)
        self.clientes.remover(self.address)
        self.connection.close()