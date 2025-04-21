# Backend para MVP buxa, apenas para verificar funcionalidades
## É uma bomba!! usar apenas localmente (sandbox pode aceitar código malicioso)

# Comandos
## Usando Anaconda (mais fácil para instalar o gdal):
```
conda install -c conda-forge gdal numpy scipy
```
Criar ambiente virtual:
```
py -3.10 -m venv venv
```
Executar:
```
// Windows:
venv\Scripts\activate
// 
```
Servidor com Flask:
```
set FLASK_APP=app
set FLASK_ENV=development
```
```
flask run --host 0.0.0.0 --port 5000
```
