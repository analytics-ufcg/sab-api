#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.insert(0,'..')
import funcoes_aux
import IO

class TestStringMethods(unittest.TestCase):

    def test_remove_accent(self):
        self.assertEqual(funcoes_aux.remover_acentos("insa"), 'insa')
        self.assertEqual(funcoes_aux.remover_acentos("ínsa"), 'insa')

    def test_fix_accent(self):
        self.assertEqual(funcoes_aux.ajuste_acentos("ínsa"), unicode('ínsa', "unicode-escape"))
        self.assertEqual(funcoes_aux.ajuste_acentos("insa"), unicode('insa', "unicode-escape"))

    def test_create_dict(self):
        values = ["insa","instituto nacional do semiario", "salomao"]
        keys = ["sigla", "nome", "diretor"]
        dictionary = {"sigla":"insa", "nome":"instituto nacional do semiario", "diretor":"salomao"}
        self.assertEqual(funcoes_aux.cria_dicionario(values,keys), dictionary)

    def test_create_list_dict(self):
        values = ["insa","instituto nacional do semiario", "salomao"]
        values2 = ["insa2","instituto nacional do semiario2", "salomao2"]
        values3 = ["insa3","instituto nacional do semiario3", "salomao3"]
        list_values = [values,values2,values3]
        keys = ["sigla", "nome", "diretor"]
        dictionary = {"sigla":"insa", "nome":"instituto nacional do semiario", "diretor":"salomao"}
        dictionary2 = {"sigla":"insa2", "nome":"instituto nacional do semiario2", "diretor":"salomao2"}
        dictionary3 = {"sigla":"insa3", "nome":"instituto nacional do semiario3", "diretor":"salomao3"}
        list_dictionarys = [dictionary,dictionary2,dictionary3]
        self.assertEqual(funcoes_aux.lista_dicionarios(list_values,keys), list_dictionarys)

    def test_shapes(self):
        self.assertTrue(len(IO.estados_sab()) > 0)
        self.assertTrue(len(IO.reservatorios()) > 0)

    def test_ajuste_dados_intervalo(self):
        boa = [(100,"20/06/2016",10),(100,"21/06/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        boa_resp = [(100,"20/06/2016",10),(100,"21/06/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        self.assertEqual(funcoes_aux.ajuste_dados_com_intervalo(boa), boa_resp)

        ruim = [(100,"20/06/2016",10),(100,"21/09/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        ruim_resp = [(100,"20/06/2016",10),(None,"20/06/2016",None),(None,"21/09/2016",None),(100,"21/09/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        self.assertEqual(funcoes_aux.ajuste_dados_com_intervalo(ruim), ruim_resp)


    def test_ajuste_dados_intervalo(self):
        reservatorios =[{"reservat": "Barragem Jabiberi", "volume": None, "volume_percentual": None, "data": None, "id": 751}, {"reservat": "UHE Pedra do Cavalo", "volume": None, "volume_percentual": None, "data": None, "id": 795}, {"reservat": "Açude Barra da Melancia", "volume": None, "volume_percentual": None, "data": None, "id": 1041}, {"reservat": "Açude Mesa de Pedra", "volume": None, "volume_percentual": None, "data": None, "id": 1055}, {"reservat": "Açude Machado", "volume": None, "volume_percentual": None, "data": None, "id": 1066}]

        resp1 =[{"reservat": "Barragem Jabiberi", "volume": None, "volume_percentual": None, "data": None, "id": 751, 'semelhanca': 100}]
        self.assertEqual(funcoes_aux.reservatorios_similares("jabiberi", reservatorios), resp1)

        resp2 = [{"reservat": "Açude Barra da Melancia", "volume": None, "volume_percentual": None, "data": None, "id": 1041, 'semelhanca': 100}, {"reservat": "Açude Mesa de Pedra", "volume": None, "volume_percentual": None, "data": None, "id": 1055, 'semelhanca': 100}, {"reservat": "Açude Machado", "volume": None, "volume_percentual": None, "data": None, "id": 1066, 'semelhanca': 100}]
        self.assertEqual(funcoes_aux.reservatorios_similares("acude", reservatorios), resp2)

if __name__ == '__main__':
    unittest.main()
