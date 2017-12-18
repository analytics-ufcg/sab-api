# Importação e conversão de dados georeferenciados

## Requisitos

A biblioteca Geospatial Data Abstraction Library, ou GDAL inclui a ferramenta de manipulação de shapefiles OGR (ogr2ogr):

```
brew install gdal
```

O TopoJSON é um pacote Node.JS para conversão e simplificação de arquivos geoespaciais:

```
npm install -g topojson@1
```

## 1 Shapefiles

O Esri Shapefile ou simplesmente shapefile é um formato popular de arquivo contendo dados geoespaciais em forma de vetor usado por Sistemas de Informações Geográficas (SIG). Foi desenvolvido e regulamentado pela ESRI como uma especificação aberta para interoperabilidade por dados entre os softwares de Esri e de outros fornecedores.

Este projeto utiliza o shapefile com o contorno do Semiárido brasileiro com sua divisão estadual, bem
como o shapefile com a geolocalização de cada reservatório.

Contorno do semiárido: [/data/shapefiles/MUNICIPIOS_SAB.shp](https://github.com/github/analytics-ufcg/sab-api/master/data/shapefiles/MUNICIPIOS_SAB.shp)
Localização dos reservatórios: [/data/shapefiles/RESERVATORIOS.shp](https://github.com/github/analytics-ufcg/sab-api/master/data/shapefiles/RESERVATORIOS.shp)

## 2 Conversão para GeoJSON e TopoJSON

Após instalados os requisitos, execute os comandos na raiz do projeto:

```
ogr2ogr -f GeoJSON data/geojson/semiarido.json data/shapefiles/MUNICIPIOS_SAB.shp
ogr2ogr -f GeoJSON data/geojson/reservatorios.json data/shapefiles/RESERVATORIOS.shp

topojson -o data/topojson/sab.json --id-property CD_GEOCUF --properties CD_GEOCUF=id -- data/geojson/semiarido.json
topojson -o data/topojson/reservatorios.json --id-property CD_RESERV_ --properties CD_RESERV_=id -- data/geojson/reservatorios.json

toposimplify -o data/topojson/semiarido.json -P 0.05 data/topojson/sab.json
```
