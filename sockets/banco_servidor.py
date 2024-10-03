import socket
import threading
import json
import time
import logging
from collections import defaultdict
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
        tipo = operacao['tipo']
        conta = operacao['conta']
        valor = operacao.get('valor', 0)

        with self.semaphore:  
            with self.lock:  
                print(f"Executando operação {tipo} na conta {conta}...")
                if tipo == 'deposito':
                    self.contas[conta] += valor
                    logging.info(f'Depósito: {valor} na conta {conta}')
                elif tipo == 'saque':
                    if self.contas[conta] >= valor:
                        self.contas[conta] -= valor
                        logging.info(f'Saque: {valor} da conta {conta}')
                    else:
                        return f'Saldo insuficiente na conta {conta}.'
                elif tipo == 'consulta':
                    saldo = self.contas[conta]
                    logging.info(f'Consulta saldo: {saldo} na conta {conta}')
                    return f'Saldo na conta {conta}: {saldo}'
                elif tipo == 'transferencia':
                    conta_destino = operacao['conta_destino']
                    if self.contas[conta] >= valor:
                        self.contas[conta] -= valor
                        self.contas[conta_destino] += valor
                        logging.info(f'Transferência: {valor} da conta {conta} para {conta_destino}')
                    else:
                        return f'Saldo insuficiente na conta {conta}.'

                self.salvar_dados()   
                return f'Operação {tipo} realizada com sucesso na conta {conta}.'

    def run(self):
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.processar_operacoes, args=(conn,)).start()

if __name__ == "__main__":
    servidor = BancoServidor()
    servidor.run()
