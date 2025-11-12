from time import sleep

def linha(largura=42):
    return "-" * largura


def cabecalho(txt="MENU PRINCIPAL", largura=60):
    barra = linha(largura)
    print(barra)
    print(txt.center(len(barra)))
    print(barra)


def menu(*opcoes, conta_corrente=None, largura=60):
    cabecalho(f"MENU PRINCIPAL - Agência: 0001 - Conta Corrente: {conta_corrente} ", largura=largura)
    for i, item in enumerate(opcoes, start=1):
        print(f"{i} - {item}")
    barra = '-' * largura
    print(barra)
    prompt = "Escolha uma opção:  "
    prompt_preenchido = prompt.ljust(len(barra) - 1)
    print(prompt_preenchido, end="")

    try:
        valor = int(input().strip())
    except ValueError:
        return 0
    return valor


def arquivo_existe(nome_arquivo):
    try:
        arquivo = open(nome_arquivo, 'rt') 
        arquivo.close()
    except FileNotFoundError:
        return False
    else:
        return True


def criar_arquivo(nome_arquivo):
    try:
        arquivo = open(nome_arquivo, 'wt+')
        arquivo.close()
    except:
        print(f'Houve um ERRO ao criar o arquivo')
    else:
        print(f' >>> Arquivo {nome_arquivo} criado com sucesso! <<< ')


def ler_usuario_com_saldo(cpf, conta_corrente, ARQ):
    try:
        with open(ARQ, 'r') as arq:
            for linha in arq:
                partes = linha.strip().split(';')
                if len(partes) == 6:
                    nome, data_nascimento, cpf_lido, endereco, conta_corrente, saldo = partes
                    if cpf.strip() == cpf_lido.strip():
                        return {
                            'nome': nome,
                            'data_de_nascimento': data_nascimento,
                            'cpf': cpf_lido,
                            'endereco': endereco,
                            'conta_corrente': int(conta_corrente),
                            'saldo': float(saldo)
                        }
        return None  
    except FileNotFoundError:
        print("Arquivo não encontrado!")
        return None


def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    if valor > saldo:
        print(f'>>> Operação falhou! Saldo insuficiente. <<< ')
    elif valor > limite:
        print(f'>>> Operação falhou! O valor do saque excede o limite. <<< ')
    elif numero_saques >= limite_saques:
        print(f'>>> Operação falhou! Número máximo de saques diários excedido. <<< ')
    elif valor > 0:
        saldo -= valor
        extrato += f'Saque: R$ {valor:.2f}\n'
        numero_saques += 1
        print(f'>>> Saque de R$ {valor:.2f} realizado com sucesso! <<< ')
    else:
        print(f'>>> Operação falhou! O valor informado é inválido. <<< ')
    return saldo, extrato, numero_saques


