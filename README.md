
# Sistema Bancário em Python - Projeto Bootcamp Backend em Python by LuizaLabs

Este é um projeto desenvolvido como desafio prático em um bootcamp de backend com Python By LuizaLabs-DIO., focado em iniciantes. O objetivo é implementar um sistema bancário simples que permita realizar operações básicas como saque, depósito, visualização de extrato, cadastro de usuário e criação de conta corrente, armazenando dados em arquivos.

**Funcionalidades**

* Cadastro de usuários com informações: nome, CPF, data de nascimento e endereço.
* Criação de contas correntes vinculadas a usuários pelo CPF.
* Operações bancárias:
    * Saque (com limite por operação e máximo diário de saques).
    * Depósito.
    * Visualização do extrato com histórico das movimentações.

* Armazenamento persistente dos dados dos usuários, contas e saldo em arquivo texto.
* Gerenciamento de múltiplas contas por usuário.
* Interação via menu de terminal (interface CLI simples).

**Especificidades Utilizadas**

* Manipulação de arquivos para armazenamento em formato CSV simplificado (delimitado por ;)

* Passagem de argumentos com tipos diferentes (keyword-only, positional-only) para melhorar o aprendizado dos conceitos Python.


**Descrição das Funções Principais**

* sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques): realiza saque, exige keyword-only arguments para reforçar conceitos.
* depositar(saldo, valor, extrato, /): realiza depósito, com argumentos position-only.
* cadastrar(ARQ, cpf, nome, data_nascimento, endereco, conta_corrente, saldo): cadastra usuário e conta no arquivo.
* nova_conta_corrente(*contas_existentes): gera novo número sequencial para conta.
* ler_contas_usuario(cpf, ARQ): obtém lista de contas associadas a um CPF.
* atualizar_saldo_no_arquivo(cpf, saldo, conta_corrente, ARQ): atualiza saldo no arquivo.
* Estrutura de menu e navegação para operação e seleção de conta.


**Aprendizados e Conceitos Abordados**

* Fundamentos de Python focados no backend, como manipulação de arquivos.
* Controle de fluxo e estruturação de programas CLI.
* Uso de funções com diferentes tipos de passagem de parâmetros.
* Regra de negócio para operações bancárias (limites, saques diários).
* Persistência simples de dados usando arquivos.
* Tratamento básico de erros e validação de entradas.
