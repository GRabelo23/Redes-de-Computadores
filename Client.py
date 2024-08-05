import socket
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import threading

# Funções de envio
def enviar_mensagem():
    mensagem = mensagem_entry.get()
    if mensagem:
        cliente_socket.send(mensagem.encode('utf-8'))
        mensagem_entry.delete(0, tk.END)

def enviar_mensagem_grupo():
    nome_grupo = grupo_entry.get()
    mensagem = mensagem_entry.get()
    if mensagem and nome_grupo:
        cliente_socket.send(f"/mensagem_grupo {nome_grupo} {mensagem}".encode('utf-8'))
        mensagem_entry.delete(0, tk.END)

def convidar_usuario():
    nome_grupo = simpledialog.askstring("Convidar usuário", "Digite o nome do grupo:")
    email_usuario = simpledialog.askstring("Convidar usuário", "Digite o email do usuário:")
    if nome_grupo and email_usuario:
        cliente_socket.send(f"/convidar {nome_grupo} {email_usuario}".encode('utf-8'))

def consultar_perfil():
    email = simpledialog.askstring("Consultar perfil", "Digite o email do usuário:")
    if email:
        cliente_socket.send(f"/perfil {email}".encode('utf-8'))

def criar_grupo():
    nome_grupo = simpledialog.askstring("Criar grupo", "Digite o nome do grupo:")
    emails_membros = simpledialog.askstring("Criar grupo", "Digite os emails dos membros separados por espaço:")
    if nome_grupo and emails_membros:
        cliente_socket.send(f"/grupo {nome_grupo} {emails_membros}".encode('utf-8'))

def listar_grupos():
    cliente_socket.send("/listar_grupos".encode('utf-8'))

def listar_membros_grupo():
    nome_grupo = simpledialog.askstring("Listar membros do grupo", "Digite o nome do grupo:")
    if nome_grupo:
        cliente_socket.send(f"/membros_grupo {nome_grupo}".encode('utf-8'))

def aceitar_convite():
    nome_grupo = simpledialog.askstring("Aceitar convite", "Digite o nome do grupo:")
    if nome_grupo:
        cliente_socket.send(f"/aceitar_convite {nome_grupo}".encode('utf-8'))

def recusar_convite():
    nome_grupo = simpledialog.askstring("Recusar convite", "Digite o nome do grupo:")
    if nome_grupo:
        cliente_socket.send(f"/recusar_convite {nome_grupo}".encode('utf-8'))

def excluir_usuario():
    nome_grupo = simpledialog.askstring("Excluir usuário", "Digite o nome do grupo:")
    email_usuario = simpledialog.askstring("Excluir usuário", "Digite o email do usuário:")
    if nome_grupo and email_usuario:
        cliente_socket.send(f"/excluir {nome_grupo} {email_usuario}".encode('utf-8'))

def limpar_chat():
    mensagens_text.config(state=tk.NORMAL)
    mensagens_text.delete(1.0, tk.END)
    mensagens_text.config(state=tk.DISABLED)

def pedir_ingresso():
    nome_grupo = simpledialog.askstring("Pedir ingresso", "Digite o nome do grupo:")
    if nome_grupo:
        cliente_socket.send(f"/pedir_ingresso {nome_grupo}".encode('utf-8'))

def aceitar_pedido():
    nome_grupo = simpledialog.askstring("Aceitar pedido", "Digite o nome do grupo:")
    email_usuario = simpledialog.askstring("Aceitar pedido", "Digite o email do usuário:")
    if nome_grupo and email_usuario:
        cliente_socket.send(f"/aceitar_pedido {nome_grupo} {email_usuario}".encode('utf-8'))

def recusar_pedido():
    nome_grupo = simpledialog.askstring("Recusar pedido", "Digite o nome do grupo:")
    email_usuario = simpledialog.askstring("Recusar pedido", "Digite o email do usuário:")
    if nome_grupo and email_usuario:
        cliente_socket.send(f"/recusar_pedido {nome_grupo} {email_usuario}".encode('utf-8'))

def sair_grupo():
    nome_grupo = simpledialog.askstring("Sair do grupo", "Digite o nome do grupo:")
    if nome_grupo:
        cliente_socket.send(f"/sair_grupo {nome_grupo}".encode('utf-8'))

# Configuração do socket do cliente
HOST = '127.0.0.1'
PORT = 12345

cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente_socket.connect((HOST, PORT))

