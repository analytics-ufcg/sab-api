echo "PEGANDO OS DADOS"
sh get_dados.sh
echo "COLETA DE DADOS FINALIZADA. TRANSFORMANDO OS DADOS EM UM CSV"
python parser.py "dados/*.html" "reservatorios.csv"
echo "FIM"