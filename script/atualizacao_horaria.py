from datetime import datetime
print str(datetime.now()) + " - script horario iniciado"
import aesa
import aux_collection_insert
aux_collection_insert.update_BD('call refresh_mv_monitoramento;')
print str(datetime.now()) + " - script horario concluido"