def depositar(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f'Depósito: R$ {valor:.2f}\n'
        print(f'>>> Depósito de R$ {valor:.2f} realizado com sucesso! <<< ')
    else:
        print(f'>>> Operação falhou! O valor informado é inválido. <<< ')
    return saldo, extrato


def historico(saldo, extrato):
    cabecalho('EXTRATO BANCÁRIO')
    if not extrato:
        print(">>> Não foram realizadas movimentações recentes. <<< ")
    else:
        print(extrato)
    print(f'Saldo: R$ {saldo:.2f}')
    print(f'{linha()}')


def cadastrar(ARQ, cpf, nome, data_de_nascimento, endereco, conta_corrente=None, saldo=0.0):
    try:
        a = open(ARQ, 'at')  # append text 
    except:
        print(f' >>> Houve um ERRO na abertura do arquivo <<< ')
    else:
        try:
            a.write(f'{nome};{data_de_nascimento};{cpf};{endereco};{conta_corrente};{saldo}\n')
        except:
            print(f' >>> Houve um ERRO ao escrever os dados <<< ')
        else:
            print(f'>>> Novo registro de {nome} adicionado <<< ')
            a.close()


def nova_conta_corrente(*conta_corrente):
    global AGENCIA 
    AGENCIA = '0001' 

    qty_contas = list(conta_corrente)  
    conta_corrente_criada = len(qty_contas) + 1 if qty_contas else 1
    return {'agencia': AGENCIA, 'conta_corrente': conta_corrente_criada}


def atualizar_saldo_no_arquivo(cpf, saldo, conta_corrente, ARQ):
    actual_saldo = float(saldo)
    linhas_novas = []
    with open(ARQ, 'r') as arq:
        for linha in arq:
            linha_original = linha.strip('\n')
            if not linha_original:
                continue

            partes = linha.strip().split(';')

            if len(partes) >= 6:
                if partes[2].strip() == cpf.strip() and partes[4].strip() == str(conta_corrente).strip():
                    partes[-1] = f'{actual_saldo:.2f}'
                    linha_original = ';'.join(partes) 
            linhas_novas.append(linha_original)

    with open(ARQ, 'w') as arq:
            arq.write('\n'.join(linhas_novas)+'\n')


def opcao1( saldo, extrato, numero_saques, conta_corrente, cpf, ARQ):

    list_contas = ler_contas_usuario(cpf, ARQ)

    cabecalho('QUAL CONTA DESEJA ACESSAR?')
    
    for i, conta in enumerate(list_contas, start=1):
        print(f"{i} - Agência: 0001 - Conta Corrente: {conta['conta_corrente']}")
    
    escolha = 0
    while escolha < 1 or escolha > len(list_contas):
        try:
            escolha = int(input('Digite o número refente a conta: '))
        except ValueError:
            print('>>> OPÇÃO INVÁLIDA - Tente novamente <<<')
    conta_escolhida = list_contas[escolha - 1]

    saldo = float(conta_escolhida.get('saldo', 0.0))
    extrato = ''
    numero_saques = 0
    conta_corrente = conta_escolhida['conta_corrente'] 
    return (saldo, extrato, numero_saques, conta_corrente)


def util_menu(saldo, extrato, numero_saques, limite, limite_saques, cpf, nome, conta_corrente, data_de_nascimento, endereco, ARQ):
    while True:
        atualizar_saldo_no_arquivo( cpf, saldo, conta_corrente, ARQ)
        print(f'Agência: 0001 - C/c: {conta_corrente}')
        opcao = menu('LISTAR CONTAS', 'SALDO', 'SAQUE', 'DEPÓSITO', 'EXTRATO', 'NOVA CONTA CORRENTE','SAIR DO SISTEMA', conta_corrente=conta_corrente)

        if opcao == 1:
            saldo, extrato, numero_saques, conta_corrente = opcao1(saldo, extrato, numero_saques, conta_corrente, cpf, ARQ)
            sleep(1)
            
        elif opcao == 2:
            print(f'Saldo atual: R$ {saldo:.2f}')
            sleep(1)

        elif opcao == 3:
            valor = float(input('Digite o valor do saque: '))
            saldo, extrato, numero_saques = sacar(
            saldo=saldo, valor=valor, extrato=extrato,
            limite=limite, numero_saques=numero_saques, limite_saques=limite_saques)
            print(f'Saldo atual: R$ {saldo:.2f}')
            sleep(1)
        elif opcao == 4:
            valor = float(input('Digite o valor do depósito: '))
            saldo, extrato = depositar(saldo, valor, extrato)
            print(f'Saldo atual: R$ {saldo:.2f}')
            sleep(1)
        elif opcao == 5:
            historico(saldo, extrato)
            sleep(1)
        elif opcao == 6:
            qty_contas=[]
            try:
                with open(ARQ, 'r') as arq:
                    for linha in arq:
                        partes = linha.strip().split(';')
                        if len(partes) >= 5:
                            conta_corrente = int(partes[4])
                            qty_contas.append(int(partes[4]))
            except FileNotFoundError:
                print("Arquivo não encontrado!")

            agencia_conta_corrente = nova_conta_corrente(*qty_contas)
            conta_corrente = agencia_conta_corrente['conta_corrente']  

            cadastrar(ARQ, cpf, nome, data_de_nascimento, endereco, conta_corrente, saldo=0.0)

            print(f'>>> Conta criada com sucesso! <<< ')
            sleep(0.5)
            print(f'Sua nova conta corrente foi criada: 0001-{conta_corrente}')
            sleep(0.5)

            opcao1( saldo, extrato, numero_saques, conta_corrente, cpf, ARQ)

        elif opcao == 7:
            print('Obrigado por usar nosso sistema bancário. Até logo!')
            sleep(1)
            break
        else:
            print(f'>>> OPÇÃO INVÁLIDA - Tente novamente <<<')
            sleep(1)
            continue


def dados_cadastro():
        nome = input('Digite seu nome completo: ').strip().title()
        dados['nome'] = nome
        print('Data de nascimento')
        dia_de_nascimento = int(input('Digite o dia de nascimento (dd): '))
        mes_de_nascimento = int(input('Digite o mês de nascimento (mm): '))
        ano_de_nascimento = int(input('Digite o ano de nascimento (aaaa): '))
        data_de_nascimento = f'{dia_de_nascimento}/{mes_de_nascimento}/{ano_de_nascimento}'
        dados['data_de_nascimento'] = data_de_nascimento
        print('Endereço')
        rua = input('Digite o logradouro: ').strip().title()
        nro = input('Digite o número: ').strip()
        complemento = input('Digite o complemento: ').strip()
        bairro = input('Digite o bairro: ').strip().title()
        cidade = input('Digite a cidade: ').strip().title()
        estado = input('Digite o estado (sigla): ').strip().upper()
        endereco = f'{rua}, {nro}/{complemento} - {bairro} - {cidade}/{estado}'
        dados['endereco'] = endereco
        return nome, data_de_nascimento, endereco


def ler_contas_usuario(cpf, ARQ):
    list_contas = []
    try:
        with open(ARQ, 'r') as arq:
            for linha in arq:
                partes = linha.strip().split(';')
                if len(partes) >= 6:
                    nome, data_de_nascimento, cpf_lido, endereco, conta_corrente, saldo_str = partes[:6]
                    if cpf.strip() == cpf_lido.strip():
                        list_contas.append({
                            'nome': nome,
                            'data_de_nascimento': data_de_nascimento,
                            'cpf': cpf_lido,
                            'endereco': endereco,
                            'conta_corrente': conta_corrente,
                            'saldo': float(saldo_str)
                        })
    except FileNotFoundError:
        print("Arquivo não encontrado!")
    return list_contas



# PROGRAMA PRINCIPAL

ARQ = 'cadastro.txt'
if not arquivo_existe(ARQ):
    criar_arquivo(ARQ)

dados = {}
saldo = 0.0
extrato = ''
limite = 500
limite_saques = 3
numero_saques = 0
conta = 0

while True:
    cpf = (input('Digite o CPF (apenas números): ')).strip()

    while not (cpf.isdigit() and len(cpf) == 11):
        print(f'>>> CPF INVÁLIDO - Tente novamente <<<')
        cpf = input('Digite o CPF (apenas números): ').strip()

    dic_usuario = ler_usuario_com_saldo(cpf, conta, ARQ)
    if dic_usuario:
        saldo = dic_usuario['saldo']
        nome = dic_usuario['nome']
        conta = dic_usuario['conta_corrente']
        data_de_nascimento = dic_usuario['data_de_nascimento']
        endereco = dic_usuario['endereco']
        cpf = dic_usuario['cpf']
        
    else:
        saldo = 0.0
        nome = None
        conta = 0

    if nome:
        print(f'CPF {cpf} - AGÊNCIA: 001 - Nome: {nome}')
        if dic_usuario:
            saldo = dic_usuario['saldo']
            nome = dic_usuario['nome']
            conta = dic_usuario.get('conta_corrente', 0)

            dados['nome'] = dic_usuario['nome']
            dados['data_de_nascimento'] = dic_usuario['data_de_nascimento'] 
            dados['endereco'] = dic_usuario['endereco']
        else:
            saldo = 0.0
            nome = None 
            conta = 0

        
        contas = ler_contas_usuario(cpf, ARQ)
        cabecalho('QUAL CONTA DESEJA ACESSAR?')
        
        for i, conta in enumerate(contas, start=1):
            print(f"{i} - Agência: 0001 - Conta Corrente: {conta['conta_corrente']}")
        escolha = 0
        while escolha < 1 or escolha > len(contas):
                try:
                    escolha = int(input('Digite o número refente a conta: '))
                except ValueError:
                    print('>>> OPÇÃO INVÁLIDA - Tente novamente <<<')

        dic_conta_corrente = contas[escolha - 1]
        
        dic_dados_conta = {
            'cpf': dic_conta_corrente['cpf'],
            'nome': dic_conta_corrente['nome'],
            'data_de_nascimento': dic_conta_corrente['data_de_nascimento'],
            'endereco': dic_conta_corrente['endereco'],
            'conta_corrente': dic_conta_corrente['conta_corrente'],
            'saldo': dic_conta_corrente['saldo']
        }

        extrato = ''
        numero_saques = 0
        conta_corrente = dic_conta_corrente['conta_corrente']


        cabecalho('Selecione a operação desejada no menu abaixo')
        util_menu(dic_conta_corrente['saldo'], extrato, numero_saques, limite, limite_saques, cpf, nome, conta_corrente, data_de_nascimento, endereco, ARQ)

    else:
        print('CPF NÃO ENCONTRADO')
        cadastro = ''
        while cadastro not in ['s', 'n']:
            cadastro = input('Deseja criar uma conta? [S/N]').strip().lower()
            if cadastro not in ['s', 'n']:
                print(f'>>> RESPOSTA INVÁLIDA - Digite S ou N <<<')
            if cadastro == 'n':
                break

        if cadastro == 'n':
            continue

        print(f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}')

        nome, data_de_nascimento, endereco = dados_cadastro()
        dados['nome'] = nome
        dados['data_de_nascimento'] = data_de_nascimento
        dados['endereco'] = endereco

        #criar nova conta corrente para cadastro inicial

        contas_existentes = []
        try:
            with open(ARQ, 'r') as arq:
                for linha in arq:
                    partes = linha.strip().split(';')
                    if len(partes) >= 5:
                        conta_corrente = int(partes[4])
                        contas_existentes.append(conta_corrente)
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        conta = nova_conta_corrente(*contas_existentes)
        cadastrar(ARQ, cpf, nome, data_de_nascimento, endereco, conta['conta_corrente'])

        print(f'>>> Conta criada com sucesso! <<< ')
        sleep(0.5)
        print(f'Sua nova conta corrente foi criada: 0001-{conta_corrente}')
        sleep(0.5)

        cabecalho('Selecione a operação desejada no menu abaixo')
        util_menu(saldo, extrato, numero_saques, limite, limite_saques, cpf, nome, conta_corrente, data_de_nascimento, endereco, ARQ)
