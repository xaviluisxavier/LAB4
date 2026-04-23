import pygame
import socket
import cliente
from cliente.interface.broadcast_receiver import BroadcastReceiver

class InterfaceGrafica:
    def __init__(self):
        # 1. LIGAÇÃO DE REDE
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((cliente.SERVER_ADDRESS, cliente.PORT))
        
        # Socket UDP para escutar broadcasts do histórico
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 0))
        self.udp_port = self.udp_socket.getsockname()[1]
        
        # Avisar o servidor do nosso porto UDP
        self.send_str(self.connection, cliente.UDP_PORT)
        self.send_int(self.connection, self.udp_port, cliente.INT_SIZE)
        
        # Iniciar thread do recetor UDP
        self.broadcast = BroadcastReceiver(self.udp_socket)
        self.broadcast.start()

        # 2. INICIALIZAÇÃO DO PYGAME
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Calculadora Distribuída SD 2026")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        
        # 3. VARIÁVEIS DE ESTADO DO ECRÃ
        self.val_x = ""
        self.val_y = ""
        self.campo_ativo = 'x' # Alterna entre 'x' e 'y'
        self.resultado = "A aguardar."

    # --- Funções auxiliares de rede ---
    def receive_str(self, connect, n_bytes): 
        return connect.recv(n_bytes).decode()
        
    def send_str(self, connect, value): 
        connect.send(value.encode())
        
    def send_int(self, connect, value, n_bytes): 
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))
        
    def receive_int(self, connect, n_bytes): 
        return int.from_bytes(connect.recv(n_bytes), byteorder='big', signed=True)

    # --- Função de desenho ---
    def desenhar_ecra(self):
        self.screen.fill((230, 230, 250)) # Fundo lilás claro
        
        # Cria os textos. Cor vermelha se for a caixa selecionada
        cor_x = (255, 0, 0) if self.campo_ativo == 'x' else (0, 0, 0)
        cor_y = (255, 0, 0) if self.campo_ativo == 'y' else (0, 0, 0)
        
        txt_x = self.font.render(f"Valor X: {self.val_x}", True, cor_x)
        txt_y = self.font.render(f"Valor Y: {self.val_y}", True, cor_y)
        txt_res = self.font.render(f"Resultado: {self.resultado}", True, (0, 100, 0))
        instrucoes = pygame.font.Font(None, 24).render("ESC: Sair | TAB: Trocar X/Y | +, -, / : Calcular", True, (100, 100, 100))

        # Posiciona os textos no ecrã
        self.screen.blit(txt_x, (50, 50))
        self.screen.blit(txt_y, (50, 100))
        self.screen.blit(txt_res, (50, 200))
        self.screen.blit(instrucoes, (20, 350))
        
        pygame.display.flip()

    # --- Ciclo principal (Thread Pygame) ---
    def execute(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.send_str(self.connection, cliente.END_OP)
                
                if event.type == pygame.KEYDOWN:
                    # 0. Sair com a tecla ESC <--- AQUI ESTÁ A NOVA FUNÇÃO
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.send_str(self.connection, cliente.END_OP)
                        
                    # 1. Alternar caixa de texto
                    elif event.key == pygame.K_TAB:
                        self.campo_ativo = "y" if self.campo_ativo == "x" else "x"
                    
                    # 2. Apagar números
                    elif event.key == pygame.K_BACKSPACE:
                        if self.campo_ativo == "x": self.val_x = self.val_x[:-1]
                        else: self.val_y = self.val_y[:-1]
                    
                    # 3. Inserir números (0 a 9)
                    elif event.unicode.isdigit():
                        if self.campo_ativo == "x": self.val_x += event.unicode
                        else: self.val_y += event.unicode
                    
                    # 4. Sinais ou Operações (+, -, /)
                    elif event.unicode in ["+", "-", "/"]:
                        
                        # EXCEÇÃO: Permite números negativos se a caixa atual estiver vazia
                        if event.unicode == "-" and ((self.campo_ativo == "x" and self.val_x == "") or (self.campo_ativo == "y" and self.val_y == "")):
                            if self.campo_ativo == "x": self.val_x += "-"
                            else: self.val_y += "-"
                            
                        # CASO CONTRÁRIO: Envia a operação matemática para o Servidor
                        elif self.val_x not in ["", "-"] and self.val_y not in ["", "-"]:
                            op = cliente.ADD_OP if event.unicode == "+" else (cliente.SUB_OP if event.unicode == "-" else cliente.DIV_OP)
                            
                            self.send_str(self.connection, op)
                            self.send_int(self.connection, int(self.val_x), cliente.INT_SIZE)
                            self.send_int(self.connection, int(self.val_y), cliente.INT_SIZE)
                            
                            # Fica à espera do resultado via TCP
                            self.resultado = str(self.receive_int(self.connection, cliente.INT_SIZE))
                            
                            # Limpa os campos para o próximo cálculo
                            self.val_x = ""
                            self.val_y = ""
                            self.campo_ativo = "x"

            self.desenhar_ecra()
            self.clock.tick(30) # Mantém os frames controlados (30 FPS)
            
        pygame.quit()
