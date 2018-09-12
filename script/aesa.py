#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import requests
from unicodedata import normalize
from fuzzywuzzy import fuzz
import re
import urllib, json
from datetime import datetime
import aux_collection_insert


reload(sys)
sys.setdefaultencoding('utf8')

def remove_accents(txt):
	if (type(txt) is str):
		txt= unicode(txt, "utf-8")
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

paraiba = aux_collection_insert.consulta_BD("SELECT DISTINCT r.id id_reservatorio, r.nome nome_reservatorio, r.reservat reservat, r.capacidade capacidade,"
				" mo2.data_info data_info, mo2.cota cota, mo2.volume volume, mo2.volume_percentual volumePercentual "
				"FROM tb_estado e, tb_municipio mu, tb_reservatorio_municipio rm, tb_reservatorio r, "
				"(SELECT mon.id id_reservatorio, mo.cota, mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d-%m-%Y') data_info "
				"FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id, max(m.data_informacao) AS maior_data FROM tb_reservatorio r "
				"LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon ON mo.id_reservatorio=mon.id "
				"AND mon.maior_data=mo.data_informacao) mo2 WHERE e.id = mu.id_estado and mu.id=rm.id_municipio and rm.id_reservatorio=r.id "
				"and r.id=mo2.id_reservatorio and e.sigla='PB';")

url = "http://www.aesa.pb.gov.br/aesa-website/resources/data/volumeAcudes/ultimosVolumes/data.json"
response = urllib.urlopen(url)

to_insert = []
aesa = json.loads(response.read())
for json_reservatorio in aesa:
    for reserv in paraiba:
        similaridade_acude = fuzz.token_set_ratio(remove_accents(reserv[1]),remove_accents(json_reservatorio["acude"]))
        apelido = re.sub(remove_accents(reserv[1])+'|acude|barragem|lagoa|[()-]| do | da | de ','',remove_accents(reserv[2]), flags=re.IGNORECASE).strip()
        similaridade_apelido = fuzz.token_set_ratio(remove_accents(apelido),remove_accents(json_reservatorio["acude"]))
        capacidade = round(float(json_reservatorio["capacidade"])/1000000,2)
        if ((similaridade_acude>=80 or similaridade_apelido>=80)):
            if (json_reservatorio["data"] is not None and ((reserv[4] is None) or (datetime.strptime(reserv[4], '%d-%m-%Y') < datetime.strptime(json_reservatorio["data"][2], '%Y-%m-%d')))):
                ultimo_monitoramento = [reserv[0],reserv[5], reserv[6], reserv[7], reserv[4]]
                to_add = [[reserv[0],'',round(float(json_reservatorio["data"][1])/1000000,2), (float(json_reservatorio["data"][1])/float(json_reservatorio["capacidade"]))*100,
                	datetime.strptime(json_reservatorio["data"][2], '%Y-%m-%d').strftime('%Y-%m-%d')]]
                to_insert.extend(aux_collection_insert.retira_ruido(to_add,ultimo_monitoramento, "AESA"))

                # Para mostrar ao bot que o reservatorio foi atualizado
                aux_collection_insert.update_BD("UPDATE tb_user_reservatorio SET atualizacao_reservatorio = 1 WHERE id_reservatorio="+str(reserv[0])+";")

aux_collection_insert.insert_many_BD(to_insert)
