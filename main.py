from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# os.environ para despliegue. Descomente cuando ya probó todo local.

client = MongoClient(os.environ["MONGO_URI"])
db = client["ISIS2304D09202610"]


@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}

@app.get("/bares")
def get_bares():
    bares = list(
        db.Bares.find({}, {'_id': 1, 'nombre': 1})
    )

    for b in bares:
        b['_id'] = str(b['_id'])

    return bares

@app.get("/test-db")
def test_db():

    return {
        "bases": client.list_database_names(),
        "colecciones": db.list_collection_names()
    }
#Fin validaciones

@app.get('/bares/{bar_id}/comentarios')
def get_comentarios(bar_id: int):

    bar = db.Bares.find_one(
        {'_id': bar_id},
        {'_id': 0, 'comentarios': 1}
    )

    if not bar:
        return {"error": "Bar no encontrado"}

    return bar.get('comentarios', [])


@app.post('/bares/{bar_id}/comentarios')
def post_comentario(bar_id: int, coment: str, autor: str):

    comentario = {
        'autor': autor,
        'reseña': coment,
        'fecha': datetime.now().isoformat()
    }

    db.Bares.update_one(
        {'_id': bar_id},
        {
            '$push': {
                'Comentarios': comentario
            }
        }
    )

    return {'mensaje': 'Comentario agregado al bar'}


# GET eventos
@app.get('/bares/{bar_id}/eventos')
def get_eventos(bar_id: int):

    eventos = list(
        db.Eventos.find(
            {'bar_id': bar_id},
            {'_id': 0}
        )
    )

    return eventos


# POST eventos
@app.post('/bares/{bar_id}/eventos')
def post_evento(bar_id: int, datos: dict, costo:int, nombre:str):

    datos['barId'] = bar_id
    datos['fecha_creacion'] = datetime.now().isoformat()
    datos['costoEntrada'] = costo
    datos['nombre'] = nombre

    db.Eventos.insert_one(datos)

    return {'mensaje': 'Evento guardado'}

