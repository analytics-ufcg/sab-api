## Instalação de library
# install.packages("dplyr")
# install.packages("data.table")
# install.packages("stringdist")
# install.packages("lubridate")
# install.packages("DBI")

library(dplyr)
library(data.table)
library(stringdist)
library(lubridate)

### Funções criadas para auxiliar no script

## Tratamento dos municípios

# Verifica qual é o município que mais se aproxima da lista de município
closestMatch = function(string, stringVector){
  stringVector[amatch(string, stringVector, maxDist=2, matchNA = FALSE)]
}

match_municipio <- function(municipios, municipios_completo){
  df <- data.frame(municipio=character(), 
                   municipio_new=character(), 
                   stringsAsFactors=FALSE)
  
  for(value in municipios){
    df <- rbind(df, data.frame(municipio=value, 
                               municipio_new = closestMatch(value, municipios_completo), 
                               stringsAsFactors=FALSE))
  }
  df
}

# Verifica se existe mais de um nome de município em uma mesmo reservatório. Se existir ele duplica a linha
unica_cidade_reservatorio <- function(x) {
  output <- data.frame(PERIM = as.numeric(), 
                       AREA_M2 = as.numeric(),
                       HECTARES = as.numeric(), 
                       GEOCODIGO = as.numeric(),
                       RESERVAT = as.character(),
                       NOME = as.character(),
                       BACIA = as.character(),
                       TIPO_RESER = as.character(),
                       CAP_HM3 = as.numeric(),
                       MUNICIPIO = as.character(),
                       ESTADO = as.character())
  
  if (length(grep("/", x[10])) == 1){
    for (i in strsplit(x[10], "/")[[1]]){
      output <- rbind(output, data.frame(PERIM = x[1], 
                                         AREA_M2 = x[2],
                                         HECTARES = x[3], 
                                         GEOCODIGO = x[4],
                                         RESERVAT = x[5],
                                         NOME = x[6],
                                         BACIA = x[7],
                                         TIPO_RESER = x[8],
                                         CAP_HM3 = x[9],
                                         MUNICIPIO = i,
                                         ESTADO = x[11]))
    }
  } else {
    output <- rbind(output, data.frame(PERIM = x[1], 
                                       AREA_M2 = x[2],
                                       HECTARES = x[3], 
                                       GEOCODIGO = x[4],
                                       RESERVAT = x[5],
                                       NOME = x[6],
                                       BACIA = x[7],
                                       TIPO_RESER = x[8],
                                       CAP_HM3 = x[9],
                                       MUNICIPIO = x[10],
                                       ESTADO = x[11]))
  }
  return (output)
}

## Tabela Município
municipios_sab <- read.csv("../data/municipios_sab.csv", header=TRUE, stringsAsFactors=FALSE)
municipios_sab <- rbind(municipios_sab, data.frame(ID = -99,
                                                    GEOCODIGO = 999999,
                                                    GEOCODIGO1 = 999999,
                                                    MUNICIPIO = 9999999,
                                                    UF_COD = 99,
                                                    UF   = 9999999,
                                                    REGIAO = 999999,
                                                    MESO_COD = 9999,
                                                    MESOREGIAO = 9999999,
                                                    MICRO_COD = 99999,
                                                    MICROREGIA = 9999999,
                                                    AREA_KM2 = 999,
                                                    SEMIARIDO = 999))
  
to_print_municipio <- select(municipios_sab, GEOCODIGO, GEOCODIGO1, MUNICIPIO, UF_COD, MESO_COD, MICRO_COD, AREA_KM2)
colnames(to_print_municipio) <- c("id", "geocod_min", "nome", "id_estado", "id_mesoregiao", "id_microregiao", "area")

## Tabela Estado 
estados_br <- read.csv("../data/estados_br.csv", header=TRUE, stringsAsFactors=FALSE)
head(estados_br)
estados_br <- rbind(estados_br, data.frame(ID = -99,
                                           CD_GEOCODU = 99,
                                           NM_ESTADO = 9999,
                                           NM_REGIAO = 9999,
                                           SIGLA = 99))

to_print_estado <- unique(select(estados_br, CD_GEOCODU, NM_ESTADO, NM_REGIAO, SIGLA))
colnames(to_print_estado) <- c("id", "nome", "nome_regiao", "sigla")

