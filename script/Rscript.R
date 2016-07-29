#Importanto tabela Municipios

library(dplyr)

municipios_sab <- read.csv("data/municipios_sab.csv", header=T)

head(municipios_sab)

to_print_municipio <- select(municipios_sab, GEOCODIGO, GEOCODIGO1, MUNICIPIO, UF_COD, MESO_COD, MICRO_COD, AREA_KM2)
colnames(to_print_municipio) <- c("ID", "GEOCOD", "NOME_MUNICIPIO", "UF_COD", "MESO_COD", "MICRO_COD", "AREA_KM2")

to_print_estado <- unique(select(municipios_sab, UF_COD, UF, REGIAO))

to_print_mesoregiao <- unique(select(municipios_sab, MESO_COD, MESOREGIAO))

to_print_microregiao <- unique(select(municipios_sab, MICRO_COD, MICROREGIA))

#reservatorios2006.2016 <- read.csv("~/Projetos/sab-api/script/reservatorios2006-2016.csv")

reservatorios <- read.csv("~/Projetos/sab-api/data/reservatorios.csv")
head(reservatorios)

to_print_reservatorios <- select(reservatorios, GEOCODIGO, NOME, RESERVAT, BACIA, TIPO_RESER, AREA_M2, PERIM, HECTARES, CAP_HM3)