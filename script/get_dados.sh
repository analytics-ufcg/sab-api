#!/usr/bin/bash

filename = "codigoANAt.txt"

while read line           
do           
    echo-e "$ line \ n"           
done < filename  


#mkdir reservatorios
#for prop in `grep -v rop ../dados/proposicoes-votadas.csv | cut -d, -f1`; 
#do 
#	if [ ! -f ../dados/proposicoes/p$prop.xml ]; 
#	then 
#		curl --connect-timeout 15 --retry 5 --keepalive-time 10 'http://www.camara.gov.br//SitCamaraWS/Proposicoes.asmx/ObterProposicaoPorID?idProp='$prop > ../dados/proposicoes/p$prop.xml; 
#		sleep 3;
#	fi
#done





echo "Ok"