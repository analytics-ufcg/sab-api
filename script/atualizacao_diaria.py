from datetime import datetime
print str(datetime.now()) + " - inicio do script diario"
print str(datetime.now()) + " - script da ana iniciado"
import insert_collection_on_DB
print str(datetime.now()) + " - script da ana finalizado"
print str(datetime.now()) + " - script do governo rn iniciado"
import governo_rn
print str(datetime.now()) + " - script do governo rn finalizado"
print str(datetime.now()) + " - script da demanda iniciado"
insert_demanda_on_BD.popular_demanda()
print str(datetime.now()) + " - script da demanda finalizado"
print str(datetime.now()) + " - script das uhes iniciado"
import uhe
print str(datetime.now()) + " - script das uhes finalizado"
import aux_collection_insert
aux_collection_insert.update_BD('call refresh_mv_monitoramento;')
aux_collection_insert.update_BD('call refresh_mv_monitoramento_estado;')
print str(datetime.now()) + " - fim do script diario"
