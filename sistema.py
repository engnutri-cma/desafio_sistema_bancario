from time import sleep
from datetime import datetime, date
import os
import logging
from typing import Iterator, Any
from functools import wraps
import json 

logging.basicConfig(
    filename='banco.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a',
    encoding='utf-8'
)

def linha(largura=42):
    return "-" * largura

def cabecalho(txt="MENU PRINCIPAL", largura=60):
    barra = linha(largura)
    print(barra)
    print(txt.center(len(barra)))  
    print(barra)

def log_transacao(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = datetime.now()
        conta_num = getattr(args[0], 'numero_conta', 'N/A') if args else 'N/A'
        try:
            resultado = func(*args, **kwargs)
            duracao = (datetime.now() - inicio).total_seconds()
            logging.info(f"Conta {conta_num} - {func.__name__.upper()} SUCESSO - Duração: {duracao:.3f}s")
            return resultado
        except Exception as e:
            logging.error(f"Conta {conta_num} - {func.__name__.upper()} FALHOU - Erro: {str(e)}")
            raise
    return wrapper

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
    return os.path.exists(nome_arquivo)

def criar_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'wt+', encoding='utf-8') as arquivo:
            pass
        print(f' >>> Arquivo {nome_arquivo} criado com sucesso! <<< ')
    except:
        print(f'Houve um ERRO ao criar o arquivo')

class TransacoesIterator:
    """Listagem personalizada para transações da conta COM HORÁRIOS"""
    def __init__(self, extrato: str):
        self.transacoes = []
        linhas = extrato.split('\n')
        for linha in linhas:
            linha = linha.strip()
            if linha and ('R$' in linha):
                # Correção: checa formato horário simples
                partes = linha.split(' - ', 1)
                if len(partes) < 2 or not (':' in partes[0] and len(partes[0]) == 8):
                    agora = datetime.now().strftime('%H:%M:%S')
                    linha = f"{agora} - {linha}"
                self.transacoes.append(linha)
        self.index = 0
    
    def __iter__(self) -> Iterator[str]:
        return self
    
    def __next__(self) -> str:
        if self.index >= len(self.transacoes):
            raise StopIteration
        transacao = self.transacoes[self.index]
        self.index += 1
        return transacao

class Conta:
    LIMITE_SAQUE = 500
    LIMITE_SAQUES_DIARIOS = 3
    
    def __init__(self, agencia, numero_conta, cpf, nome, data_de_nascimento, endereco, saldo=0.0, extrato="", saques_realizados=0, data_ultimo_saque=None):
        self.agencia = agencia
        self.numero_conta = numero_conta
        self.cpf = cpf
        self.nome = nome
        self.data_de_nascimento = data_de_nascimento
        self.endereco = endereco
        self.saldo = saldo
        self.extrato = extrato
        self.saques_realizados = saques_realizados
        self.data_ultimo_saque = data_ultimo_saque or date.today()
    
    def _reset_saques_diaros(self):
        hoje = date.today()
        if self.data_ultimo_saque != hoje:
            self.saques_realizados = 0
            self.data_ultimo_saque = hoje

    @log_transacao
    def sacar(self, valor):
        self._reset_saques_diaros()
        agora = datetime.now().strftime('%H:%M:%S')
        if valor > self.saldo:
            print(">>> Operação falhou! Saldo insuficiente. <<< ")
            return False
        elif valor > Conta.LIMITE_SAQUE:
            print(">>> Operação falhou! O valor do saque excede o limite. <<< ")
            return False
        elif self.saques_realizados >= Conta.LIMITE_SAQUES_DIARIOS:
            print(">>> Operação falhou! Número máximo de saques diários excedido. <<< ")
            return False
        elif valor > 0:
            self.saldo -= valor
            self.extrato += f'{agora} - Saque: R$ {valor:.2f}\n'
            self.saques_realizados += 1
            print(f'>>> Saque de R$ {valor:.2f} realizado com sucesso! <<< ')
            return True
        else:
            print(">>> Operação falhou! O valor informado é inválido. <<< ")
            return False

    @log_transacao
    def depositar(self, valor):
        agora = datetime.now().strftime('%H:%M:%S')
        if valor > 0:
            self.saldo += valor
            self.extrato += f'{agora} - Depósito: R$ {valor:.2f}\n'
            print(f'>>> Depósito de R$ {valor:.2f} realizado com sucesso! <<< ')
            return True
        else:
            print(">>> Operação falhou! O valor informado é inválido. <<< ")
            return False

    @log_transacao
    def mostrar_extrato(self):
        cabecalho('EXTRATO BANCÁRIO')
        if not self.extrato:
            print(">>> Não foram realizadas movimentações recentes. <<< ")
        else:
            print(self.extrato)
        print(f'Saldo: R$ {self.saldo:.2f}')
        print(linha())

    def __iter__(self):
        return TransacoesIterator(self.extrato)

    def relatorio_transacoes(self, limite=10):
        """Gera relatório das últimas transações"""
        transacoes = [t.strip() for t in self.extrato.split('\n') if t.strip()]
        for i, transacao in enumerate(reversed(transacoes[-limite:]), 1):
            yield f"{i}. {transacao}"
    
    def relatorio_resumo(self):
        """Relatório executivo da conta"""
        return {
            'agencia': self.agencia,
            'conta': self.numero_conta,
            'titular': self.nome,
            'saldo_atual': f'R$ {self.saldo:.2f}',
            'total_transacoes': len([t for t in self.extrato.split('\n') if t.strip()]),
            'saques_realizados': self.saques_realizados
        }

