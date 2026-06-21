# server.py — Servidor TCP do Chat

import socket
import threading

# Configurações do servidor
HOST = "0.0.0.0"    # Aceita conexões de qualquer interface de rede
PORT = 5555         # Porta que o servidor vai escutar


# Estado global do servidor
salas = {}          # { "nome_da_sala": [{"conn": conn, "apelido": "X"}, ...] }
lock = threading.Lock()  # Garante acesso seguro ao dicionário entre threads


# Envia uma mensagem para todos os clientes de uma sala, exceto o remetente
def broadcast(sala, mensagem, remetente_conn=None):
    with lock:
        for cliente in salas.get(sala, []):
            if cliente["conn"] != remetente_conn:
                try:
                    cliente["conn"].send(mensagem.encode("utf-8"))
                except Exception:
                    pass


# Adiciona um cliente a uma sala, criando-a se não existir
def adicionar_cliente(sala, conn, apelido):
    with lock:
        if sala not in salas:
            salas[sala] = []
        salas[sala].append({"conn": conn, "apelido": apelido})


# Remove um cliente de uma sala, apagando a sala se ficar vazia
def remover_cliente(sala, conn):
    with lock:
        if sala in salas:
            salas[sala] = [c for c in salas[sala] if c["conn"] != conn]
            if not salas[sala]:
                del salas[sala]


# Retorna uma string listando as salas ativas e seus ocupantes
def listar_salas():
    with lock:
        if not salas:
            return "Nenhuma sala disponível no momento."
        linhas = ["Salas disponíveis:"]
        for nome, clientes in salas.items():
            apelidos = ", ".join(c["apelido"] for c in clientes)
            linhas.append(f"  #{nome} ({len(clientes)} pessoa(s)): {apelidos}")
        return "\n".join(linhas)


# Função que trata cada cliente em sua própria thread
def handle_client(conn, addr):
    """
    Executada em uma thread separada para cada cliente conectado.

    Parâmetros:
        conn (socket): conexão estabelecida com o cliente
        addr (tuple): endereço do cliente (ip, porta)
    """
    print(f"[SERVIDOR] Nova conexão: {addr}")
    apelido = None
    sala_atual = None

    try:
        # Solicitar apelido ao cliente
        conn.send("Digite seu apelido: ".encode("utf-8"))
        apelido = conn.recv(1024).decode("utf-8").strip()
        if not apelido:
            apelido = f"user_{addr[1]}"
        print(f"[SERVIDOR] {addr} entrou como '{apelido}'")

        # Solicitar sala ao cliente
        conn.send(f"\nBem-vindo, {apelido}!\n{listar_salas()}\nDigite o nome da sala para entrar (ou crie uma nova): ".encode("utf-8"))
        sala_atual = conn.recv(1024).decode("utf-8").strip().lower()
        if not sala_atual:
            sala_atual = "geral"

        # Entrar na sala e notificar os demais
        adicionar_cliente(sala_atual, conn, apelido)
        conn.send(f"\nVocê entrou na sala #{sala_atual}. Digite /ajuda para ver os comandos.\n".encode("utf-8"))
        broadcast(sala_atual, f"[{apelido} entrou na sala #{sala_atual}]", remetente_conn=conn)
        print(f"[SERVIDOR] '{apelido}' entrou na sala '{sala_atual}'")

        # Loop de recebimento de mensagens e comandos
        while True:
            dados = conn.recv(1024).decode("utf-8").strip()
            if not dados:
                break

            if dados.startswith("/"):
                partes = dados.split(" ", 1)
                comando = partes[0].lower()

                if comando == "/sair":
                    conn.send("Até logo!".encode("utf-8"))
                    break

                elif comando == "/salas":
                    conn.send(listar_salas().encode("utf-8"))

                elif comando == "/ajuda":
                    ajuda = (
                        "Comandos disponíveis:\n"
                        "  /salas          → lista as salas e seus ocupantes\n"
                        "  /trocar <sala>  → muda para outra sala\n"
                        "  /sair           → desconecta do servidor\n"
                        "  /ajuda          → exibe esta mensagem"
                    )
                    conn.send(ajuda.encode("utf-8"))

                elif comando == "/trocar":
                    if len(partes) < 2 or not partes[1].strip():
                        conn.send("Uso: /trocar <nome_da_sala>".encode("utf-8"))
                    else:
                        nova_sala = partes[1].strip().lower()
                        if nova_sala == sala_atual:
                            conn.send(f"Você já está na sala #{nova_sala}.".encode("utf-8"))
                        else:
                            broadcast(sala_atual, f"[{apelido} saiu da sala #{sala_atual}]", remetente_conn=conn)
                            remover_cliente(sala_atual, conn)
                            sala_atual = nova_sala
                            adicionar_cliente(sala_atual, conn, apelido)
                            conn.send(f"Você entrou na sala #{sala_atual}.".encode("utf-8"))
                            broadcast(sala_atual, f"[{apelido} entrou na sala #{sala_atual}]", remetente_conn=conn)
                            print(f"[SERVIDOR] '{apelido}' trocou para a sala '{sala_atual}'")

                else:
                    conn.send(f"Comando desconhecido: {comando}. Digite /ajuda.".encode("utf-8"))

            else:
                mensagem_formatada = f"[#{sala_atual}] {apelido}: {dados}"
                broadcast(sala_atual, mensagem_formatada, remetente_conn=conn)
                print(f"[SERVIDOR] {mensagem_formatada}")

    except ConnectionResetError:
        print(f"[SERVIDOR] '{apelido}' desconectou abruptamente.")

    except Exception as e:
        print(f"[SERVIDOR] Erro com {addr}: {e}")

    finally:
        # Remover cliente da sala e notificar os demais
        if sala_atual and apelido:
            remover_cliente(sala_atual, conn)
            broadcast(sala_atual, f"[{apelido} saiu do chat]")
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