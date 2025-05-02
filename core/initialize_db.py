import logging
from sqlalchemy import create_engine, Column, BigInteger, String, MetaData, Table, Text
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from core.messages import ServerMessages

logger = logging.getLogger("uvicorn.error")

class InitializeDB:
    def __init__(self, config):
        self.config = config
        self.mariadb_config = config.mariadb
        self.data_config = self.config.data
        self.milvus_config = config.milvus

        try:
            self.engine = create_engine(
                f"mysql+pymysql://{self.mariadb_config.user}:{self.mariadb_config.password}"
                f"@{self.mariadb_config.host}:{self.mariadb_config.port}/{self.mariadb_config.database}"
            )
            self.connection = self.engine.connect()
            self.session = sessionmaker(bind=self.engine)
            logger.info(ServerMessages.DB_CONNECT)
        except Exception as e:
            logger.error(ServerMessages.DB_CONNECT_ERROR + f"{e}")

        try:
            connections.connect(
                alias="default",
                host=self.milvus_config.host,
                port=int(self.milvus_config.port)
            )
            logger.info(ServerMessages.MILVUS_CONNECT)
        except Exception as e:
            logger.error(ServerMessages.MILVUS_ERROR + f"{e}")

    def create_mariadb_table(self):
            metadata = MetaData()

            inspector = reflection.Inspector.from_engine(self.engine)
            if self.mariadb_config.table in inspector.get_table_names():
                logger.info(ServerMessages.DB_EXISTS + f"{self.mariadb_config.table}")
                return

            columns = [Column("id", BigInteger, primary_key=True, autoincrement=True)]

            for col in self.data_config.column:
                name = col.get("name")
                col_type = col["type"]

                if not name:
                    name = list(col.values())[0]
                    col["name"] = name

                if col_type == "String":
                    length = col.get("length", 255)
                    columns.append(Column(name, String(length)))
                elif col_type == "Text":
                    columns.append(Column(name, Text))
                else:
                    logger.error(ServerMessages.COLUMN_ERROR + f"{col_type}")

            table = Table(self.mariadb_config.table, metadata, *columns)
            metadata.create_all(self.engine)

            logger.info(ServerMessages.DB_COMPLETE + f"{self.mariadb_config.table}")

    def create_milvus_collections(self):
            milvus_collections = self.config.data.collection

            results = []

            for collection_name in milvus_collections:
                if utility.has_collection(collection_name):
                    results.append(ServerMessages.MILVUS_COL_INFO + f"{collection_name}")
                    continue

                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
                ]

                schema = CollectionSchema(fields=fields, description=f"{collection_name} collection")
                collection = Collection(name=collection_name, schema=schema, shards_num=2)

                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }

                collection.create_index(field_name="embedding", index_params=index_params)
                collection.load()

                results.append(ServerMessages.MILVUS_COMPLETE + f"{collection_name}")

            logger.info("\n".join(results))