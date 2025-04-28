import json
import requests
from tqdm import tqdm
from snowflake import SnowflakeGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from fastapi import UploadFile
import re

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
        """텍스트를 임베딩 벡터로 변환하는 함수"""
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
            result = response.json()
            if isinstance(result, dict) and "embeddings" in result:
                return result["embeddings"][0]
            elif isinstance(result, list):
                return result[0]
            else:
                print(f"[Embedding Error] Unexpected format: {result}")
                return None
        except Exception as e:
            print(f"[Embedding Error] {e}")
            return None

    def convert_camel_to_snake_case(self, name):
        """CamelCase 문자열을 snake_case로 변환하는 함수"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def upload_json(self, file: UploadFile):
        """JSON 파일을 읽어 DB와 Milvus에 저장하는 메인 함수"""
        session = self.Session()
        mariadb = self.config.mariadb
        collection_names = self.config.data.collection
        gen = SnowflakeGenerator(42)

        # Milvus 데이터를 임시로 저장할 버퍼
        milvus_buffers = {col: {"ids": [], "contents": [], "embeddings": []} for col in collection_names}

        try:
            # JSON 파일 전체 로드 (여기서는 dict 형식)
            data = json.load(file.file)

            for key, obj in tqdm(data.items(), desc="Processing applicants"):
                snowflake_id = next(gen)
                detailed_summary = obj.get("DetailedSummary", "")
                categorical_values = obj.get("CategoricalValues", {})

                # DB 삽입용 데이터 준비
                db_data = {"id": snowflake_id}
                db_data["file_name"] = key  # 업로드된 파일명 추가

                for col in self.config.data.column:
                    col_name = col["name"]
                    if col_name == "file_name":
                        continue  # 이미 넣었음
                    if col_name == "detailed_summary":
                        db_data[col_name] = detailed_summary
                    else:
                        # CategoricalValues 안에서 찾아서 넣음
                        camel_case_key = ''.join(word.capitalize() for word in col_name.split('_'))
                        value = categorical_values.get(camel_case_key, "")
                        if isinstance(value, list):
                            value = "; ".join(value)  # 리스트는 문자열로 변환
                        db_data[col_name] = value

                # DB Insert
                keys = db_data.keys()
                columns_str = ", ".join(f"`{k}`" for k in keys)
                placeholders = ", ".join([f":{k}" for k in keys])
                sql = text(f"INSERT INTO {mariadb.table} ({columns_str}) VALUES ({placeholders})")
                session.execute(sql, db_data)
                #print(f"[DB] Inserted: {snowflake_id}")

                # Milvus Insert 준비
                for col in collection_names:
                    content = db_data.get(col)
                    if content:
                        embedding = self.get_embedding(content)
                        if embedding:
                            milvus_buffers[col]["ids"].append(snowflake_id)
                            milvus_buffers[col]["contents"].append(content)
                            milvus_buffers[col]["embeddings"].append(embedding)
                        else:
                            print(f"[Milvus] ❌ Embedding 실패: {col}")

            # 모든 collection에 대해 insert + flush
            for col, data in milvus_buffers.items():
                if data["ids"]:
                    collection = Collection(col)
                    collection.insert([data["ids"], data["contents"], data["embeddings"]])
                    collection.flush()
                    #print(f"[Milvus] Flushed '{col}'에 {len(data['ids'])}개 삽입 완료")

            session.commit()
            return {"status": "success"}

        except Exception as e:
            session.rollback()
            return {"status": "error", "detail": str(e)}
        finally:
            session.close()