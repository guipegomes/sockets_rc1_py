# Chat TCP — Redes de Computadores

Aplicação de chat em tempo real usando **sockets TCP** em Python.  
Suporta múltiplos clientes simultaneamente com **apelidos** e **salas** de conversa.

## Integrantes

- Guilherme Perez Gomes
- Maria Clara Passareli Alves
- Mateus Ciffoni

## Requisitos

- Python 3.8+
- Sem dependências externas (usa apenas a biblioteca padrão do Python)

## Como executar

**1. Inicie o servidor:**
```bash
python server.py
```

**2. Em outro terminal, inicie um cliente:**
```bash
python client.py
```

Repita o passo 2 para cada participante do chat.

## Comandos disponíveis

| Comando | Descrição |
|---|---|
| `/salas` | Lista as salas disponíveis |
| `/trocar <sala>` | Muda para outra sala |
| `/sair` | Desconecta do servidor |

## Demonstração em vídeo

[Link do YouTube]