#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import csv
import json
from unicodedata import normalize
from datetime import datetime

import insert_users_on_DB

try:
	conn = MySQLdb.connect(read_default_group='INSA')
	cursor = conn.cursor()
	for line in open("db_insa.sql").read().split(';\n'):
		if(line != ""):
			cursor.execute(line)
finally:
	cursor.close()
	conn.close()

def execute_many_BD(insert,values):
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	try:
		cursor.executemany(insert, values)
		conn.commit()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	conn.close()

reader_cidades_br = csv.DictReader(open('../data/cidades_br.csv'))
cidades_br = {}
for row in reader_cidades_br:
	for column, value in row.iteritems():
		cidades_br.setdefault(column, []).append(value)
#CABEÇALHO cidades_br
#ibge_id,uf,name,capital,lon,lat,no_accents,alternative_names,microregion,mesoregion


reader_mun_sab = csv.DictReader(open('../data/municipios_sab.csv'))
municipios_sab = {}
for row in reader_mun_sab:
	for column, value in row.iteritems():
		municipios_sab.setdefault(column, []).append(value)
#CABEÇALHO municipios_sab
#ID,GEOCODIGO,GEOCODIGO1,MUNICIPIO,UF_COD,UF,REGIAO,MESO_COD,MESOREGIAO,MICRO_COD,MICROREGIA,AREA_KM2,SEMIARIDO


reader_estado_br = csv.DictReader(open('../data/estados_br.csv'))
estados_br = {}
for row in reader_estado_br:
	for column, value in row.iteritems():
		estados_br.setdefault(column, []).append(value)
#CABEÇALHO estados_br
#ID,CD_GEOCODU,NM_ESTADO,NM_REGIAO,SIGLA


#tabela tb_reservatorio
with open('../data/reserv.json') as data_file:
	_reservatorios = json.load(data_file)
geocodes = {}
tb_reservatorio = []
info_municipio_reservatorio = []
for reservat in _reservatorios['features']:
	geocodes[int(reservat['properties']['GEOCODIGO'])] = reservat['geometry']['coordinates']
	bacia = reservat['properties']['BACIA'].encode('utf8')
	reservat_nome = reservat['properties']['RESERVAT'].encode('utf8')
	if (bacia == "Curimata?"):
		bacia = "Curimataú"
	elif(bacia == "Gar?as"):
		bacia = "Garças"
	elif (bacia == "Corea?"):
		bacia = "Coreaú"
	elif ("São Francisco" in bacia):
		bacia = "São Francisco"

	if (reservat_nome == "Açude Riacho de Santo Ant?nio"):
		reservat_nome = "Açude Riacho de Santo Antônio"
	elif (reservat_nome == "Açude Joaquim T?vora (Feiticeiro)"):
		reservat_nome = "Açude Joaquim Távora (Feiticeiro)"
	elif (reservat_nome == "Açude Pompeu Sobrinho (Choró Lim?o)"):
		reservat_nome = "Açude Pompeu Sobrinho (Choró Limão)"

	tb_reservatorio.append((int(reservat['properties']['GEOCODIGO']),reservat['properties']['NOME'].encode('utf8'), reservat_nome,
		bacia,reservat['properties']['TIPO_RESER'],reservat['properties']['AREA_M2'],reservat['properties']['PERIM'],
		reservat['properties']['HECTARES'],reservat['properties']['CAP_HM3'],reservat['geometry']['coordinates'][1],reservat['geometry']['coordinates'][0]))
	info_municipio_reservatorio.append((int(reservat['properties']['GEOCODIGO']),reservat['properties']['MUNICIPIO'].encode('utf8'),reservat['properties']['ESTADO'].encode('utf8')))

#tabela tb_estado
tb_estado = zip(estados_br["CD_GEOCODU"], estados_br["NM_ESTADO"], estados_br["NM_REGIAO"], estados_br["SIGLA"])

#tabela tb_municipio
tb_municipio = []
municipios_br = zip(cidades_br["ibge_id"],cidades_br["name"],cidades_br["uf"],cidades_br["lat"],cidades_br["lon"])

for municipio in municipios_br:
	id_uf = estados_br["CD_GEOCODU"][estados_br["SIGLA"].index(municipio[2])]
	if (municipio[0] in municipios_sab["GEOCODIGO"]):
		area = municipios_sab["AREA_KM2"][municipios_sab["GEOCODIGO"].index(municipio[0])]
		tb_municipio.append((municipio[0],municipio[1],id_uf,area,municipio[3],municipio[4],1))
	else:
		tb_municipio.append((municipio[0],municipio[1],id_uf,"",municipio[3],municipio[4],0))


