import logging
from typing import List
from fastapi import FastAPI, UploadFile, Body, File
from fastapi.middleware.cors import CORSMiddleware
from core.config import AppConfig
from core.messages import ServerMessages
from core.initialize_db import InitializeDB
from api.get_info import GetInfo
from api.insert_data import InsertData
from api.vector_search import VectorSearch

logger = logging.getLogger("uvicorn.error")

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# 설정 및 구성 객체 초기화
config = AppConfig()
initialize_db = InitializeDB(config)
get_info = GetInfo(config)
insert_data = InsertData(config, initialize_db)
vector_search = VectorSearch(config, initialize_db)

# CORS 설정: 개발 편의를 위해 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """서버 시작 시 DB 및 Milvus 컬렉션 초기화를 수행합니다."""
    logger.info(ServerMessages.INIT_START)
    initialize_db.create_mariadb_table()
    initialize_db.create_milvus_collections()
    logger.info(ServerMessages.INIT_COMPLETE)


@app.get("/info")
async def api_info():
    """서버 설정 정보 및 상태를 반환합니다.

    Returns:
        dict: 서버 및 설정 정보.
    """
    return get_info.get_server_info()


@app.post("/insert_data")
async def api_insert_data(file: UploadFile = File(...)):
    """업로드된 JSONL 파일을 기반으로 DB 및 Milvus에 데이터를 삽입합니다.

    Args:
        file (UploadFile): 업로드된 JSONL 파일.

    Returns:
        dict: 데이터 삽입 결과 정보.
    """
    result = insert_data.data_insert(file)
    return result


@app.post("/dev_embedding_insert_only")
async def api_dev_embedding_insert_only():
    """DB에 있는 데이터를 Milvus에 임베딩만 수행하는 개발용 엔드포인트입니다.

    Returns:
        dict: 임베딩 삽입 결과 정보.
    """
    result = insert_data.dev_embedding_insert_only()
    return result


@app.post("/search")
async def api_search(
    query: str = Body(...),
    collection_names: str = Body(...),
    top_k: int = Body(1)
):
    """임베딩 벡터 기반 검색을 수행합니다.

    Args:
        query (str): 검색할 쿼리 텍스트.
        collection_names (str): 검색할 Milvus 컬렉션 이름.
        top_k (int): 반환할 유사도 결과 개수. 기본값은 1.

    Returns:
        dict: 검색 결과 리스트.
    """
    return vector_search.only_vector(
        collection_names=collection_names,
        query_text=query,
        top_k=top_k
    )