class Banco:
    def __init__(self, arquivo_cadastro: str, agencia_padrao: str = "0001"):
        self.arquivo = arquivo_cadastro
        self.agencia_padrao = agencia_padrao
        if not arquivo_existe(self.arquivo):
            criar_arquivo(self.arquivo)

    def ler_contas_usuario(self, cpf):
        list_contas = []
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as arq:
                for linha in arq:
                    if not linha.strip():
                        continue
                    partes = linha.strip().split(';')
                    if len(partes) >= 6:
                        nome, data_de_nascimento, cpf_lido, endereco, conta_corrente, saldo_str = partes[:6]
                        if cpf.strip() == cpf_lido.strip():
                            # Carrega estado completo (simplificado)
                            conta = Conta(
                                agencia=self.agencia_padrao,
                                numero_conta=int(conta_corrente),
                                cpf=cpf_lido,
                                nome=nome,
                                data_de_nascimento=data_de_nascimento,
                                endereco=endereco,
                                saldo=float(saldo_str)
                            )
                            list_contas.append(conta)
        except FileNotFoundError:
            print("Arquivo não encontrado!")
        return list_contas

    def ler_usuario_com_saldo(self, cpf):
        contas = self.ler_contas_usuario(cpf)
        if not contas:
            return None
        conta = contas[0]
        return {
            'nome': conta.nome,
            'data_de_nascimento': conta.data_de_nascimento,
            'cpf': conta.cpf,
            'endereco': conta.endereco,
            'conta_corrente': conta.numero_conta,
            'saldo': conta.saldo
        }
    
    def atualizar_saldo_no_arquivo(self, conta: Conta):
        atual_saldo = float(conta.saldo)
        linhas_novas = []
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as arq:
                for linha in arq:
                    linha_limpa = linha.strip()
                    if not linha_limpa:
                        continue
                    partes = linha_limpa.split(';')
                    if len(partes) >= 6:
                        if partes[2].strip() == conta.cpf.strip() and partes[4].strip() == str(conta.numero_conta).strip():
                            partes[-1] = f'{atual_saldo:.2f}'
                            linha_limpa = ';'.join(partes)
                    linhas_novas.append(linha_limpa)
            
            with open(self.arquivo, 'w', encoding='utf-8') as arq:
                arq.write('\n'.join(linhas_novas) + '\n')
        except Exception as e:
            print(f"Erro ao atualizar arquivo: {e}")
    
    @log_transacao
    def criar_nova_conta(self, cpf, nome, data_de_nascimento, endereco):
        contas_existentes = self.ler_contas_usuario(cpf)
        if contas_existentes:
            numeros_contas = [conta.numero_conta for conta in contas_existentes]
            novo_numero_conta = max(numeros_contas) + 1
        else:
            novo_numero_conta = 1

        nova_conta = Conta(
            agencia=self.agencia_padrao,
            numero_conta=novo_numero_conta,
            cpf=cpf,
            nome=nome,
            data_de_nascimento=data_de_nascimento,
            endereco=endereco,
            saldo=0.0
        )

        with open(self.arquivo, 'a', encoding='utf-8') as a:
            a.write(f'{nome};{data_de_nascimento};{cpf};{endereco};{novo_numero_conta};0.00\n')

        return nova_conta

def opcao_escolher_conta(banco: Banco, cpf: str):
    contas = banco.ler_contas_usuario(cpf)
    if not contas:
        return None
    
    cabecalho('QUAL CONTA DESEJA ACESSAR?')
    
    for i, conta in enumerate(contas, start=1):
        print(f"{i} - Agência: {conta.agencia} - Conta Corrente: {conta.numero_conta} - Nome: {conta.nome} ")
    
    escolha = 0
    while escolha < 1 or escolha > len(contas):
        try:
            escolha = int(input('Digite o número referente à conta: '))
            if 1 <= escolha <= len(contas):
                return contas[escolha - 1]
        except ValueError:
            print('>>> OPÇÃO INVÁLIDA - Tente novamente <<<')
    return None

