import socket
import threading

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor (localhost)
PORT = 12345        # Porta que o servidor estará escutando

# Dicionário para armazenar as informações dos usuários e grupos
usuarios = {}
grupos = {}
clientes = []
pedidos_ingresso = {}

# Função para gerenciar as mensagens recebidas de um cliente
def gerenciar_cliente(conn, addr):
    # Receber informações do usuário
    usuario_info = conn.recv(1024).decode('utf-8').split(';')
    email, nome, localizacao = usuario_info
    usuarios[email] = (nome, localizacao, conn)
    clientes.append(conn)
    print(f"{nome} ({email}, {localizacao}) conectado.")

    while True:
        try:
            mensagem = conn.recv(1024).decode('utf-8')
            if mensagem.startswith('/perfil'):
                email_consulta = mensagem.split(' ')[1]
                consultar_perfil(email_consulta, conn)
            elif mensagem.startswith('/grupo'):
                criar_grupo(mensagem, conn)
            elif mensagem.startswith('/convidar'):
                convidar_usuario(mensagem, conn)
            elif mensagem.startswith('/aceitar_convite'):
                aceitar_convite(mensagem, conn)
            elif mensagem.startswith('/recusar_convite'):
                recusar_convite(mensagem, conn)
            elif mensagem.startswith('/excluir'):
                excluir_usuario(mensagem, conn)
            elif mensagem.startswith('/mensagem_grupo'):
                enviar_mensagem_grupo(mensagem, conn)
            elif mensagem.startswith('/listar_grupos'):
                listar_grupos(email, conn)
            elif mensagem.startswith('/membros_grupo'):
                nome_grupo = mensagem.split(' ')[1]
                listar_membros_grupo(nome_grupo, conn)
            elif mensagem.startswith('/pedir_ingresso'):
                pedir_ingresso(mensagem, conn)
            elif mensagem.startswith('/aceitar_pedido'):
                aceitar_pedido(mensagem, conn)
            elif mensagem.startswith('/recusar_pedido'):
                recusar_pedido(mensagem, conn)
            elif mensagem.startswith('/sair_grupo'):
                sair_grupo(mensagem, conn)
            else:
                mensagem_completa = f"{usuarios[email][0]}: {mensagem}"
                print(mensagem_completa)
                transmitir_mensagem(mensagem_completa, conn)
        except:
            desconectar_cliente(conn)
            break

# Função para transmitir a mensagem recebida para todos os clientes
def transmitir_mensagem(mensagem, conn):
    for cliente in clientes:
        try:
            cliente.send(mensagem.encode('utf-8'))
        except:
            desconectar_cliente(cliente)

# Função para consultar o perfil de um usuário
def consultar_perfil(email, conn):
    if email in usuarios:
        nome, localizacao, _ = usuarios[email]
        perfil_info = f"Perfil de {email} - Nome: {nome}, Localização: {localizacao}"
    else:
        perfil_info = f"Perfil de {email} não encontrado."
    conn.send(perfil_info.encode('utf-8'))

