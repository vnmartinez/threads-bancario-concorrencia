@echo off
REM Inicia o servidor em uma nova janela do terminal
start cmd /k "python .\banco_servidor.py"

REM Inicia o cliente em uma nova janela do terminal
start cmd /k "python .\banco_cliente.py"

REM Mantém a janela do .bat aberta
pause