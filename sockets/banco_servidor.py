import socket
import json
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Semaphore

logging.basicConfig(filename='banco.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class BancoServidor:
    def __init__(self, host='localhost', port=12345):
        self.contas = defaultdict(float)  
        self.lock = Lock() 
        self.semaphore = Semaphore(5)  
        self.carregar_dados() 

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Servidor bancário ouvindo em {host}:{port}...")

    def carregar_dados(self):
        try:
            with open('contas.json', 'r') as file:
                self.contas = json.load(file)
        except FileNotFoundError:
            print("Arquivo de dados não encontrado. Usando contas vazias.")

    def salvar_dados(self):
        with open('contas.json', 'w') as file:
            json.dump(self.contas, file)

    def processar_operacoes(self, conn):
        while True:
            try:
                dados = conn.recv(1024).decode()
                if not dados:
                    break
                operacao = json.loads(dados)
                resposta = self.executar_operacao(operacao)
                conn.sendall(resposta.encode())
            except Exception as e:
                print(f"Erro: {e}")
                break
        conn.close()

    def executar_operacao(self, operacao):
        with self.semaphore:  
            operacao_tipo = operacao.get('tipo')
            conta = operacao.get('conta')
            valor = operacao.get('valor', 0)

            print (f'Executando operação {operacao_tipo} na conta {conta}...')
            if operacao_tipo == 'deposito':
                with self.lock:  
                    self.contas[conta] += valor
                    self.salvar_dados()
                    return f"Depósito de {valor} realizado com sucesso na conta {conta}."
                
            if operacao_tipo == 'saque':
                with self.lock: 
                    if self.contas[conta] >= valor:
                        self.contas[conta] -= valor
                        self.salvar_dados()
                        return f"Saque de {valor} realizado com sucesso na conta {conta}."
                    else:
                        return "Saldo insuficiente."
            if operacao_tipo == 'consulta':
                with self.lock: 
                    saldo = self.contas[conta]
                    return f"Saldo na conta {conta}: {saldo}."
            
            if operacao_tipo == 'transferencia':
                conta_destino = operacao.get('conta_destino')
                with self.lock: 
                    if self.contas[conta] >= valor:
                        self.contas[conta] -= valor
                        self.contas[conta_destino] += valor
                        self.salvar_dados()
                        return f"Transferência de {valor} realizada com sucesso da conta {conta} para a conta {conta_destino}."
                    else:
                        return "Saldo insuficiente."

    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:  
            while True:
                conn, _ = self.server_socket.accept()
                executor.submit(self.processar_operacoes, conn)

if __name__ == "__main__":
    servidor = BancoServidor()
    servidor.run()