def util_menu(banco: Banco, conta: Conta):
    while True:
        print(f'Agência: {conta.agencia} - Conta Corrente: {conta.numero_conta} - Nome: {conta.nome}')
        opcao = menu('LISTAR CONTAS','SALDO', 'SAQUE', 'DEPOSITAR', 'EXTRATO', 
                    'RELATÓRIOS', 'LISTAR TRANSACOES', 'NOVA CONTA', 'SAIR DO SISTEMA', 
                    conta_corrente=conta.numero_conta)

        if opcao == 1:
            nova_conta = opcao_escolher_conta(banco, conta.cpf)
            if nova_conta: conta = nova_conta
        elif opcao == 2:
            print(f'Seu saldo é: R$ {conta.saldo:.2f}')
        elif opcao == 3:
            try:
                valor = float(input('Digite o valor do saque: R$ '))
                if conta.sacar(valor):
                    print(f'Seu novo saldo é: R$ {conta.saldo:.2f}')
            except ValueError:
                print('>>> Valor inválido <<<')
        elif opcao == 4:
            try:
                valor = float(input('Digite o valor do depósito: R$ '))
                if conta.depositar(valor):
                    print(f'Seu novo saldo é: R$ {conta.saldo:.2f}')
            except ValueError:
                print('>>> Valor inválido <<<')
        elif opcao == 5:
            conta.mostrar_extrato()
        elif opcao == 6:  
            print("\n=== RELATÓRIOS ===")
            print("1 - Resumo Executivo")
            print("2 - Últimas 5 Transações")
            rel = int(input("Escolha relatório: "))
            if rel == 1:
                resumo = conta.relatorio_resumo()
                for k, v in resumo.items():
                    print(f"{k}: {v}")
            elif rel == 2:
                print("Últimas transações:")
                for trans in conta.relatorio_transacoes(5):
                    print(trans)
        elif opcao == 7:  
            print("\n TRANSÇÕES COM HORÁRIOS:")
            print("Formato: HH:MM:SS - Tipo: R$ valor")
            print("-" * 50)
            transacoes_exibidas = 0
            try:
                for i, transacao in enumerate(conta, 1):
                    print(f"{i:2d}. {transacao}")
                    transacoes_exibidas += 1
                    if transacoes_exibidas >= 10:  
                        total = len([t for t in conta.extrato.splitlines() if t.strip()])
                        print(f"... e mais {total - 10} transações")
                        break
                else:
                    print("Todas as transações exibidas.")
            except StopIteration:
                pass
        elif opcao == 8:
            nova_conta = banco.criar_nova_conta(conta.cpf, conta.nome, conta.data_de_nascimento, conta.endereco)
            print(f'>>> Nova conta criada: {nova_conta.agencia}-{nova_conta.numero_conta} <<< ')
            conta = nova_conta
        elif opcao == 9:
            banco.atualizar_saldo_no_arquivo(conta)
            print('Saindo do sistema...')
            break
        else:
            print('>>> OPÇÃO INVÁLIDA <<<')
        sleep(0.5)

def dados_cadastro(cpf):
    nome = input('Digite seu nome completo: ').strip().title()
    print('Data de nascimento')
    dia = input('Dia (dd): ').strip()
    mes = input('Mês (mm): ').strip()
    ano = input('Ano (aaaa): ').strip()
    data_de_nascimento = f'{dia}/{mes}/{ano}'
    print('Endereço')
    rua = input('Logradouro: ').strip().title()
    nro = input('Número: ').strip()
    comp = input('Complemento: ').strip()
    bairro = input('Bairro: ').strip().title()
    cidade = input('Cidade: ').strip().title()
    estado = input('Estado (UF): ').strip().upper()
    endereco = f'{rua}, {nro}/{comp} - {bairro} - {cidade}/{estado}'
    return nome, data_de_nascimento, endereco

# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    ARQ = 'cadastro.txt'
    banco = Banco(ARQ)
    
    while True:
        cpf = input('Digite o CPF (apenas números): ').strip()
        while not (cpf.isdigit() and len(cpf) == 11):
            print('>>> CPF INVÁLIDO <<<')
            cpf = input('Digite o CPF (apenas números): ').strip()

        info_usuario = banco.ler_usuario_com_saldo(cpf)
        if info_usuario:
            print(f'Usuário encontrado: {info_usuario["nome"]}')
            conta_escolhida = opcao_escolher_conta(banco, cpf)
            if conta_escolhida:
                cabecalho('MENU OPERACIONAL')
                util_menu(banco, conta_escolhida)
        else:
            print('>>> USUÁRIO NÃO ENCONTRADO <<<')
            while True:
                cadastro = input('Cadastrar novo? [S/N]: ').strip().upper()
                if cadastro == 'S': break
                elif cadastro == 'N': exit()
                else: print('>>> S/N <<<')
            
            nome, data, endereco = dados_cadastro(cpf)
            nova_conta = banco.criar_nova_conta(cpf, nome, data, endereco)
            print(f'>>> {nome} cadastrado! Conta: {nova_conta.numero_conta} <<<')
            cabecalho('MENU OPERACIONAL')
            util_menu(banco, nova_conta)
