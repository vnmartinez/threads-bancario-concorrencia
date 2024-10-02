import requests
import random
import time

class BancoCliente:
    def __init__(self, host='http://localhost:8000', num_transacoes=10):
        self.host = host
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
        else:  # consulta
            return {'tipo': operacao, 'conta': conta}

    def enviar_transacao(self, transacao):
        response = requests.post(f'{self.host}/transacao/', json=transacao)
        if response.status_code == 200:
            print(f'Resposta do servidor: {response.json()["message"]}')
        else:
            print(f'Erro: {response.json()["detail"]}')

    def executar_clientes(self, num_clientes):
        for i in range(num_clientes):
            conta = f"conta{i % 5 + 1}"
            for _ in range(self.num_transacoes):
                transacao = self.gerar_transacao(conta)
                self.enviar_transacao(transacao)
                time.sleep(random.uniform(0.1, 0.5))  # Atraso entre transações

if __name__ == "__main__":
    cliente = BancoCliente(num_transacoes=5)  # Pode ajustar o número de transações
    cliente.executar_clientes(num_clientes=10)  # Simula 10 clientes