#tabela tb_reservatorio_municipio
tb_reservatorio_municipio = []

def remover_acentos(txt):
	if (type(txt) is str):
		txt= unicode(txt, "utf-8")
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

estados_sem_acento = {"nome":[], "uf":[]}
for estado in tb_estado:
	estados_sem_acento["nome"].append(remover_acentos(estado[1]))
	estados_sem_acento["uf"].append(estado[3])


for municipio_reservatorio in info_municipio_reservatorio:
	lista_estados = remover_acentos(municipio_reservatorio[2]).split("/")
	lista_municipios = municipio_reservatorio[1].split("/")
	for munic in lista_municipios:
		for estado in lista_estados:
			uf = estados_sem_acento["uf"][estados_sem_acento["nome"].index(remover_acentos(estado).upper())]
			if(munic == "São João Rio Peixe"):
				munic = "São João do Rio do Peixe"
			elif(munic == "Senhor Bonfim"):
				munic = "Senhor do Bonfim"
			elif(munic == "São José Caiana"):
				munic = "São José de Caiana"
			elif(munic == "Palmeira dos Indios"):
				munic = "Palmeira dos Índios"
			elif(munic == "Curaça"):
				munic = "Curaçá"
			elif(munic == "Cansanço"):
				munic = "Cansanção"
			elif(munic == "Santa Cruz do capibaribe"):
				munic = "Santa Cruz do Capibaribe"

			municipio_reservatorio_uf = munic +" - "+ uf
			if(municipio_reservatorio_uf == "Espinosa - BA"):
				municipio_reservatorio_uf = "Espinosa - MG"
			elif(municipio_reservatorio_uf == "Poções - PE"):
				municipio_reservatorio_uf = "Poção - PE"
			elif(municipio_reservatorio_uf == "Carnaúba - PE"):
				municipio_reservatorio_uf = "Carnaíba - PE"
			elif(municipio_reservatorio_uf == "Olho D'Água - PB"):
				municipio_reservatorio_uf = "Olho d'Água - PB"
			elif(municipio_reservatorio_uf == "Itaje - RN"):
				municipio_reservatorio_uf = "Itajá - RN"
			elif(municipio_reservatorio_uf == "Açuu - RN"):
				municipio_reservatorio_uf = "Açu - RN"
			elif(municipio_reservatorio_uf == "Brejos do Cruz - PB"):
				municipio_reservatorio_uf = "Brejo do Cruz - PB"
			elif(municipio_reservatorio_uf == "Olho D'Água do Borges - RN"):
				municipio_reservatorio_uf = "Olho-d'Água do Borges - RN"
			elif(municipio_reservatorio_uf == "Cariria?u - CE"):
				municipio_reservatorio_uf = "Caririaçu - CE"
			elif(municipio_reservatorio_uf == "Uirauna - PB"):
				municipio_reservatorio_uf = "Uiraúna - PB"
			elif(municipio_reservatorio_uf == "Miraima - CE"):
				municipio_reservatorio_uf = "Miraíma - CE"
			elif(municipio_reservatorio_uf == "Antonio Gonçalves - BA"):
				municipio_reservatorio_uf = "Antônio Gonçalves - BA"
			elif(municipio_reservatorio_uf == "Buique - PE"):
				municipio_reservatorio_uf = "Buíque - PE"
			elif(municipio_reservatorio_uf == "Cachoeira dos Indios - PB"):
				municipio_reservatorio_uf = "Cachoeira dos Índios - PB"
			elif(municipio_reservatorio_uf == "Luis Gomes - RN"):
				municipio_reservatorio_uf = "Luís Gomes - RN"
			elif(municipio_reservatorio_uf == "Carire - CE"):
				municipio_reservatorio_uf = "Cariré - CE"
			elif(municipio_reservatorio_uf == "Mãe d'água - PB"):
				municipio_reservatorio_uf = "Mãe d'Água - PB"
			elif(municipio_reservatorio_uf == "Licenio de Almeida - BA"):
				municipio_reservatorio_uf = "Licínio de Almeida - BA"
			elif(municipio_reservatorio_uf == "São Francisco do Piau? - PI"):
				municipio_reservatorio_uf = "São Francisco do Piauí - PI"
			elif(municipio_reservatorio_uf == "Caraibas - BA"):
				municipio_reservatorio_uf = "Caraíbas - BA"
			elif(municipio_reservatorio_uf == "Maracos - BA"):
				municipio_reservatorio_uf = "Maracás - BA"
			elif(municipio_reservatorio_uf == "Santo Estevão - BA"):
				municipio_reservatorio_uf = "Santo Estêvão - BA"
			elif(municipio_reservatorio_uf == "Iati - AL"):
				municipio_reservatorio_uf = "Iati - PE"
			elif(municipio_reservatorio_uf == "São Luis do Piaui - PI"):
				municipio_reservatorio_uf = "São Luis do Piauí - PI"
			elif(municipio_reservatorio_uf == "Cabrobo - PE"):
				municipio_reservatorio_uf = "Cabrobó - PE"
			elif(municipio_reservatorio_uf == "Jucus - CE"):
				municipio_reservatorio_uf = "Jucás - CE"
			elif(municipio_reservatorio_uf == "Itau - RN"):
				municipio_reservatorio_uf = "Itaú - RN"
			elif(municipio_reservatorio_uf == "Quixele - CE"):
				municipio_reservatorio_uf = "Quixelô - CE"
			elif(municipio_reservatorio_uf == "Solonopole - CE"):
				municipio_reservatorio_uf = "Solonópole - CE"
			elif(municipio_reservatorio_uf == "Iraçuba - CE"):
				municipio_reservatorio_uf = "Irauçuba - CE"
			elif(municipio_reservatorio_uf == "Apuiarus - CE"):
				municipio_reservatorio_uf = "Apuiarés - CE"
			elif(municipio_reservatorio_uf == "Coreau - CE"):
				municipio_reservatorio_uf = "Coreaú - CE"
			elif(municipio_reservatorio_uf == "Tiangua - CE"):
				municipio_reservatorio_uf = "Tianguá - CE"
			elif(municipio_reservatorio_uf == "Puxinan? - PB"):
				municipio_reservatorio_uf = "Puxinanã - PB"
			elif(municipio_reservatorio_uf == "Bel?m do Brejo do Cruz - PB"):
				municipio_reservatorio_uf = "Belém do Brejo do Cruz - PB"
			elif(municipio_reservatorio_uf == "São Domingos Cariri - PB"):
				municipio_reservatorio_uf = "São Domingos do Cariri - PB"

			for municipio in municipios_br:
				municipio_uf = municipio[1] + " - "+municipio[2]
				if (municipio_uf == municipio_reservatorio_uf):
					tb_reservatorio_municipio.append((municipio_reservatorio[0],municipio[0]))

