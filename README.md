# threads-bancario-concorrencia

# Sistema Bancário Simples

Este é um sistema bancário simples implementado em Python, consistindo em um servidor que gerencia contas bancárias e processa transações, e um cliente que simula múltiplos usuários realizando operações bancárias.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **FastAPI**: Para o desenvolvimento da API HTTP.
- **Sockets**: Para comunicação entre o cliente e o servidor.
- **Threading**: Para permitir operações simultâneas.
- **JSON**: Para persistência de dados e manipulação de contas.

## Funcionalidades

- **Servidor Bancário** (`banco_servidor.py`):
  - Mantém um conjunto de contas bancárias.
  - Processa operações de depósito, saque, consulta de saldo e transferências.
  - Utiliza **locks** para proteger operações em contas individuais.
  - Registra todas as operações realizadas em um arquivo de log.
  - Utiliza sockets para comunicação com os clientes.

- **Cliente Bancário** (`banco_cliente.py`):
  - Permite ao usuário especificar o número de clientes e transações.
  - Gera transações aleatórias (depósito, saque, consulta de saldo, transferências).
  - Adiciona um pequeno atraso entre as operações para simular um cenário mais realista.
  - Exibe os resultados das operações.

