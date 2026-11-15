# Resultado dos testes

Após as correções autorizadas, executados 30 testes automatizados: **30 passaram, sem falhas**.
Na execução inicial, 23 passaram e 7 falharam. Os testes gravam somente em diretórios temporários; o estoque real permaneceu inalterado, confirmado pelo SHA256.

Foram corrigidos: preços NaN e infinitos, código e nome vazios, espaços nas extremidades dos códigos (cadastro, remoção e movimentação) e tipo da estrutura principal do JSON. Lista e null agora geram aviso e retornam um dicionário vazio. A validação dos campos internos de cada produto e os demais riscos descritos abaixo continuam fora desta correção.

## O que passou

- Cadastro e persistência em JSON com acentos e códigos com zeros iniciais.
- Bloqueio de código duplicado idêntico.
- Consulta com diferenças de maiúsculas/minúsculas e espaços no nome buscado.
- Listagem, remoção e resumo, incluindo estoque vazio e produto inexistente.
- Entrada, saída total, estoque insuficiente, cancelamento e opção inválida.
- Rejeição de números negativos, zero quando proibido e frações em quantidades inteiras.
- Fluxo completo em um processo real do terminal: menu inválido, cadastro, consulta, entrada, saída, listagem, resumo, remoção e encerramento.
- Estresse de 1.000 movimentações com gravação: saldo final correto e igualdade entre entradas menos saídas e quantidade.

## Falhas reproduzidas na execução inicial e corrigidas

1. **Preço `nan` aceito:** valor sem significado numérico pode ser salvo no estoque.
2. **Preço `inf` aceito:** preço infinito pode ser salvo no estoque.
3. **Código vazio aceito:** é possível cadastrar um produto sem código.
4. **Nome vazio aceito:** espaços viram um nome vazio após strip().
5. **Código com espaços cria duplicata lógica:** `001` e ` 001 ` são tratados como produtos distintos.
6. **JSON com lista aceito:** carregar `[]` retorna lista, embora as funções esperem dicionário.
7. **JSON null aceito:** carregar `null` retorna None, embora as funções esperem dicionário.

## Outros riscos observados na leitura do código

Estes pontos são análise estática, separados das sete falhas automatizadas:

- JSON corrompido é silenciosamente convertido em estoque vazio; um cadastro posterior pode sobrescrever o arquivo anterior.
- O caminho de estoque.json depende da pasta atual do terminal, podendo carregar ou criar outro estoque ao iniciar o programa de uma pasta diferente.
- Não há validação dos campos e tipos de cada produto carregado do JSON.
- A gravação substitui diretamente o arquivo; não há proteção contra interrupção da escrita nem acesso simultâneo.
- Importar o módulo executa main() imediatamente. A suíte carrega as definições via AST para testar sem alterar o programa.

## Como repetir

Com Python instalado e disponível, nesta pasta:

```powershell
py -m unittest -v test_consulta_de_produtos
```

Nesta sessão não havia Python registrado no launcher `py`; foi usado o interpretador fornecido pelo ambiente Codex:

```powershell
& 'C:\Users\igorm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest -v test_consulta_de_produtos
```

A suíte agora retorna código 0. Os sete testes anteriormente reprovados passaram sem enfraquecer suas verificações, assim como o fluxo completo no terminal e o estresse de 1.000 movimentações.
