import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from typing import Any
from services.text_embedding import TextEmbeddings

logger = logging.getLogger("uvicorn.error")

class VectorSearch:
    def __init__(self, config, initialize_db):
        self.config = config
        self.text_embedding = TextEmbeddings()
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus
        self.embedding_config = config.embedding
        self.batch_size = self.embedding_config.batch_size
        self.data_config = config.data
        self.db = initialize_db
        self.engine = initialize_db.engine
        self.session = initialize_db.session
        self.connection = initialize_db.connection