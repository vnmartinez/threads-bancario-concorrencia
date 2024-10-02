from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Lock
import json
import logging


logging.basicConfig(filename='banco.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = FastAPI()


contas = {}
lock = Lock()


class Transacao(BaseModel):
    tipo: str
    conta: str
    valor: float = 0
    conta_destino: str = None

def carregar_dados():
    try:
        with open('contas.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def salvar_dados():
    with open('contas.json', 'w') as file:
        json.dump(contas, file)


contas = carregar_dados()

@app.post("/transacao/")
async def processar_transacao(transacao: Transacao):
    with lock: 
        if transacao.tipo == 'deposito':
            contas[transacao.conta] = contas.get(transacao.conta, 0) + transacao.valor
            logging.info(f'Depósito: {transacao.valor} na conta {transacao.conta}')
            salvar_dados()
            return {"message": f'Depósito de {transacao.valor} na conta {transacao.conta} realizado com sucesso.'}

        elif transacao.tipo == 'saque':
            if contas.get(transacao.conta, 0) >= transacao.valor:
                contas[transacao.conta] -= transacao.valor
                logging.info(f'Saque: {transacao.valor} da conta {transacao.conta}')
                salvar_dados()
                return {"message": f'Saque de {transacao.valor} da conta {transacao.conta} realizado com sucesso.'}
            else:
                raise HTTPException(status_code=400, detail="Saldo insuficiente.")

        elif transacao.tipo == 'consulta':
            saldo = contas.get(transacao.conta, 0)
            logging.info(f'Consulta saldo: {saldo} na conta {transacao.conta}')
            return {"message": f'Saldo na conta {transacao.conta}: {saldo}'}

        elif transacao.tipo == 'transferencia':
            if contas.get(transacao.conta, 0) >= transacao.valor:
                contas[transacao.conta] -= transacao.valor
                contas[transacao.conta_destino] = contas.get(transacao.conta_destino, 0) + transacao.valor
                logging.info(f'Transferência: {transacao.valor} da conta {transacao.conta} para {transacao.conta_destino}')
                salvar_dados()
                return {"message": f'Transferência de {transacao.valor} da conta {transacao.conta} para {transacao.conta_destino} realizada com sucesso.'}
            else:
                raise HTTPException(status_code=400, detail="Saldo insuficiente.")

    return {"message": "Operação não reconhecida."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
