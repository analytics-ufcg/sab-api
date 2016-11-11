#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.insert(0,'..')
import funcoes_aux
import IO

class TestStringMethods(unittest.TestCase):

    def test_remove_accent(self):
        self.assertEqual(funcoes_aux.remove_accents("insa"), 'insa')
        self.assertEqual(funcoes_aux.remove_accents("ínsa"), 'insa')

    def test_fix_accent(self):
        self.assertEqual(funcoes_aux.fix_accents("ínsa"), unicode('ínsa', "unicode-escape"))
        self.assertEqual(funcoes_aux.fix_accents("insa"), unicode('insa', "unicode-escape"))

    def test_create_dict(self):
        values = ["insa","instituto nacional do semiario", "salomao"]
        keys = ["sigla", "nome", "diretor"]
        dictionary = {"sigla":"insa", "nome":"instituto nacional do semiario", "diretor":"salomao"}
        self.assertEqual(funcoes_aux.create_dictionary(values,keys), dictionary)

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
        self.assertEqual(funcoes_aux.list_of_dictionarys(list_values,keys), list_dictionarys)

    def test_shapes(self):
        self.assertTrue(len(IO.states_sab()) > 0)
        self.assertTrue(len(IO.brazil()) > 0)

    def test_fix_data_interval_limit(self):
        answer = [(100,"20/06/2016",10),(100,"21/06/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        answer_good = [(100,"20/06/2016",10),(100,"21/06/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        self.assertEqual(funcoes_aux.fix_data_interval_limit(answer), answer_good)

        bad = [(100,"20/06/2016",10),(100,"21/09/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        answer_bad = [(100,"20/06/2016",10),(None,"20/06/2016",None),(None,"21/09/2016",None),(100,"21/09/2016",10),(100,"22/06/2016",10),(100,"23/06/2016",10),(100,"24/06/2016",10)]
        self.assertEqual(funcoes_aux.fix_data_interval_limit(bad), answer_bad)


    def test_reservoirs_similar(self):
        reservoirs =[{"nome": "Barragem Jabiberi","reservat": "Barragem Jabiberi", "volume": None, "volume_percentual": None, "data": None, "id": 751, "estado": "", "uf": ""}, {"nome": "UHE Pedra do Cavalo","reservat": "UHE Pedra do Cavalo", "volume": None, "volume_percentual": None, "data": None, "id": 795, "estado": "", "uf": ""}, {"nome": "Açude Barra da Melancia","reservat": "Açude Barra da Melancia", "volume": None, "volume_percentual": None, "data": None, "id": 1041, "estado": "", "uf": ""}, {"nome": "Açude Mesa de Pedra","reservat": "Açude Mesa de Pedra", "volume": None, "volume_percentual": None, "data": None, "id": 1055, "estado": "", "uf": ""}]

        answer_1 =[{"nome": "Barragem Jabiberi","reservat": "Barragem Jabiberi", "volume": None, "volume_percentual": None, "data": None, "id": 751, 'semelhanca': 100, "apelido": "", "estado": "", "uf": ""}]
        self.assertEqual(funcoes_aux.reservoirs_similar("jabiberi", reservoirs,50), answer_1)

        answer_2 = [{"nome": "Açude Barra da Melancia","reservat": "Açude Barra da Melancia", "volume": None, "volume_percentual": None, "data": None, "id": 1041, 'semelhanca': 100, "apelido": "", "estado": "", "uf": ""}, {"reservat": "Açude Mesa de Pedra","nome": "Açude Mesa de Pedra", "volume": None, "volume_percentual": None, "data": None, "id": 1055, 'semelhanca': 100, "apelido": "", "estado": "", "uf": ""}]
        self.assertEqual(funcoes_aux.reservoirs_similar("acude", reservoirs,50), answer_2)

if __name__ == '__main__':
    unittest.main()