execute_many_BD("""INSERT INTO tb_estado (id,nome,nome_regiao,sigla) VALUES (%s,%s,%s,%s)""", tb_estado)
execute_many_BD("""INSERT INTO tb_municipio (id,nome,id_estado,area,latitude,longitude,semiarido) VALUES (%s,%s,%s,%s,%s,%s,%s)""", tb_municipio)
execute_many_BD("""INSERT INTO tb_reservatorio (id,nome,reservat,bacia,tipo,area,perimetro,hectares,capacidade,latitude,longitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", tb_reservatorio)
execute_many_BD("""INSERT INTO tb_reservatorio_municipio (id_reservatorio,id_municipio) VALUES (%s,%s)""", tb_reservatorio_municipio)


########  REMOVENDO dos açudes (Estreito e Pai Mané) as cidades que não são contabilizadas no boletim informativo do INSA
# (Estreito,Espinosa-MG) e (Pai Mané, Iati=AL)
reservatorios_municipios = [(12176,3124302),(12303,2606507)]
execute_many_BD("""DELETE FROM tb_reservatorio_municipio WHERE id_reservatorio=%s and id_municipio=%s""", reservatorios_municipios)


reader_boletim = csv.DictReader(open('../data/dados_boletim.csv'))
boletim_historico = []
formato_data_1 = '%d/%m/%Y'
formato_data_2 = '%Y-%m-%d'
for row in reader_boletim:
	historico =  (row["id"], None, row["volume"], round((float(row["volume"])*100/float(row["capacidade"])),2),
	datetime.strptime(row["data_info"], formato_data_1).strftime(formato_data_2),1, row["fonte"])
	if (historico not in boletim_historico):
		boletim_historico.append(historico)

execute_many_BD("""INSERT INTO tb_monitoramento (id_reservatorio,cota,volume,volume_percentual,data_informacao,visualizacao,fonte) VALUES (%s,%s,%s,%s,%s,%s,%s)""", boletim_historico)

import atualizacao_diaria

#### INSERINDO usuários ao banco de dados
insert_users_on_DB.drop_table()
insert_users_on_DB.create_table()
insert_users_on_DB.insert_user('insa', 'volup14')
insert_users_on_DB.insert_user('admin', '0lh0n4gu4')

#### INSERINDO outorgas para os reservatórios da PB
insert_outorga_on_BD.create_outorga()
insert_outorga_on_BD.popular_outorga()
