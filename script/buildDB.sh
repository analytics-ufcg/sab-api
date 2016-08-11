echo "Iniciando script BuildDB"
mysql -h db-insa -uroot -p < db_insa.sql
echo "Tabelas criadas"
Rscript Rscript.R
echo "Banco povoado!"

