[![Build Status](https://travis-ci.org/analytics-ufcg/sab-api.svg?branch=master)](https://travis-ci.org/analytics-ufcg/sab-api)

# Monitoramento dos reservatórios da região Semi-árida brasileira

Contém o acesso aos dados do monitoramento em uma API.

## Desenvolvimento

Para instalar as dependencias necessárias só é necessário executar o comando abaixo na pasta do projeto:

```
pip install -r requirements.txt
```

Também é necessário o arquivo de configuração do banco de dados que deve ser criado em `~/.my.cnf`. O conteúdo do arquivo é o seguinte:

```
[INSA]
user=usuarioDoBD
password=SenhaDoUsuario
host=db-insa
database=INSA
```


Para criar o Banco de dados e populá-lo inicialmente com os dados previamente baixados é necessário:

- instalar o R  na sua máquina:
```
sudo echo "deb http://cran.rstudio.com/bin/linux/ubuntu xenial/" | sudo tee -a /etc/apt/sources.list
gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get install r-base r-base-dev
```

- executar o script:
```
script/buildBD.sh
```

Caso queira que a aplicação tenha a versão mais atual dos dados vindos do site da ANA é necessário:

- instalar:
```
pip install requests
pip install bs4
```

- executar o script:
```
python script/insert_month_on_DB.py
```

Caso queira colocar uma rotina no Ubuntu para todo primeiro dia do mês atualizar o banco de dados as 5 da manhã:
```
crontab -e
0 5 1 * *   <caminho>/insert_month_on_DB.py

```