## Tabela MesoRegiao
to_print_mesoregiao <- unique(select(municipios_sab, MESO_COD, MESOREGIAO))
colnames(to_print_mesoregiao) <- c("id","nome")


## Tabela MicroRegiao
to_print_microregiao <- unique(select(municipios_sab, MICRO_COD, MICROREGIA))
colnames(to_print_microregiao) <- c("id","nome")

## Tabela Reservatorio
reservatorios <- read.csv("../data/reservatorios.csv", header=TRUE, stringsAsFactors=FALSE)
to_print_reservatorios <- select(reservatorios, GEOCODIGO, NOME, RESERVAT, BACIA, TIPO_RESER, AREA_M2, PERIM, HECTARES, CAP_HM3)
colnames(to_print_reservatorios) <- c("id", "nome", "reservat", "bacia", "tipo", "area", "perimetro", "hectares", "capacidade")

## Monitoramento
reservatorios2006.2016 <- read.csv("../data/reservatorios2006-2016.csv", header=TRUE, stringsAsFactors=FALSE)
colnames(reservatorios2006.2016) <- c("ID_reser", "Reservatorio", "Cota", "Capacidade", "Volume", "VolumePercentual", "DataInformacao")
to_print_monitoramento <- select(reservatorios2006.2016, ID_reser, Cota, Volume, VolumePercentual, DataInformacao)
to_print_monitoramento$DataInformacao = as.Date(parse_date_time(to_print_monitoramento$DataInformacao,"dmy"))
colnames(to_print_monitoramento) <- c("id_reservatorio", "cota", "volume", "volume_percentual", "data_informacao")

## Tabela Reservatorio Município
reservatorios <- rbindlist(apply(reservatorios, 1, unica_cidade_reservatorio))
reservatorios$MUNICIPIO <- as.character(reservatorios$MUNICIPIO)

# Ajuste do nome de alguns municípios
reservatorios$MUNICIPIO[reservatorios$MUNICIPIO == "Conceição da Feira"] <- "Feira de Santana"
reservatorios$MUNICIPIO[reservatorios$MUNICIPIO == "São João Rio Peixe"] <- "São João do Rio do Peixe"
reservatorios$MUNICIPIO[reservatorios$MUNICIPIO == "Senhor Bonfim"] <- "Senhor do Bonfim"
reservatorios$MUNICIPIO[reservatorios$MUNICIPIO == "São José Caiana"] <-"São José de Caiana"

reservatorios$MUNICIPIO <- match_municipio(reservatorios$MUNICIPIO, municipios_sab$MUNICIPIO)$municipio_new

to_print_reservatorio_municipio <- select(reservatorios, GEOCODIGO, MUNICIPIO, ESTADO)
to_print_reservatorio_municipio$MUNICIPIO <- as.character(to_print_reservatorio_municipio$MUNICIPIO)
municipios_sab$MUNICIPIO <- as.character(municipios_sab$MUNICIPIO)

to_print_reservatorio_municipio <- left_join(as.data.frame(to_print_reservatorio_municipio), 
                                             select(municipios_sab, MUNICIPIO, GEOCODIGO), by = "MUNICIPIO")
colnames(to_print_reservatorio_municipio) <- c("id_reservatorio", "MUNICIPIO", "ESTADO", "id_municipio")

to_print_reservatorio_municipio <- select(to_print_reservatorio_municipio, id_reservatorio, id_municipio)

# 99999 São municípios não mapeados pelo municipios_sab
to_print_reservatorio_municipio[is.na(to_print_reservatorio_municipio)] <- 999999



############### INSERE NO BD

library(DBI)

con <- dbConnect(RMySQL::MySQL(),
                 group="INSA")
dbWriteTable(con, "tb_mesoregiao", value=to_print_mesoregiao, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_microregiao", value=to_print_microregiao, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_estado", value=to_print_estado, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_municipio", value=to_print_municipio, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_reservatorio", value=to_print_reservatorios, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_reservatorio_municipio", value=to_print_reservatorio_municipio, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbWriteTable(con, "tb_monitoramento", value=to_print_monitoramento, overwrite=FALSE, append=TRUE, row.names=FALSE)

dbDisconnect(con)

teste <- dbGetQuery(con, "select * from tb_microregiao")

to_print_microregiao[(to_print_microregiao$id)==27005,]
