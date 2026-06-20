# client.py — Cliente TCP do Chat

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
                print("[CLIENTE] Conexão encerrada pelo servidor.")
                break
            print(mensagem)

        except Exception:
            print("[CLIENTE] Conexão perdida.")
            break


# Thread de envio
# Fica em loop lendo o input do usuário e mandando pro servidor
def enviar_mensagens(sock):
    """
    Lê o input do usuário e envia ao servidor.
    Também interpreta /sair para encerrar o cliente localmente.

    Parâmetros:
        sock (socket): socket conectado ao servidor
    """
    while True:
        try:
            mensagem = input()
            if not mensagem:
                continue
            sock.send(mensagem.encode("utf-8"))

            # Encerra o cliente após enviar /sair ao servidor
            if mensagem.strip().lower() == "/sair":
                break

        except (EOFError, KeyboardInterrupt):
            print("\n[CLIENTE] Encerrando...")
            sock.send("/sair".encode("utf-8"))
            break

        except Exception as e:
            print(f"[CLIENTE] Erro ao enviar: {e}")
            break


# Inicialização do cliente
def iniciar_cliente():
    """
    Conecta ao servidor, realiza o fluxo de entrada (apelido e sala)
    e sobe as threads de envio e recebimento.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
        print(f"[CLIENTE] Conectado ao servidor {HOST}:{PORT}\n")

        # Fluxo de entrada: recebe prompts do servidor e responde
        # O servidor envia "Digite seu apelido: " e aguarda a resposta
        prompt_apelido = sock.recv(1024).decode("utf-8")
        print(prompt_apelido, end="", flush=True)
        apelido = input()
        sock.send(apelido.encode("utf-8"))

        # O servidor envia a lista de salas e pede para escolher uma
        prompt_sala = sock.recv(1024).decode("utf-8")
        print(prompt_sala, end="", flush=True)
        sala = input()
        sock.send(sala.encode("utf-8"))

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