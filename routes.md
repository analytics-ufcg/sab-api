#**Rotas da api**

## Shapes
### **Estados**
*GET*           /api/estados/sab

### **Municípios**
*GET*           /api/municipios
*GET*           /api/municipios/sab

### **Brasil**
*GET*           /api/pais

### **Reservatórios**
*GET*           /api/reservatorios

## Informações
### **Reservatórios**
*GET*           /api/reservatorios/info
*GET*           /api/reservatorios/:id/info

### **Reservatórios e municípios**
*GET*           /api/pesquisa/municipio_reservatorio

## Monitoramento
### **Reservatórios**
*GET*           /api/reservatorios/:id/monitoramento
*GET*           /api/reservatorios/:id/monitoramento/completo
*GET*           /api/reservatorios/:id/monitoramento/csv


## Similares
### **Reservatórios**
*GET*           /api/reservatorios/similares/:nome/:limiar


## Equivalentes
### **Reservatórios**
*GET*           /api/reservatorio/equivalente/bacia
*GET*           /api/reservatorio/equivalente/estado


## Upload manual
### **Verificação**
*POST*           /api/upload/verificacao
*OPTIONS*        /api/upload/verificacao
*POST*           /api/upload/confirmacao
*OPTIONS*        /api/upload/confirmacao
