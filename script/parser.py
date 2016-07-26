# coding: utf-8

import sys
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

fileToWrite = open('Boqueirao.csv','w')

cabecalho = 'Código;Reservatório;Cota;Capacidade;Volume;VolumePercentual;DataInformacao;'
fileToWrite.write(cabecalho + '\n')

to_print = []
reservatorio = ''
count = 1

soup = BeautifulSoup(open("c1.txt", "r"), 'html.parser')

for link in soup.find_all('td'):
	if not reservatorio:
		reservatorio = link.get_text().strip() + ";"
	elif count < 7:
		reservatorio += link.get_text().strip() + ";"
		count += 1
	else:
		to_print.append(reservatorio)
		reservatorio = link.get_text().strip() + ";"
		count = 1

to_print.append(reservatorio)

fileToWrite.write('\n'.join(to_print) + "\n")
fileToWrite.close()

#print to_print

print "ok"