# Função para criar um grupo
def criar_grupo(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    emails_membros = partes[2:]

    if nome_grupo in grupos:
        conn.send(f"Grupo {nome_grupo} já existe.".encode('utf-8'))
        return

    membros = [conn]  # Inclui o criador do grupo
    administradores = {conn}
    for email in emails_membros:
        if email in usuarios:
            membros.append(usuarios[email][2])
        else:
            conn.send(f"Usuário {email} não encontrado.".encode('utf-8'))
            return

    grupos[nome_grupo] = {'membros': membros, 'administradores': administradores, 'convites': {}, 'pedidos': {}}
    membros_emails = [email for email in emails_membros if email in usuarios] + [email for email, (_, _, cliente) in usuarios.items() if cliente == conn]
    membros_info = f"Membros do grupo {nome_grupo}: " + ', '.join(membros_emails)
    for membro in membros:
        membro.send(membros_info.encode('utf-8'))

# Função para convidar um usuário para um grupo
def convidar_usuario(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email_novo_membro = partes[2]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if conn not in grupos[nome_grupo]['administradores']:
        conn.send("Você não tem permissão para convidar novos membros para este grupo.".encode('utf-8'))
        return

    if email_novo_membro not in usuarios:
        conn.send(f"Usuário {email_novo_membro} não encontrado.".encode('utf-8'))
        return

    novo_membro = usuarios[email_novo_membro][2]
    if novo_membro in grupos[nome_grupo]['membros']:
        conn.send(f"Usuário {email_novo_membro} já é membro do grupo {nome_grupo}.".encode('utf-8'))
        return

    grupos[nome_grupo]['convites'][email_novo_membro] = novo_membro
    novo_membro.send(f"Você foi convidado para o grupo {nome_grupo}. Aceite ou recuse o convite ".encode('utf-8'))
    conn.send(f"Usuário {email_novo_membro} foi convidado para o grupo {nome_grupo}.".encode('utf-8'))

# Função para aceitar convite
def aceitar_convite(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email = [email for email, (_, _, cliente) in usuarios.items() if cliente == conn][0]

    if nome_grupo not in grupos or email not in grupos[nome_grupo]['convites']:
        conn.send(f"Convite para o grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    grupos[nome_grupo]['membros'].append(conn)
    grupos[nome_grupo]['convites'].pop(email)
    conn.send(f"Você agora é membro do grupo {nome_grupo}.".encode('utf-8'))

    # Notificar os membros do grupo
    membros = grupos[nome_grupo]['membros']
    for membro in membros:
        if membro != conn:
            membro.send(f"{usuarios[email][0]} entrou no grupo {nome_grupo}".encode('utf-8'))

# Função para recusar convite
def recusar_convite(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email = [email for email, (_, _, cliente) in usuarios.items() if cliente == conn][0]

    if nome_grupo not in grupos or email not in grupos[nome_grupo]['convites']:
        conn.send(f"Convite para o grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    grupos[nome_grupo]['convites'].pop(email)
    conn.send(f"Você recusou o convite para o grupo {nome_grupo}.".encode('utf-8'))

# Função para excluir um usuário de um grupo
def excluir_usuario(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email_usuario = partes[2]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if conn not in grupos[nome_grupo]['administradores']:
        conn.send("Você não tem permissão para excluir usuários deste grupo.".encode('utf-8'))
        return

    if email_usuario not in usuarios:
        conn.send(f"Usuário {email_usuario} não encontrado.".encode('utf-8'))
        return

    usuario_a_excluir = usuarios[email_usuario][2]
    if usuario_a_excluir not in grupos[nome_grupo]['membros']:
        conn.send(f"Usuário {email_usuario} não é membro do grupo {nome_grupo}.".encode('utf-8'))
        return

    grupos[nome_grupo]['membros'].remove(usuario_a_excluir)
    usuario_a_excluir.send(f"Você foi excluído do grupo {nome_grupo}.".encode('utf-8'))

    # Notificar os membros restantes do grupo
    for membro in grupos[nome_grupo]['membros']:
        membro.send(f"Usuário {email_usuario} foi excluído do grupo {nome_grupo}.".encode('utf-8'))

# Função para enviar mensagem ao grupo
def enviar_mensagem_grupo(mensagem, conn):
    partes = mensagem.split(' ', 2)
    nome_grupo = partes[1]
    conteudo_mensagem = partes[2]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    nome_remetente = None
    for email, (nome, _, cliente) in usuarios.items():
        if cliente == conn:
            nome_remetente = nome
            break

    if not nome_remetente:
        conn.send("Erro ao identificar o remetente.".encode('utf-8'))
        return

    membros = grupos[nome_grupo]['membros']
    for membro in membros:
        membro.send(f"(Grupo - {nome_grupo}) {nome_remetente}: {conteudo_mensagem}".encode('utf-8'))

# Função para listar os grupos em que um usuário está inserido
def listar_grupos(email, conn):
    grupos_usuario = [nome_grupo for nome_grupo, dados in grupos.items() if usuarios[email][2] in dados['membros']]
    grupos_info = "Grupos: " + ', '.join(grupos_usuario) if grupos_usuario else "Você não está em nenhum grupo."
    conn.send(grupos_info.encode('utf-8'))

# Função para listar os membros de um grupo
def listar_membros_grupo(nome_grupo, conn):
    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    membros_emails = [email for email, (_, _, cliente) in usuarios.items() if cliente in grupos[nome_grupo]['membros']]
    membros_info = f"Membros do grupo {nome_grupo}: " + ', '.join(membros_emails)
    conn.send(membros_info.encode('utf-8'))

# Função para pedir ingresso em um grupo
def pedir_ingresso(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email = [email for email, (_, _, cliente) in usuarios.items() if cliente == conn][0]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if email in grupos[nome_grupo]['pedidos']:
        conn.send(f"Você já solicitou ingresso ao grupo {nome_grupo}.".encode('utf-8'))
        return

    grupos[nome_grupo]['pedidos'][email] = conn
    for administrador in grupos[nome_grupo]['administradores']:
        administrador.send(f"Usuário {email} solicitou ingresso ao grupo {nome_grupo}. Aceite ou recuse o pedido.".encode('utf-8'))

# Função para aceitar pedido de ingresso
def aceitar_pedido(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email_novo_membro = partes[2]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if conn not in grupos[nome_grupo]['administradores']:
        conn.send("Você não tem permissão para aceitar novos membros para este grupo.".encode('utf-8'))
        return

    if email_novo_membro not in grupos[nome_grupo]['pedidos']:
        conn.send(f"Pedido de ingresso do usuário {email_novo_membro} não encontrado.".encode('utf-8'))
        return

    novo_membro_conn = grupos[nome_grupo]['pedidos'].pop(email_novo_membro)
    grupos[nome_grupo]['membros'].append(novo_membro_conn)
    novo_membro_conn.send(f"Você foi aceito no grupo {nome_grupo}.".encode('utf-8'))

    # Notificar os membros do grupo
    membros = grupos[nome_grupo]['membros']
    for membro in membros:
        membro.send(f"{usuarios[email_novo_membro][0]} entrou no grupo {nome_grupo}".encode('utf-8'))

# Função para recusar pedido de ingresso
def recusar_pedido(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email_novo_membro = partes[2]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if conn not in grupos[nome_grupo]['administradores']:
        conn.send("Você não tem permissão para recusar novos membros para este grupo.".encode('utf-8'))
        return

    if email_novo_membro not in grupos[nome_grupo]['pedidos']:
        conn.send(f"Pedido de ingresso do usuário {email_novo_membro} não encontrado.".encode('utf-8'))
        return

    grupos[nome_grupo]['pedidos'].pop(email_novo_membro)
    usuarios[email_novo_membro][2].send(f"Seu pedido de ingresso ao grupo {nome_grupo} foi recusado.".encode('utf-8'))

# Função para um usuário sair de um grupo
def sair_grupo(mensagem, conn):
    partes = mensagem.split(' ')
    nome_grupo = partes[1]
    email_usuario = [email for email, (_, _, cliente) in usuarios.items() if cliente == conn][0]

    if nome_grupo not in grupos:
        conn.send(f"Grupo {nome_grupo} não encontrado.".encode('utf-8'))
        return

    if conn not in grupos[nome_grupo]['membros']:
        conn.send(f"Você não é membro do grupo {nome_grupo}.".encode('utf-8'))
        return

    grupos[nome_grupo]['membros'].remove(conn)
    conn.send(f"Você saiu do grupo {nome_grupo}.".encode('utf-8'))

    # Notificar os membros restantes do grupo
    for membro in grupos[nome_grupo]['membros']:
        membro.send(f"Usuário {email_usuario} saiu do grupo {nome_grupo}.".encode('utf-8'))

# Função para desconectar um cliente
def desconectar_cliente(conn):
    try:
        clientes.remove(conn)
        for email, (_, _, cliente) in usuarios.items():
            if cliente == conn:
                del usuarios[email]
                break
        conn.close()
    except:
        pass

# Função principal para iniciar o servidor
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    print(f"Servidor iniciado em {HOST}:{PORT}")

    while True:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=gerenciar_cliente, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()
