# coding: utf-8
import glob
import sys
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

files = glob.glob(sys.argv[1])
fileToWrite = open(sys.argv[2],'w')

cabecalho = 'Código;Reservatório;Cota;Capacidade;Volume;VolumePercentual;DataInformacao;'
fileToWrite.write(cabecalho + '\n')

numero_colunas = 7

for file in files:
	print file
	to_print = []
	reservatorio = ''
	count_colunas = 1

	soup = BeautifulSoup(open(file, "r"), 'html.parser')

	for link in soup.find_all('td'):
		if not reservatorio:
			reservatorio = link.get_text().strip() + ";"
		elif count_colunas < numero_colunas:
			reservatorio += link.get_text().strip() + ";"
			count_colunas += 1
		else:
			to_print.append(reservatorio)
			reservatorio = link.get_text().strip() + ";"
			count_colunas = 1

	if len(reservatorio.split(";")) > numero_colunas:
		to_print.append(reservatorio)

	fileToWrite.write('\n'.join(to_print) + "\n")

fileToWrite.close()
