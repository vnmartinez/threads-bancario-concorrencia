import socket
import threading
import json
import time
import logging
from collections import defaultdict
from threading import Lock, Semaphore

# Configuração de logging
logging.basicConfig(filename='banco.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class BancoServidor:
    def __init__(self, host='localhost', port=12345):
        self.contas = defaultdict(float)  # Dicionário para armazenar saldos
        self.lock = Lock()  # Lock para proteger acessos concorrentes
        self.semaphore = Semaphore(5)  # Limita a 5 operações simultâneas
        self.carregar_dados()  # Carrega dados de contas existentes

        # Inicia o servidor
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Servidor bancário ouvindo em {host}:{port}...")
    
    def carregar_dados(self):
        try:
            with open('contas.json', 'r') as file:
                self.contas = json.load(file)
                print("Dados carregados com sucesso.")
        except FileNotFoundError:
            print("Arquivo de dados não encontrado. Usando contas vazias.")
    
    def salvar_dados(self):
        with open('contas.json', 'w') as file:
            json.dump(self.contas, file)
            print("Dados salvos com sucesso.")

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

        with self.semaphore:  # Limita o número de operações simultâneas
            with self.lock:  # Protege o acesso às contas
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

                self.salvar_dados()  # Salva dados após cada operação
                return f'Operação {tipo} realizada com sucesso na conta {conta}.'

    def run(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f'Conexão aceita de {addr}.')
            threading.Thread(target=self.processar_operacoes, args=(conn,)).start()

if __name__ == "__main__":
    servidor = BancoServidor()
    servidor.run()
