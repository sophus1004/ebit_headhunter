import logging
from typing import List
from fastapi import FastAPI, UploadFile, Body, File
from fastapi.middleware.cors import CORSMiddleware
from core.config import AppConfig
from core.messages import ServerMessages
from core.initialize_db import InitializeDB
from api.get_info import GetInfo
from api.regist_data import RegistData
from api.vector_search import VectorSearch

logger = logging.getLogger("uvicorn.error")

app = FastAPI()
config = AppConfig()
initialize_db = InitializeDB(config)
get_info = GetInfo(config)
regist_data = RegistData(config, initialize_db)
vector_search = VectorSearch(config, initialize_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (개발 중)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

@app.on_event("startup")
def startup_event():
    logger.info(ServerMessages.INITIALIZE)
    initialize_db.create_mariadb_table()
    initialize_db.create_milvus_collections()
    logger.info(ServerMessages.INITIALIZE_COMPLETE)

@app.get("/info")
async def info():
    return get_info.get_server_info()

@app.post("/regist_data")
async def upload_data(file: UploadFile = File(...)):
    result = regist_data.data_insert(file)
    return result

@app.post("/search")
async def search(
    query: str = Body(...),
    collection_names: List[str] = Body(...),
    top_k: int = Body(1)
):
    return vector_search.search(
        collection_names=collection_names,
        query_text=query,
        top_k=top_k
    )