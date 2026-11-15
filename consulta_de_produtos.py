import json
import math


def carregar_produtos():
    try:
        with open("estoque.json", "r", encoding="utf-8") as arquivo:
            produtos = json.load(arquivo)
        if not isinstance(produtos, dict):
            print("Formato de estoque inválido: esperado um objeto JSON.")
            return {}
        return produtos
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_produtos(produtos):
    with open("estoque.json", "w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def ler_numero(mensagem, tipo=int, permitir_zero=False):
    while True:
        try:
            valor = tipo(input(mensagem))
            if isinstance(valor, float) and not math.isfinite(valor):
                print("Digite um número finito válido.")
                continue
            if permitir_zero and valor < 0:
                print("O valor não pode ser negativo.")
                continue
            if not permitir_zero and valor <= 0:
                print("Digite um valor maior que zero.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Digite apenas números.")


def consulta_produtos(produtos):
    nome_produto = input("Digite o nome do produto que deseja consultar: ").strip() .lower()
    nome_buscado = nome_produto.casefold()
    produto = next(
        (p for p in produtos.values() if p["nome"].casefold() == nome_buscado),
        None,
    )
    if produto is not None:
        print("|-------------------------------------|")
        print("|        Produto encontrado!          |")
        print("|-------------------------------------|")
        print(f"Produto: {produto['nome']}")
        print(f"Preço: R${produto['preco']:.2f}")
        print(f"Quantidade em estoque: {produto['quantidade']}")
    else:
        print("Produto não encontrado.")


def adicinar_produtos(produtos):
    codigo_produto = input("Digite o código do produto que deseja adicionar: ").strip()
    if not codigo_produto:
        print("O código do produto não pode ficar vazio.")
        return
    if codigo_produto in produtos:
        print("Produto já existe no estoque.")
        return

    nome_produto = input("Digite o nome do produto: ") .strip() .title()
    if not nome_produto:
        print("O nome do produto não pode ficar vazio.")
        return
    preco_produto = ler_numero("Digite o preço do produto: ", tipo=float)
    quantidade_produto = ler_numero(
        "Digite a quantidade em estoque: ", tipo=int, permitir_zero=True
    )

    produtos[codigo_produto] = {
        "nome": nome_produto,
        "preco": preco_produto,
        "quantidade": quantidade_produto,
        "total_entrada": quantidade_produto,
        "total_saida": 0,
    }

    salvar_produtos(produtos)
    print("Produto adicionado com sucesso!")


def remover_produtos(produtos):
    codigo_produto = input("Digite o código do produto que deseja remover: ").strip()
    if codigo_produto in produtos:
        del produtos[codigo_produto]
        salvar_produtos(produtos)
        print("Produto removido com sucesso!")
    else:
        print("Produto não encontrado no estoque.")


def listar_produtos(produtos):
    if produtos:
        print("|-------------------------------------|")
        print("|          Lista de Produtos          |")
        print("|-------------------------------------|")
        for codigo, produto in produtos.items():
            print(f"Código: {codigo}")
            print(f"Produto: {produto['nome']}")
            print(f"Preço: R${produto['preco']:.2f}")
            print(f"Quantidade em estoque: {produto['quantidade']}")
            print("|-------------------------------------|")
    else:
        print("Nenhum produto cadastrado no estoque.")


def resgistro_de_entrada_saida(produtos):
    codigo_produto = input("Digite o código do produto para registrar a movimentação: ").strip()
    if codigo_produto in produtos:
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Voltar ao menu principal")
        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            quantidade_entrada = ler_numero(
                "Digite a quantidade de entrada: ", tipo=int
            )
            produtos[codigo_produto]["quantidade"] += quantidade_entrada
            produtos[codigo_produto]["total_entrada"] += quantidade_entrada
            salvar_produtos(produtos)
            print("Entrada de produtos registrada com sucesso!")

        elif opcao == "2":
            quantidade_saida = ler_numero(
                "Digite a quantidade de saída: ", tipo=int
            )
            if quantidade_saida <= produtos[codigo_produto]["quantidade"]:
                produtos[codigo_produto]["quantidade"] -= quantidade_saida
                produtos[codigo_produto]["total_saida"] += quantidade_saida
                salvar_produtos(produtos)
                print("Saída de produtos registrada com sucesso!")
            else:
                print("Quantidade insuficiente em estoque para realizar a saída.")

        elif opcao == "3":
            return
        else:
            print("Opção inválida.")
    else:
        print("Produto não encontrado no estoque.")


def receita_de_entrada_saida_de_estoque(produtos):
    print("|-------------------------------------|")
    print("|      Resumo do Estoque Atual        |")
    print("|-------------------------------------|")

    if not produtos:
        print("Nenhum produto cadastrado no estoque.")
    else:
        for codigo, produto in produtos.items():
            print("-" * 25)
            print(f"{'Código:':<25}{codigo}")
            print(f"{'Quantidade em estoque:':<25}{produto['quantidade']}")
            print(f"{'Total de Entrada:':<25}{produto['total_entrada']}")
            print(f"{'Total de Saída:':<25}{produto['total_saida']}")
            print("-" * 25)


def main():
    produtos = carregar_produtos()

    while True:
        largura = 40
        print("-" * largura)
        print(f"{'Menu de opções':^40}")
        print("-" * largura)
        print("1. Adicionar produtos")
        print("2. Remover produtos")
        print("3. Consultar produtos")
        print("4. Listar produtos")
        print("5. Registrar entrada/saída")
        print("6. Resumo de entrada/saída")
        print("7. Sair")
        print("-" * largura)

        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            adicinar_produtos(produtos)
        elif opcao == "2":
            remover_produtos(produtos)
        elif opcao == "3":
            consulta_produtos(produtos)
        elif opcao == "4":
            listar_produtos(produtos)
        elif opcao == "5":
            resgistro_de_entrada_saida(produtos)
        elif opcao == "6":
            receita_de_entrada_saida_de_estoque(produtos)
        elif opcao == "7":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Digite novamente.")


main()
