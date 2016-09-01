#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import csv
from unicodedata import normalize

try:
	conn = MySQLdb.connect(read_default_group='INSA')
	cursor = conn.cursor()
	for line in open("db_insa.sql").read().split(';\n'):
		if(line != ""):
			cursor.execute(line)
finally:
	cursor.close()
	conn.close()

def insert_many_BD(insert,values):
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


reader_reservatorios = csv.DictReader(open('../data/reservatorios.csv'))
reservatorios = {}
for row in reader_reservatorios:
	for column, value in row.iteritems():
		reservatorios.setdefault(column, []).append(value)
#CABEÇALHO estados_br
#PERIM,AREA_M2,HECTARES,GEOCODIGO,RESERVAT,NOME,BACIA,TIPO_RESER,CAP_HM3,MUNICIPIO,ESTADO


#tabela tb_estado
tb_estado = zip(estados_br["CD_GEOCODU"], estados_br["NM_ESTADO"], estados_br["NM_REGIAO"], estados_br["SIGLA"])

#tabela tb_reservatorio
tb_reservatorio = zip(reservatorios["GEOCODIGO"], reservatorios["NOME"], reservatorios["RESERVAT"],reservatorios["BACIA"], 
	reservatorios["TIPO_RESER"], reservatorios["AREA_M2"],reservatorios["PERIM"], reservatorios["HECTARES"], reservatorios["CAP_HM3"])


#tabela tb_municipio
tb_municipio = []
municipios_br = zip(cidades_br["ibge_id"],cidades_br["name"],cidades_br["uf"])

for municipio in municipios_br:
	id_uf = estados_br["CD_GEOCODU"][estados_br["SIGLA"].index(municipio[2])]
	if (municipio[0] in municipios_sab["GEOCODIGO"]):
		area = municipios_sab["AREA_KM2"][municipios_sab["GEOCODIGO"].index(municipio[0])]
		tb_municipio.append((municipio[0],municipio[1],id_uf,area,1))
	else:
		tb_municipio.append((municipio[0],municipio[1],id_uf,"",0))


#tabela tb_reservatorio_municipio
tb_reservatorio_municipio = []
info_municipio_reservatorio = zip(reservatorios["GEOCODIGO"], reservatorios["MUNICIPIO"], reservatorios["ESTADO"])


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
			

			for municipio in municipios_br:
				municipio_uf = municipio[1] + " - "+municipio[2]
				if (municipio_uf == municipio_reservatorio_uf):
					tb_reservatorio_municipio.append((municipio_reservatorio[0],municipio[0]))

insert_many_BD("""INSERT INTO tb_estado (id,nome,nome_regiao,sigla) VALUES (%s,%s,%s,%s)""", tb_estado)
insert_many_BD("""INSERT INTO tb_municipio (id,nome,id_estado,area,semiarido) VALUES (%s,%s,%s,%s,%s)""", tb_municipio)
insert_many_BD("""INSERT INTO tb_reservatorio (id,nome,reservat,bacia,tipo,area,perimetro,hectares,capacidade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", tb_reservatorio)
insert_many_BD("""INSERT INTO tb_reservatorio_municipio (id_reservatorio,id_municipio) VALUES (%s,%s)""", tb_reservatorio_municipio)

import insert_month_on_DB