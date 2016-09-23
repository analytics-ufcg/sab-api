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



if __name__ == '__main__':
    unittest.main()
