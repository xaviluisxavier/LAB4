import socket
import json
import cliente

from cliente.interface.broadcast_receiver import BroadcastReceiver

class Interface:
    def __init__(self):
        # Ligação TCP para pedidos/respostas da calculadora
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((cliente.SERVER_ADDRESS, cliente.PORT))
        
        # Socket UDP dedicado para receber broadcasts
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 0)) # porta livre atribuída pelo SO
        self.udp_port = self.udp_socket.getsockname()[1]
        
        # Informa o servidor de que a seguir será enviado o porto UDP
        self.send_str(self.connection, cliente.UDP_PORT)
        self.send_int(self.connection, self.udp_port, cliente.INT_SIZE)
        print(f"Cliente ligado por TCP; à escuta de broadcasts UDP na porta {self.udp_port}")
        broadcast = BroadcastReceiver(self.udp_socket)
        broadcast.start()

    def receive_str(self, connect, n_bytes: int) -> str:
        data = connect.recv(n_bytes)
        return data.decode()

    def send_str(self, connect, value: str) -> None:
        connect.send(value.encode())

    def send_int(self, connect: socket.socket, value: int, n_bytes: int) -> None:
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_int(self, connect: socket.socket, n_bytes: int) -> int:
        data = connect.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def execute(self):
        # Iniciar recepção de udp no lado do cliente
        

        print("Preciso que introduza dois valores:")
        x: int = int(input("x="))
        y: int = int(input("y="))

        res = ""
        while res != ".":
            print("Qual é o cálculo que quer efetuar? x + - / ('.' para fim)")
            res = input()

            if res == "+":
                self.send_str(self.connection, cliente.ADD_OP)
                self.send_int(self.connection, x, cliente.INT_SIZE)
                self.send_int(self.connection, y, cliente.INT_SIZE)
                resultado = self.receive_int(self.connection, cliente.INT_SIZE)
                print(f"-> Resultado: {resultado}")

            elif res == "-":
                self.send_str(self.connection, cliente.SUB_OP)
                self.send_int(self.connection, x, cliente.INT_SIZE)
                self.send_int(self.connection, y, cliente.INT_SIZE)
                resultado = self.receive_int(self.connection, cliente.INT_SIZE)
                print(f"-> Resultado: {resultado}")
                
            elif res == "/":
                self.send_str(self.connection, cliente.DIV_OP)
                self.send_int(self.connection, x, cliente.INT_SIZE)
                self.send_int(self.connection, y, cliente.INT_SIZE)
                resultado = self.receive_int(self.connection, cliente.INT_SIZE)
                print(f"-> Resultado: {resultado}")

        self.send_str(self.connection, cliente.END_OP)
