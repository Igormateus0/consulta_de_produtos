# Consulta de Produtos

Sistema de estoque em Python, executado pelo terminal, para cadastrar produtos, consultar preços e controlar entradas e saídas. Os dados são salvos em `estoque.json`.

## Funcionalidades

- Cadastro de produtos com código, nome, preço e quantidade.
- Consulta pelo nome, sem diferenciar maiúsculas e minúsculas.
- Listagem e remoção de produtos.
- Registro de entradas e saídas, com bloqueio de saída superior ao saldo.
- Resumo da quantidade atual e dos totais de entrada e saída por produto.
- Persistência em JSON com suporte a acentos.

## Atualização de validações

Esta atualização corrige sete falhas encontradas nos testes:

1. Rejeita `NaN` como preço.
2. Rejeita preços infinitos, como `inf`.
3. Impede o cadastro com código vazio.
4. Impede o cadastro com nome vazio ou composto apenas por espaços.
5. Remove espaços nas extremidades dos códigos, evitando que `001` e ` 001 ` criem cadastros distintos. A normalização também se aplica à remoção e à movimentação.
6. Detecta estoque JSON contendo uma lista, em vez de um objeto.
7. Detecta estoque JSON contendo `null`.

Quando o cadastro recebe código ou nome vazio, exibe uma mensagem e retorna ao menu. Quando o preço é inválido, solicita outro valor. Um JSON cujo tipo principal não é um objeto gera um aviso e retorna um estoque vazio em memória.

## Como executar

Requer Python 3. Não há dependências externas.

Abra o terminal na pasta do projeto e execute:

```powershell
py consulta_de_produtos.py
```

Se o seu ambiente usa o comando `python`:

```sh
python consulta_de_produtos.py
```

Digite a opção desejada no menu. Para preços decimais, use ponto, por exemplo `25.90`. Quantidades devem ser inteiras. O cadastro permite quantidade inicial zero; entradas e saídas devem ser maiores que zero.

## Testes e resultados

Execute na pasta do projeto:

```powershell
py -m unittest -v test_consulta_de_produtos
```

A última execução local teve **30 testes aprovados e nenhuma falha**. Na primeira execução, antes das correções, foram 23 aprovações e 7 falhas.

A suíte cobre cadastro, consulta, remoção, listagem, movimentações, persistência, entradas inválidas e o fluxo completo em um processo real do terminal. Inclui um teste de estresse com **1.000 movimentações**, verificando o saldo e os totais.

Os testes usam pastas temporárias. O estoque real foi preservado e seu hash SHA256 foi conferido antes e depois da execução. Detalhes em [RELATORIO_TESTES.md](RELATORIO_TESTES.md).

## Arquivos

| Arquivo | Finalidade |
| --- | --- |
| `consulta_de_produtos.py` | Programa e menu do estoque |
| `estoque.json` | Dados persistidos |
| `test_consulta_de_produtos.py` | Testes automatizados com unittest |
| `RELATORIO_TESTES.md` | Resultados e limitações identificadas |

## Limitações atuais

- Execute a partir da pasta do projeto: o caminho de `estoque.json` é relativo à pasta atual do terminal.
- A validação do JSON verifica seu tipo principal; os campos internos de cada produto ainda não são validados.
- Um JSON corrompido é tratado como estoque vazio. Um cadastro posterior pode sobrescrever o arquivo; mantenha uma cópia de segurança antes de editar o JSON manualmente.
- A gravação ainda não é atômica e não há controle de acesso simultâneo. Use uma instância do programa por vez.
