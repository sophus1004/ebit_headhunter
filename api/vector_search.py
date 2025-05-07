import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from typing import Any
from services.text_embedding import TextEmbeddings
from core.messages import ServerMessages

logger = logging.getLogger("uvicorn.error")

class VectorSearch:
    def __init__(self, config, initialize_db):
        self.text_embedding = TextEmbeddings()

        self.initialize_db = initialize_db

        self.config = config
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus
        self.embedding_config = config.embedding
        self.data_config = config.data

    def _milvus_search(self, col, metric_type, nprobe, embedded_data, top_k, output_fields):
        try:
            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": nprobe}
            }

            collection = Collection(col)
            results = collection.search(
                data=embedded_data,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=output_fields
            )

            return results

        except Exception as e:
            logger.error(ServerMessages.MILVUS_SEARCH_ERROR + f"{e}")

    def _mariadb_search(self, id_list):
        try:
            with self.initialize_db.engine.connect() as conn:
                placeholders = ", ".join([":id{}".format(i) for i in range(len(id_list))])
                sql = text(f"SELECT * FROM {self.mariadb_config.table} WHERE id IN ({placeholders})")
                params = {f"id{i}": id_val for i, id_val in enumerate(id_list)}

                result = conn.execute(sql, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(ServerMessages.MARIA_SEARCH_ERROR + f"{e}")

    def only_vector(self, collection_names, query_text, top_k):
        col = collection_names
        metric_type = "COSINE"
        nprobe = 10
        embedded_data = self.text_embedding.get_embeddings([query_text])
        top_k = top_k
        output_fields = ["id"]

        milvus_result = self._milvus_search(col, metric_type, nprobe, embedded_data, top_k, output_fields)
        id_list = [hit.id for hit in milvus_result[0]]
        mariadb_result = self._mariadb_search(id_list)

        return mariadb_result