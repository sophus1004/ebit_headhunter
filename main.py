from fastapi import FastAPI, UploadFile, Body, File
from core.config import AppConfig
from core.init_db import create_mariadb_table, create_milvus_collections
from api.GetInfo import get_server_info
from api.RegistData import RegistData
from api.VectorSearch import VectorSearch

# ✅ 설정 객체 생성
app = FastAPI()
config = AppConfig()
regist_data = RegistData(config)
vector_search = VectorSearch(config)

# ✅ 서버 시작 시 DB 및 Milvus 초기화
@app.on_event("startup")
def startup_event():
    print("🚀 서버 시작 → DB 및 Milvus 초기화 시작")
    mariadb_msg = create_mariadb_table(config)
    print(mariadb_msg)
    milvus_msg = create_milvus_collections(config)
    print(milvus_msg)
    print("✅ 초기화 완료")

@app.get("/info")
def info():
    return get_server_info(config)

@app.post("/regist_data")
async def upload_data(file: UploadFile = File(...)):
    result = regist_data.upload_jsonl(file)
    return result

@app.post("/search")
async def search(
    query: str = Body(...),
    collection_name: str = Body(...),
    top_k: int = Body(1)
    ):
    return vector_search.search(
        collection_name=collection_name,
        query_text=query,
        top_k=top_k
    )