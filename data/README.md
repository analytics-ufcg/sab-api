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

Este projeto utiliza o shapefile com o contorno do Semiárido brasileiro com sua divisão estadual.

Contorno do semiárido:
[/data/shapefiles/semiarido.shp](https://github.com/github/analytics-ufcg/sab-api/master/data/shapefiles/semiarido.shp)

## 2 Conversão para GeoJSON e TopoJSON

Após instalados os requisitos, execute os comandos na raiz do projeto:

```
ogr2ogr -f GeoJSON data/geojson/semiarido.json data/shapefiles/semiarido.shp
topojson -o data/topojson/sab.json --id-property SIGLA --properties SIGLA=uf -- data/geojson/semiarido.json
toposimplify -o data/topojson/semiarido.json -P 0.05 data/topojson/sab.json
rm data/geojson/semiarido.json
rm data/topojson/sab.json
```
