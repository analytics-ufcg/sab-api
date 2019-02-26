import requests
import xml.etree.ElementTree as et
import aux_collection_insert
from datetime import datetime


last_dates = {}
formato_data_1 = '%d/%m/%Y'
formato_data_2 = '%d-%m-%Y'
formato_data_3 = '%Y-%m-%dT%H:%M:%S'

ultimos_monitoramentos = aux_collection_insert.consulta_BD("SELECT mon.id, mo.cota, mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d-%m-%Y') FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id, max(m.data_informacao) AS maior_data FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao WHERE mon.id IN (19123,19116,19122,19124,19125,19121,19126);")
for monit in ultimos_monitoramentos:
	if monit[-1] is not None:
		last_dates[monit[0]] = datetime.strptime(monit[-1],formato_data_2)

data_final = datetime.now()
uhes = ['19123','19116','19122','19124','19125','19121','19126']

cabecalho = ['Codigo','Reservatorio','Cota','Capacidade','Volume','VolumePercentual','DataInformacao']
to_insert = []
to_insert_monitoring = []
reserv_info = aux_collection_insert.consulta_BD("SELECT id, capacidade, volume_minimo, volume_util FROM INSA.tb_reservatorio where id in (19123,19116,19122,19124,19125,19121,19126);")
# capacidade, volume_minimo, volume_util
uhe_info = {}
for row in reserv_info:
	uhe_info[str(row[0])] = [float(row[1])] + [row[2]] + [row[3]]
for uhe in uhes:
	if uhe not in last_dates:
		start = datetime.strptime('01/01/1970',formato_data_1)
	else:
		start = last_dates[int(uhe)]
	init = start.strftime(formato_data_1)
	end = data_final.strftime(formato_data_1)
	if start < data_final:
		response = requests.get('http://sarws.ana.gov.br/SarWebService.asmx/DadosHistoricosSIN?CodigoReservatorio='+ uhe +'&DataInicial='+ init +'&DataFinal='+ end)
		tree = et.fromstring(response.content)
		for row in tree:
			#id_reservatorio,volume_util_acumulado,cota,afluencia,defluencia,data_informacao,fonte
			line = []
			#id_reservatorio,cota,volume,volume_percentual,data_informacao,visualizacao,fonte
			line_monitoring = [uhe,0,0,0,0,1,'ANA']
			for element in row:
				if element.tag.replace('{http://sarws.ana.gov.br}','') != 'nome_reservatorio':
					if element.tag.replace('{http://sarws.ana.gov.br}','') == 'data_medicao':
						line += [datetime.strptime(element.text,formato_data_3).strftime(formato_data_3)] + ['ANA']
						to_insert += [line]
						line_monitoring[4] = datetime.strptime(element.text,formato_data_3).strftime(formato_data_3)
						to_insert_monitoring += [line_monitoring]
					elif element.tag.replace('{http://sarws.ana.gov.br}','') == 'cota':
						line += [element.text]
						line_monitoring[1] = element.text
					elif element.tag.replace('{http://sarws.ana.gov.br}','') == 'volumeUtil':
						if element.text is not None:
							vol_ac = float(str(element.text))*uhe_info[uhe][2]/100
							line += [format(vol_ac,'.2f')]
							line_monitoring[2] = format(vol_ac+uhe_info[uhe][1],'.2f')
							line_monitoring[3] = format((vol_ac+uhe_info[uhe][1])*100/uhe_info[uhe][0],'.2f')
						else:
							line += [element.text]
					else:
						line += [element.text]
		aux_collection_insert.update_BD("UPDATE tb_user_reservatorio SET atualizacao_reservatorio = 1 WHERE id_reservatorio="+uhe+";")
aux_collection_insert.insert_many_BD_uhe(to_insert)
aux_collection_insert.insert_many_BD(to_insert_monitoring)
