# server.py — Servidor TCP do Chat

import socket
import threading

# Configurações do servidor
HOST = "0.0.0.0"    # Aceita conexões de qualquer interface de rede
PORT = 5555         # Porta que o servidor vai escutar


# Estado global do servidor
salas = {}          # { "nome_da_sala": [{"conn": conn, "apelido": "X"}, ...] }
lock = threading.Lock()  # Garante acesso seguro ao dicionário entre threads


# Função que trata cada cliente em sua própria thread
def handle_client(conn, addr):
    """
    Executada em uma thread separada para cada cliente conectado.

    Parâmetros:
        conn (socket): conexão estabelecida com o cliente
        addr (tuple): endereço do cliente (ip, porta)
    """
    print(f"[SERVIDOR] Nova conexão: {addr}")

    try:
        # TODO (Parte 2): solicitar apelido ao cliente
        # TODO (Parte 2): solicitar sala ao cliente
        # TODO (Parte 2): loop de recebimento de mensagens e comandos
        pass

    except Exception as e:
        print(f"[SERVIDOR] Erro com {addr}: {e}")

    finally:
        # TODO (Parte 2): remover cliente da sala e notificar os demais
        conn.close()
        print(f"[SERVIDOR] Conexão encerrada: {addr}")


# Inicialização do servidor
def iniciar_servidor():
    """
    Cria o socket TCP, aguarda conexões e spawna uma thread por cliente.
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reusar a porta logo após encerrar o servidor (evita erros em dev)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PORT))
    servidor.listen(5)  # Fila de até 5 conexões pendentes

    print(f"[SERVIDOR] Escutando em {HOST}:{PORT} ...")
    print("[SERVIDOR] Aguardando clientes. Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            conn, addr = servidor.accept()  # Bloqueia até um cliente conectar

            # Cada cliente ganha sua própria thread para não bloquear os demais
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True  # Thread encerra junto com o processo principal
            )
            thread.start()

    except KeyboardInterrupt:
        print("\n[SERVIDOR] Encerrando servidor...")

    finally:
        servidor.close()


# Ponto de entrada
if __name__ == "__main__":
    iniciar_servidor()