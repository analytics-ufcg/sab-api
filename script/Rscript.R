## Instalação de library
# install.packages("dplyr")
# install.packages("data.table")
# install.packages("stringdist")

library(dplyr)
library(data.table)
library(stringdist)

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
municipios_sab <- read.csv("data/municipios_sab.csv", header=TRUE, stringsAsFactors=FALSE)
to_print_municipio <- select(municipios_sab, GEOCODIGO, GEOCODIGO1, MUNICIPIO, UF_COD, MESO_COD, MICRO_COD, AREA_KM2)
colnames(to_print_municipio) <- c("ID_municipio", "GEOCOD", "NOME_MUNICIPIO", "UF_COD", "MESO_COD", "MICRO_COD", "AREA_KM2")

## Tabela Estado 
estados_br <- read.csv("data/estados_br.csv", header=TRUE, stringsAsFactors=FALSE)
to_print_estado <- unique(select(estados_br, CD_GEOCODU, NM_ESTADO, NM_REGIAO, SIGLA))
colnames(to_print_estado)[1] <- "ID_estado"

## Tabela MesoRegiao
to_print_mesoregiao <- unique(select(municipios_sab, MESO_COD, MESOREGIAO))

## Tabela MicroRegiao
to_print_microregiao <- unique(select(municipios_sab, MICRO_COD, MICROREGIA))

## Tabela Reservatorio
reservatorios <- read.csv("data/reservatorios.csv", header=TRUE, stringsAsFactors=FALSE)
to_print_reservatorios <- select(reservatorios, GEOCODIGO, NOME, RESERVAT, BACIA, TIPO_RESER, AREA_M2, PERIM, HECTARES, CAP_HM3)
colnames(to_print_reservatorios)[1] <- "ID_reservatorio"

## Monitoramento
reservatorios2006.2016 <- read.csv("data/reservatorios2006-2016.csv", header=TRUE, stringsAsFactors=FALSE)
colnames(reservatorios2006.2016) <- c("ID_reser", "Reservatorio", "Cota", "Capacidade", "Volume", "VolumePercentual", "DataInformacao")
to_print_monitoramento <- select(reservatorios2006.2016, ID_reser, Cota, Volume, VolumePercentual, DataInformacao)

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
colnames(to_print_reservatorio_municipio) <- c("ID_reservatorio", "MUNICIPIO", "ESTADO", "ID_municipio")

to_print_reservatorio_municipio <- select(to_print_reservatorio_municipio, ID_reservatorio, ID_municipio, MUNICIPIO, ESTADO)

# 99999 São municípios não mapeados pelo municipios_sab
to_print_reservatorio_municipio[is.na(to_print_reservatorio_municipio)] <- 999999







