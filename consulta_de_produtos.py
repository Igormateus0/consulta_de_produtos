import json


def carregar_produtos():
    try:
        with open("estoque.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {}


def salvar_produtos(produtos):
    with open("estoque.json", "w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)


def consulta_produtos(produtos):
    nome_produto = input("Digite o nome do produto que deseja consultar: ")
    if nome_produto in [p["nome"] for p in produtos.values()]:
        print("|-------------------------------------|")
        print("|        Produto encontrado!          |")
        print("|-------------------------------------|")
        produto = next(p for p in produtos.values() if p["nome"] == nome_produto)
        print(f"Produto: {produto['nome']}")
        print(f"Preço: R${produto['preco']:.2f}")
        print(f"Quantidade em estoque: {produto['quantidade']}")
    else:
        print("Produto não encontrado.")


def adicinar_produtos(produtos):
    codigo_produto = input("Digite o código do produto que deseja adicionar: ")
    if codigo_produto in produtos:
        print("Produto já existe no estoque.")
    else:
        nome_produto = input("Digite o nome do produto: ")
        preco_produto = float(input("Digite o preço do produto: "))
        quantidade_produto = int(input("Digite a quantidade em estoque: "))

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
    codigo_produto = input("Digite o código do produto que deseja remover: ")
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
    codigo_produto = input("Digite o código do produto para registrar a movimentação: ")
    if codigo_produto in produtos:
        print("1. Registrar Entrada")
        print("2. Registrar Saída")
        print("3. Voltar ao menu principal")
        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            while True:
                try:
                    quantidade_entrada = int(input("Digite a quantidade de entrada: "))
                    if quantidade_entrada <= 0:
                        print("Quantidade inválida. Digite um valor positivo.")
                        continue
                    break
                except ValueError:
                    print("Entrada inválida. Digite um número inteiro.")

            produtos[codigo_produto]["quantidade"] += quantidade_entrada
            produtos[codigo_produto]["total_entrada"] += quantidade_entrada
            salvar_produtos(produtos)
            print("Entrada de produtos registrada com sucesso!")

        elif opcao == "2":
            while True:
                try:
                    quantidade_saida = int(input("Digite a quantidade de saída: "))
                    if quantidade_saida <= 0:
                        print("Quantidade inválida. Digite um valor positivo.")
                        continue
                    break
                except ValueError:
                    print("Saída inválida. Digite um número inteiro.")

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