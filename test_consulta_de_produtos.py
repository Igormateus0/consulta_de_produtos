"""Testes isolados: executar com py -m unittest -v test_consulta_de_produtos."""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name('consulta_de_produtos.py')
tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
# O programa executa main() ao importar; carregar apenas suas definições.
tree.body = [n for n in tree.body if not isinstance(n, ast.Expr)]
app = {}
exec(compile(tree, str(SOURCE), 'exec'), app)


class TestEstoque(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = os.getcwd()
        os.chdir(self.temp.name)
        self.produtos = {'001': {'nome': 'Café', 'preco': 12.5,
                                'quantidade': 5, 'total_entrada': 8, 'total_saida': 3}}

    def tearDown(self):
        os.chdir(self.previous)
        self.temp.cleanup()

    def call(self, name, answers=(), produtos=None, **kwargs):
        output = io.StringIO()
        with patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(output):
            result = app[name](self.produtos if produtos is None else produtos, **kwargs)
        return result, output.getvalue()

    def number(self, answers, **kwargs):
        with patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(io.StringIO()):
            return app['ler_numero']('Valor: ', **kwargs)

    def test_arquivo_ausente(self):
        self.assertEqual(app['carregar_produtos'](), {})

    def test_persistencia_unicode(self):
        app['salvar_produtos'](self.produtos)
        self.assertEqual(app['carregar_produtos'](), self.produtos)
        self.assertIn('Café', Path('estoque.json').read_text(encoding='utf-8'))

    def test_json_corrompido(self):
        Path('estoque.json').write_text('{quebrado', encoding='utf-8')
        self.assertEqual(app['carregar_produtos'](), {})

    def test_numero_invalido_negativo_zero(self):
        self.assertEqual(self.number(['abc', '-1', '0', '2']), 2)

    def test_quantidade_zero(self):
        self.assertEqual(self.number(['-2', '0'], permitir_zero=True), 0)

    def test_inteiro_rejeita_fracao(self):
        self.assertEqual(self.number(['1.5', '3']), 3)

    def test_preco_decimal(self):
        self.assertEqual(self.number(['12.50'], tipo=float), 12.5)

    def test_cadastro(self):
        self.call('adicinar_produtos', ['002', '  mouse usb  ', '25.90', '0'])
        self.assertEqual(self.produtos['002'], {'nome': 'Mouse Usb', 'preco': 25.9,
                          'quantidade': 0, 'total_entrada': 0, 'total_saida': 0})
        self.assertEqual(app['carregar_produtos'](), self.produtos)

    def test_codigo_duplicado(self):
        before = copy.deepcopy(self.produtos)
        self.call('adicinar_produtos', ['001'])
        self.assertEqual(self.produtos, before)

    def test_consulta_case_espacos(self):
        _, output = self.call('consulta_produtos', ['  CAFÉ  '])
        self.assertIn('Produto encontrado!', output)
        self.assertIn('12.50', output)

    def test_consulta_inexistente(self):
        self.assertIn('não encontrado', self.call('consulta_produtos', ['xyz'])[1])

    def test_listar(self):
        self.assertIn('Café', self.call('listar_produtos')[1])

    def test_listar_vazio(self):
        self.assertIn('Nenhum produto', self.call('listar_produtos', produtos={})[1])

    def test_remover(self):
        self.call('remover_produtos', ['001'])
        self.assertEqual(app['carregar_produtos'](), {})

    def test_remover_inexistente(self):
        before = copy.deepcopy(self.produtos)
        self.call('remover_produtos', ['xyz'])
        self.assertEqual(self.produtos, before)

    def test_entrada(self):
        self.call('resgistro_de_entrada_saida', ['001', '1', '3'])
        self.assertEqual(self.produtos['001']['quantidade'], 8)
        self.assertEqual(self.produtos['001']['total_entrada'], 11)
        self.assertEqual(app['carregar_produtos'](), self.produtos)

    def test_saida_total(self):
        self.call('resgistro_de_entrada_saida', ['001', '2', '5'])
        self.assertEqual(self.produtos['001']['quantidade'], 0)
        self.assertEqual(self.produtos['001']['total_saida'], 8)

    def test_saida_insuficiente(self):
        before = copy.deepcopy(self.produtos)
        self.assertIn('insuficiente', self.call('resgistro_de_entrada_saida', ['001', '2', '6'])[1])
        self.assertEqual(self.produtos, before)

    def test_movimento_cancelado_invalido_ausente(self):
        for answers in [['001', '3'], ['001', '9'], ['xyz']]:
            with self.subTest(answers=answers):
                before = copy.deepcopy(self.produtos)
                self.call('resgistro_de_entrada_saida', answers)
                self.assertEqual(self.produtos, before)

    def test_resumo(self):
        self.assertIn('Total de Entrada:', self.call('receita_de_entrada_saida_de_estoque')[1])

    def test_resumo_vazio(self):
        self.assertIn('Nenhum produto', self.call('receita_de_entrada_saida_de_estoque', produtos={})[1])

    def test_fluxo_terminal_completo(self):
        answers = ['9', '1', '010', 'Arroz', '10.50', '4', '3', 'ARROZ',
                   '5', '010', '1', '3', '5', '010', '2', '2', '4', '6',
                   '2', '010', '7']
        result = subprocess.run([sys.executable, str(SOURCE)], input='\n'.join(answers)+'\n',
                                capture_output=True, text=True, encoding='utf-8',
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Produto encontrado!', result.stdout)
        self.assertIn('Saindo do programa', result.stdout)
        self.assertEqual(app['carregar_produtos'](), {})

    def test_estresse_1000_movimentacoes(self):
        for _ in range(500):
            self.call('resgistro_de_entrada_saida', ['001', '1', '2'])
            self.call('resgistro_de_entrada_saida', ['001', '2', '2'])
        p = app['carregar_produtos']()['001']
        self.assertEqual(p['quantidade'], 5)
        self.assertEqual(p['total_entrada'] - p['total_saida'], p['quantidade'])

    def test_preco_nan_deve_ser_rejeitado(self):
        self.assertEqual(self.number(['nan', '10'], tipo=float), 10)

    def test_preco_infinito_deve_ser_rejeitado(self):
        self.assertEqual(self.number(['inf', '10'], tipo=float), 10)

    def test_codigo_vazio_deve_ser_rejeitado(self):
        self.call('adicinar_produtos', ['', 'Produto', '10', '1'])
        self.assertNotIn('', self.produtos)

    def test_nome_vazio_deve_ser_rejeitado(self):
        self.call('adicinar_produtos', ['002', '   ', '10', '1'])
        self.assertFalse(any(p['nome'] == '' for p in self.produtos.values()))

    def test_codigo_com_espacos_deve_identificar_duplicata(self):
        self.call('adicinar_produtos', [' 001 ', 'Outro', '10', '1'])
        self.assertEqual(len(self.produtos), 1)

    def test_json_lista_deve_ser_rejeitado(self):
        Path('estoque.json').write_text('[]', encoding='utf-8')
        self.assertIsInstance(app['carregar_produtos'](), dict)

    def test_json_null_deve_ser_rejeitado(self):
        Path('estoque.json').write_text('null', encoding='utf-8')
        self.assertIsInstance(app['carregar_produtos'](), dict)


if __name__ == '__main__':
    unittest.main()