# Solicitar informações do usuário
email = simpledialog.askstring("Email", "Digite seu email:")
nome = simpledialog.askstring("Nome", "Digite seu nome:")
localizacao = simpledialog.askstring("Localização", "Digite sua localização:")

# Enviar informações do usuário para o servidor
cliente_socket.send(f"{email};{nome};{localizacao}".encode('utf-8'))

# Interface gráfica com tkinter
root = tk.Tk()
root.title("Chat")

# Layout com grid
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

mensagens_frame = tk.Frame(main_frame)
mensagens_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

scrollbar = tk.Scrollbar(mensagens_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

mensagens_text = scrolledtext.ScrolledText(mensagens_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, state=tk.DISABLED, height=15, width=60)
mensagens_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=mensagens_text.yview)

entrada_frame = tk.Frame(main_frame)
entrada_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

mensagem_entry = tk.Entry(entrada_frame, width=40)
mensagem_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
mensagem_entry.bind("<Return>", lambda event: enviar_mensagem())

enviar_button = tk.Button(entrada_frame, text="Enviar", command=enviar_mensagem)
enviar_button.grid(row=0, column=1, padx=5, pady=5)

grupo_entry = tk.Entry(entrada_frame, width=20)
grupo_entry.grid(row=0, column=2, padx=5, pady=5)
grupo_entry.insert(0, "Nome do Grupo")

enviar_grupo_button = tk.Button(entrada_frame, text="Enviar ao Grupo", command=enviar_mensagem_grupo)
enviar_grupo_button.grid(row=0, column=3, padx=5, pady=5)

buttons_frame = tk.Frame(main_frame)
buttons_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky='ew')

consultar_button = tk.Button(buttons_frame, text="Consultar perfil", command=consultar_perfil)
consultar_button.grid(row=0, column=0, padx=5, pady=5)

criar_grupo_button = tk.Button(buttons_frame, text="Criar grupo", command=criar_grupo)
criar_grupo_button.grid(row=0, column=1, padx=5, pady=5)

listar_grupos_button = tk.Button(buttons_frame, text="Listar grupos", command=listar_grupos)
listar_grupos_button.grid(row=0, column=2, padx=5, pady=5)

listar_membros_button = tk.Button(buttons_frame, text="Listar membros do grupo", command=listar_membros_grupo)
listar_membros_button.grid(row=0, column=3, padx=5, pady=5)

convidar_button = tk.Button(buttons_frame, text="Convidar Usuário", command=convidar_usuario)
convidar_button.grid(row=1, column=0, padx=5, pady=5)

aceitar_button = tk.Button(buttons_frame, text="Aceitar Convite", command=aceitar_convite)
aceitar_button.grid(row=1, column=1, padx=5, pady=5)

recusar_button = tk.Button(buttons_frame, text="Recusar Convite", command=recusar_convite)
recusar_button.grid(row=1, column=2, padx=5, pady=5)

excluir_button = tk.Button(buttons_frame, text="Excluir Usuário", command=excluir_usuario)
excluir_button.grid(row=1, column=3, padx=5, pady=5)

pedir_ingresso_button = tk.Button(buttons_frame, text="Pedir Ingresso", command=pedir_ingresso)
pedir_ingresso_button.grid(row=2, column=0, padx=5, pady=5)

aceitar_pedido_button = tk.Button(buttons_frame, text="Aceitar Pedido", command=aceitar_pedido)
aceitar_pedido_button.grid(row=2, column=1, padx=5, pady=5)

recusar_pedido_button = tk.Button(buttons_frame, text="Recusar Pedido", command=recusar_pedido)
recusar_pedido_button.grid(row=2, column=2, padx=5, pady=5)

sair_grupo_button = tk.Button(buttons_frame, text="Sair do Grupo", command=sair_grupo)
sair_grupo_button.grid(row=2, column=3, padx=5, pady=5)

limpar_chat_button = tk.Button(buttons_frame, text="Limpar chat", command=limpar_chat)
limpar_chat_button.grid(row=2, column=4, padx=5, pady=5)

# Função para receber mensagens
def receber_mensagens():
    while True:
        try:
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            mensagens_text.config(state=tk.NORMAL)
            mensagens_text.insert(tk.END, mensagem + '\n')
            mensagens_text.config(state=tk.DISABLED)
            mensagens_text.yview(tk.END)
        except:
            break

# Iniciar thread para receber mensagens
receber_thread = threading.Thread(target=receber_mensagens)
receber_thread.daemon = True
receber_thread.start()

root.mainloop()
