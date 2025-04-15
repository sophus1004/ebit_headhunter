from sqlalchemy import create_engine, Column, BigInteger, String, Integer, MetaData, Table, Text
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

def create_mariadb_table(config):
    mariadb_config = config.mariadb
    mariadb_columns = config.data.column

    url = (
        f"mysql+pymysql://{mariadb_config.user}:{mariadb_config.password}"
        f"@{mariadb_config.host}:{mariadb_config.port}/{mariadb_config.database}"
    )
    engine = create_engine(url)
    metadata = MetaData()
    columns = [Column("id", BigInteger, primary_key=True)]

    for col in mariadb_columns:
        name = col["name"]
        col_type = col["type"]
        if col_type == "String":
            length = col.get("length", 255)
            columns.append(Column(name, String(length)))
        elif col_type == "Integer":
            columns.append(Column(name, Integer))
        elif col_type == "BIGINT":
            columns.append(Column(name, BigInteger))
        elif col_type == "Text":
            columns.append(Column(name, Text))
        else:
            raise ValueError(f"❌ 지원되지 않는 컬럼 타입: {col_type}")

    table = Table(mariadb_config.table, metadata, *columns)
    metadata.create_all(engine)
    return f"✅ MariaDB 테이블 생성 완료: {mariadb_config.table}"

def create_milvus_collections(config):
    milvus_config = config.milvus
    milvus_collections = config.data.collection

    try:
        connections.connect(
            host=milvus_config.host,
            port=milvus_config.port
        )
    except Exception as e:
        return f"❌ Milvus 연결 실패: {e}"

    results = []
    for collection_name in milvus_collections:
        if utility.has_collection(collection_name):
            results.append(f"⚠️ 이미 존재하는 컬렉션: {collection_name}")
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
        results.append(f"✅ Milvus 컬렉션 및 인덱스 생성 완료: {collection_name}")

    return "\n".join(results)
