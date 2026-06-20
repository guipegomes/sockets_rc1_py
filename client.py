# client.py — Cliente TCP do Chat
#teste alteração
import socket
import threading

# Configurações de conexão
HOST = "127.0.0.1"  # Endereço do servidor (localhost para testes locais)
PORT = 5555          # Deve ser igual ao PORT definido no server.py


# Thread de recebimento
# Fica em loop aguardando mensagens vindas do servidor
def receber_mensagens(sock):
    """
    Executada em uma thread separada.
    Imprime no terminal tudo que chegar do servidor.

    Parâmetros:
        sock (socket): socket conectado ao servidor
    """
    while True:
        try:
            mensagem = sock.recv(1024).decode("utf-8")
            if not mensagem:
                # Servidor fechou a conexão
                print("[CLIENTE] Conexão encerrada pelo servidor.")
                break
            print(mensagem)

        except Exception:
            # Conexão perdida inesperadamente
            print("[CLIENTE] Conexão perdida.")
            break


# Thread de envio
# Fica em loop lendo o input do usuário e mandando pro servidor
def enviar_mensagens(sock):
    """
    Executada na thread principal (ou em outra thread).
    Lê o input do usuário e envia ao servidor.

    Parâmetros:
        sock (socket): socket conectado ao servidor
    """
    while True:
        try:
            mensagem = input()
            if not mensagem:
                continue
            sock.send(mensagem.encode("utf-8"))

        except (EOFError, KeyboardInterrupt):
            print("\n[CLIENTE] Encerrando...")
            break

        except Exception as e:
            print(f"[CLIENTE] Erro ao enviar: {e}")
            break


# Inicialização do cliente
def iniciar_cliente():
    """
    Conecta ao servidor e sobe as threads de envio e recebimento.
    O fluxo de entrada (apelido e sala) será implementado na Parte 3.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
        print(f"[CLIENTE] Conectado ao servidor {HOST}:{PORT}\n")

        # TODO (Parte 3): receber prompt de apelido do servidor e responder
        # TODO (Parte 3): receber prompt de sala do servidor e responder

        # Thread de recebimento roda em segundo plano (daemon)
        thread_recv = threading.Thread(
            target=receber_mensagens,
            args=(sock,),
            daemon=True
        )
        thread_recv.start()

        # Envio roda na thread atual
        enviar_mensagens(sock)

    except ConnectionRefusedError:
        print(f"[CLIENTE] Não foi possível conectar em {HOST}:{PORT}.")
        print("[CLIENTE] Verifique se o servidor está rodando.")

    finally:
        sock.close()


# Ponto de entrada
if __name__ == "__main__":
    iniciar_cliente()