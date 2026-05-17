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


@app.get('/bares/{bar_id}/comentarios')
def get_comentarios(bar_id: int):

    bar = db.bares.find_one(
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

    db.bares.update_one(
        {'_id': bar_id},
        {
            '$push': {
                'comentarios': comentario
            }
        }
    )

    return {'mensaje': 'Comentario agregado al bar'}


# GET eventos
@app.get('/bares/{bar_id}/eventos')
def get_eventos(bar_id: int):

    eventos = list(
        db.eventos.find(
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

    db.eventos.insert_one(datos)

    return {'mensaje': 'Evento guardado'}

