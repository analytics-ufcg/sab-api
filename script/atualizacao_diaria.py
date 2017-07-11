from datetime import datetime
print str(datetime.now()) + " - inicio do script diario"
print str(datetime.now()) + " - script da ana iniciado"
import insert_collection_on_DB
print str(datetime.now()) + " - script da ana finalizado"
print str(datetime.now()) + " - script do governo rn iniciado"
import governo_rn
print str(datetime.now()) + " - script do governo rn finalizado"
import aux_collection_insert
aux_collection_insert.update_BD('call refresh_mv_monitoramento;')
print str(datetime.now()) + " - fim do script diario"
