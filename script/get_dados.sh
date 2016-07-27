#!/bin/bash

mkdir dados
input="codigoANA.txt"

while IFS= read -r var
do
  curl "http://sar.ana.gov.br/Medicao/GridMedicoes?DropDownListReservatorios="$var"&dataInicialInformada=01-01-2006&dataFinalInformada=07-07-2016&cliqueiEmPesquisar=true" > dados/"$var".html;
done < "$input"

echo "Ok"