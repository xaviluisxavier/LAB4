from servidor.operacoes.somar import Somar
from servidor.operacoes.subtrair import Subtrair
import servidor
import socket
from servidor.processa_cliente import ProcessaCliente
from dados.dados import Dados

from servidor.maquina.lista_clientes import ListaClientes
from servidor.maquina.broadcast_emissor import ThreadBroadcast

class Maquina:
    def __init__(self):
        self.sum = Somar()
        self.sub = Subtrair()
        self.s = socket.socket()
        self.s.bind(('', servidor.PORT))
        self.dados = Dados()
        self.clientes = ListaClientes()
        self.broadcast = ThreadBroadcast(self.clientes, self.dados, intervalo=10)
        self.broadcast.start()

    def execute(self):
        self.s.listen(1)
        print("Waiting for clients on port " + str(servidor.PORT))
        while True: 
            print("On accept...")
            connection, address = self.s.accept()
            print("Client", address, "connected")
            
            processo_cliente = ProcessaCliente(connection, address, self.dados, self.clientes)
            processo_cliente.start()