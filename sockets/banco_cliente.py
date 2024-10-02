import socket
import json
import random
import time
import threading

class BancoCliente:
    def __init__(self, host='localhost', port=12345, num_transacoes=10):
        self.host = host
        self.port = port
        self.num_transacoes = num_transacoes
        self.operacoes = ['deposito', 'saque', 'consulta', 'transferencia']

    def gerar_transacao(self, conta):
        operacao = random.choice(self.operacoes)
        if operacao == 'transferencia':
            conta_destino = f"conta{random.randint(1, 5)}"
            valor = random.randint(10, 100)
            return {'tipo': operacao, 'conta': conta, 'conta_destino': conta_destino, 'valor': valor}
        elif operacao in ['deposito', 'saque']:
            valor = random.randint(10, 100)
            return {'tipo': operacao, 'conta': conta, 'valor': valor}
        else: 
            return {'tipo': operacao, 'conta': conta}

    def enviar_transacao(self, transacao):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json.dumps(transacao).encode())
            resposta = s.recv(1024).decode()
            print(f'Resposta do servidor: {resposta}')

    def executar_clientes(self, num_clientes):
        threads = []
        for i in range(num_clientes):
            conta = f"conta{i % 5 + 1}"
            for _ in range(self.num_transacoes):
                transacao = self.gerar_transacao(conta)
                t = threading.Thread(target=self.enviar_transacao, args=(transacao,))
                threads.append(t)
                t.start()
                time.sleep(random.uniform(0.1, 0.5))   
        for t in threads:
            t.join()

if __name__ == "__main__":
    cliente = BancoCliente(num_transacoes=5) 
    cliente.executar_clientes(num_clientes=10) 
