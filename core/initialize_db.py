import logging
from sqlalchemy import create_engine, text, Column, BigInteger, String, MetaData, Table, Text
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility, db
from core.messages import ServerMessages

logger = logging.getLogger("uvicorn.error")


class InitializeDB:
    """MariaDB 및 Milvus의 초기화를 수행하는 클래스입니다.

    DB 존재 여부 확인, 생성, 테이블 생성, Milvus 컬렉션 생성까지 포함된 기능을 제공합니다.

    Attributes:
        config (AppConfig): 전체 애플리케이션 설정 객체.
        mariadb_config (MariaDBConfig): MariaDB 관련 설정.
        data_config (DataConfig): 데이터 컬럼 및 컬렉션 설정.
        milvus_config (MilvusConfig): Milvus 관련 설정.
        engine (Engine): SQLAlchemy 엔진 객체.
        mariadb_connection (Connection): MariaDB 연결 객체.
        session (Session): SQLAlchemy 세션 팩토리.
    """

    def __init__(self, config):
        """MariaDB 및 Milvus 연결과 DB 존재 여부 확인/생성 초기화를 수행합니다.

        Args:
            config (AppConfig): AppConfig 객체로부터 각종 설정을 불러옵니다.
        """
        self.config = config
        self.mariadb_config = config.mariadb
        self.data_config = config.data
        self.milvus_config = config.milvus

        self.engine = None
        self.mariadb_connection = None
        self.session = None

        # MariaDB 존재 여부 확인 및 생성
        try:
            tmp_engine = create_engine(
                f"mysql+pymysql://{self.mariadb_config.user}:{self.mariadb_config.password}"
                f"@{self.mariadb_config.host}:{self.mariadb_config.port}",
                pool_pre_ping=True
            )
            with tmp_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"),
                    {"db_name": self.mariadb_config.database}
                )
                if result.fetchone():
                    logger.info(ServerMessages.DB_EXISTS.format(database=self.mariadb_config.database))
                else:
                    conn.execute(text(f"CREATE DATABASE {self.mariadb_config.database}"))
                    logger.info(ServerMessages.DB_CREATE_SUCCESS.format(database=self.mariadb_config.database))
        except Exception as e:
            logger.error(ServerMessages.DB_CREATE_ERROR.format(database=self.mariadb_config.database) + f"{e}")

        # MariaDB 연결 및 세션 생성
        try:
            self.engine = create_engine(
                f"mysql+pymysql://{self.mariadb_config.user}:{self.mariadb_config.password}"
                f"@{self.mariadb_config.host}:{self.mariadb_config.port}/{self.mariadb_config.database}",
                poolclass=QueuePool,
                pool_size=self.mariadb_config.pool_size,
                max_overflow=self.mariadb_config.max_overflow,
                pool_timeout=self.mariadb_config.pool_timeout,
                pool_recycle=self.mariadb_config.pool_recycle,
                pool_pre_ping=True
            )
            self.mariadb_connection = self.engine.connect()
            self.session = sessionmaker(bind=self.engine)
            logger.info(ServerMessages.DB_CONNECT_SUCCESS)
        except Exception as e:
            logger.error(ServerMessages.DB_CONNECT_ERROR + f"{e}")

        # Milvus 연결 및 DB 존재 여부 확인/생성
        try:
            connections.connect(
                alias="default",
                host=self.milvus_config.host,
                port=int(self.milvus_config.port)
            )
            if self.milvus_config.database not in db.list_database():
                try:
                    db.create_database(self.milvus_config.database)
                    logger.info(ServerMessages.MILVUS_CREATE_SUCCESS.format(database=self.milvus_config.database))
                    db.using_database(self.milvus_config.database)
                except Exception as e:
                    logger.error(ServerMessages.MILVUS_CREATE_ERROR.format(database=self.milvus_config.database) + f"{e}")
            else:
                logger.info(ServerMessages.MILVUS_EXISTS.format(database=self.milvus_config.database))
                db.using_database(self.milvus_config.database)
            logger.info(ServerMessages.MILVUS_CONNECT_SUCCESS)
        except Exception as e:
            logger.error(ServerMessages.MILVUS_CONNECT_ERROR + f"{e}")


    def create_mariadb_table(self):
        """MariaDB에 데이터 테이블을 생성합니다.

        설정된 테이블 이름이 이미 존재하면 생략하며,
        data_config에 정의된 스키마를 기반으로 컬럼을 생성합니다.
        """
        metadata = MetaData()
        inspector = reflection.Inspector.from_engine(self.engine)

        if self.mariadb_config.table in inspector.get_table_names():
            logger.info(ServerMessages.DB_TABLE_EXISTS + f"{self.mariadb_config.table}")
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
                logger.error(ServerMessages.DB_COLUMN_CREATE_ERROR + f"{col_type}")

        table = Table(self.mariadb_config.table, metadata, *columns)
        metadata.create_all(self.engine)
        logger.info(ServerMessages.DB_TABLE_CREATE_SUCCESS + f"{self.mariadb_config.table}")


    def create_milvus_collections(self):
        """Milvus에 필요한 컬렉션과 인덱스를 생성합니다.

        DataConfig에 정의된 collection 필드를 기준으로 컬렉션을 만들며,
        embedding 필드에 COSINE 기반 IVF_FLAT 인덱스를 생성하고 컬렉션을 메모리에 로드합니다.
        """
        results = []

        for collection_name in self.data_config.collection:
            if utility.has_collection(collection_name):
                results.append(ServerMessages.MILVUS_COLLECTION_EXISTS + f"{collection_name}")
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

            results.append(ServerMessages.MILVUS_COLLECTION_CREATE_SUCCESS + f"{collection_name}")

        logger.info("\n".join(results))