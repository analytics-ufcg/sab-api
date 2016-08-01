library(dplyr)

# Tabela Município
municipios_sab <- read.csv("data/municipios_sab.csv", header=T)
to_print_municipio <- select(municipios_sab, GEOCODIGO, GEOCODIGO1, MUNICIPIO, UF_COD, MESO_COD, MICRO_COD, AREA_KM2)
colnames(to_print_municipio) <- c("ID", "GEOCOD", "NOME_MUNICIPIO", "UF_COD", "MESO_COD", "MICRO_COD", "AREA_KM2")

# Tabela Estado 
estados_br <- read.csv("data/estados_br.csv", header=T)
to_print_estado <- unique(select(estados_br, CD_GEOCODU, NM_ESTADO, NM_REGIAO, SIGLA))
colnames(to_print_estado)[1] <- "ID"

# Tabela MesoRegiao
to_print_mesoregiao <- unique(select(municipios_sab, MESO_COD, MESOREGIAO))

# Tabela MicroRegiao
to_print_microregiao <- unique(select(municipios_sab, MICRO_COD, MICROREGIA))

# Tabela Reservatorio
reservatorios <- read.csv("~/Projetos/sab-api/data/reservatorios.csv")
head(reservatorios)

to_print_reservatorios <- select(reservatorios, GEOCODIGO, NOME, RESERVAT, BACIA, TIPO_RESER, AREA_M2, PERIM, HECTARES, CAP_HM3)
colnames(to_print_reservatorios)[1] <- "ID"

# Monitoramento
reservatorios2006.2016 <- read.csv("~/Projetos/sab-api/script/reservatorios2006-2016.csv")
head(reservatorios2006.2016)

# Tabela Reservatorio Município
to_print_reservatorio_municipio <- select(reservatorios, GEOCODIGO, MUNICIPIO, ESTADO)

to_print_reservatorio_municipio$MUNICIPIO <- as.character(to_print_reservatorio_municipio$MUNICIPIO)
municipios_sab$MUNICIPIO <- as.character(municipios_sab$MUNICIPIO)

to_print_reservatorio_municipio <- left_join(to_print_reservatorio_municipio, select(municipios_sab, MUNICIPIO, GEOCODIGO), by = "MUNICIPIO")
colnames(to_print_reservatorio_municipio) <- c("ID_reservatorio", "MUNICIPIO", "ESTADO", "ID_municipio")

to_print_reservatorio_municipio <- select(to_print_reservatorio_municipio, ID_reservatorio, ID_municipio)


# Tratamento dos municípios

# install.packages("stringdist")
library(stringdist)

closestMatch = function(string, stringVector){
  stringVector[amatch(string, stringVector, maxDist=2, matchNA = FALSE)]
}


match_municipio <- function(municipios, municipios_completo){
  df <- data.frame(municipio=character(), 
                   municipio_new=character(), 
                   stringsAsFactors=FALSE)
  
  for(value in municipios){
    if(length(grep("/", value)) == 1){
      for (i in strsplit(x, "/")[[1]]){
        df <- rbind(df, data.frame(municipio=i, 
                                   municipio_new=closestMatch(i, municipios_completo), 
                                   stringsAsFactors=FALSE))
      }
    } else {
      df <- rbind(df, data.frame(municipio=value, 
                                 municipio_new=closestMatch(value, municipios_completo), 
                                 stringsAsFactors=FALSE))
    } 
  }
  
  df
  
}

xx <- match_municipio(reservatorios$MUNICIPIO, municipios_sab$MUNICIPIO)
