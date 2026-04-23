import pygame
import socket
import cliente
from cliente.interface.broadcast_receiver import BroadcastReceiver

class InterfaceGrafica:
    def __init__(self):
        # 1. LIGAÇÃO DE REDE
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((cliente.SERVER_ADDRESS, cliente.PORT))
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 0))
        self.udp_port = self.udp_socket.getsockname()[1]
        
        self.send_str(self.connection, cliente.UDP_PORT)
        self.send_int(self.connection, self.udp_port, cliente.INT_SIZE)
        
        self.broadcast = BroadcastReceiver(self.udp_socket)
        self.broadcast.start()

        # 2. INICIALIZAÇÃO DO PYGAME
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Calculadora Distribuída")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        
        # Variáveis de Estado
        self.input_x = ""
        self.input_y = ""
        self.foco_atual = 'x' # Alterna entre 'x' e 'y'
        self.resultado = "A aguardar."

    # Funções auxiliares de rede
    def receive_str(self, connect, n_bytes): return connect.recv(n_bytes).decode()
    def send_str(self, connect, value): connect.send(value.encode())
    def send_int(self, connect, value, n_bytes): connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))
    def receive_int(self, connect, n_bytes): return int.from_bytes(connect.recv(n_bytes), byteorder='big', signed=True)

    def desenhar_ecra(self):
        self.screen.fill((230, 230, 250)) # Fundo lilás claro
        
        # Cria os textos
        cor_x = (255, 0, 0) if self.foco_atual == 'x' else (0, 0, 0)
        cor_y = (255, 0, 0) if self.foco_atual == 'y' else (0, 0, 0)
        
        txt_x = self.font.render(f"Valor X: {self.input_x}", True, cor_x)
        txt_y = self.font.render(f"Valor Y: {self.input_y}", True, cor_y)
        txt_res = self.font.render(f"Resultado: {self.resultado}", True, (0, 100, 0))
        instrucoes = pygame.font.Font(None, 24).render("Pressione TAB para trocar entre X e Y. Pressione +, - ou / para calcular.", True, (100, 100, 100))

        # Posiciona os textos
        self.screen.blit(txt_x, (50, 50))
        self.screen.blit(txt_y, (50, 100))
        self.screen.blit(txt_res, (50, 200))
        self.screen.blit(instrucoes, (20, 350))
        
        pygame.display.flip()

    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.send_str(self.connection, cliente.END_OP)
                
                elif event.type == pygame.KEYDOWN:
                    # Trocar de caixa de texto
                    if event.key == pygame.K_TAB:
                        self.foco_atual = 'y' if self.foco_atual == 'x' else 'x'
                    
                    # Apagar números
                    elif event.key == pygame.K_BACKSPACE:
                        if self.foco_atual == 'x': self.input_x = self.input_x[:-1]
                        else: self.input_y = self.input_y[:-1]
                    
                    # Inserir números
                    elif event.unicode.isnumeric() or event.unicode == '-':
                        if self.foco_atual == 'x': self.input_x += event.unicode
                        else: self.input_y += event.unicode
                    
                    # Fazer o cálculo
                    elif event.unicode in ['+', '-', '/']:
                        if self.input_x and self.input_y:
                            x_val, y_val = int(self.input_x), int(self.input_y)
                            op = cliente.ADD_OP if event.unicode == '+' else (cliente.SUB_OP if event.unicode == '-' else cliente.DIV_OP)
                            
                            self.send_str(self.connection, op)
                            self.send_int(self.connection, x_val, cliente.INT_SIZE)
                            self.send_int(self.connection, y_val, cliente.INT_SIZE)
                            
                            self.resultado = str(self.receive_int(self.connection, cliente.INT_SIZE))
                            self.input_x = "" # Limpa para o próximo cálculo
                            self.input_y = ""
                            self.foco_atual = 'x'

            self.desenhar_ecra()
            self.clock.tick(30) # 30 frames por segundo
            
        pygame.quit()