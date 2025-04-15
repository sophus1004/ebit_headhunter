import jsonlines
import requests
from snowflake import SnowflakeGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from fastapi import UploadFile

class RegistData:
    def __init__(self, config):
        self.config = config

        # DB 연결
        mariadb = config.mariadb
        self.engine = create_engine(
            f"mysql+pymysql://{mariadb.user}:{mariadb.password}"
            f"@{mariadb.host}:{mariadb.port}/{mariadb.database}"
        )
        self.Session = sessionmaker(bind=self.engine)

        # Milvus 연결
        connections.connect(
            alias="default",
            host=config.milvus.host,
            port=int(config.milvus.port)
        )

    def get_embedding(self, text):
        url = "http://host.docker.internal:3201/embed"
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": [text],
            "normalize": True,
            "prompt_name": None,
            "truncate": False,
            "truncation_direction": "Right"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()[0]
        except Exception as e:
            print(f"[Embedding Error] {e}")
            return None

    def upload_jsonl(self, file: UploadFile):
        session = self.Session()
        mariadb = self.config.mariadb
        collection_names = self.config.data.collection
        gen = SnowflakeGenerator(42)

        # Milvus 데이터를 임시로 저장할 버퍼
        milvus_buffers = {col: {"ids": [], "contents": [], "embeddings": []} for col in collection_names}

        try:
            reader = jsonlines.Reader(file.file)
            for obj in reader:
                snowflake_id = next(gen)
                obj["id"] = snowflake_id

                keys = obj.keys()
                columns_str = ", ".join(f"`{k}`" for k in keys)
                placeholders = ", ".join([f":{k}" for k in keys])
                sql = text(f"INSERT INTO {mariadb.table} ({columns_str}) VALUES ({placeholders})")
                session.execute(sql, obj)
                print(f"[DB] Inserted: {snowflake_id}")

                for col in collection_names:
                    content = obj.get(col)
                    if content:
                        embedding = self.get_embedding(content)
                        if embedding:
                            milvus_buffers[col]["ids"].append(snowflake_id)
                            milvus_buffers[col]["contents"].append(content)
                            milvus_buffers[col]["embeddings"].append(embedding)
                        else:
                            print(f"[Milvus] ❌ Embedding 실패: {col}")

            # 모든 collection에 대해 한번씩 insert + flush
            for col, data in milvus_buffers.items():
                if data["ids"]:  # 데이터가 존재할 때만 처리
                    collection = Collection(col)
                    collection.insert([data["ids"], data["contents"], data["embeddings"]])
                    collection.flush()
                    print(f"[Milvus] Flushed '{col}'에 {len(data['ids'])}개 삽입 완료")

            session.commit()
            return {"status": "success"}

        except Exception as e:
            session.rollback()
            return {"status": "error", "detail": str(e)}
        finally:
            session.close()