from datetime import datetime, timedelta
from pymilvus import utility
from sqlalchemy import create_engine, text

# 서버 시작 시간 기록
start_time = datetime.now()

def get_server_info(config):
    uptime = datetime.now() - start_time

    # MariaDB 연결 확인
    def check_mariadb_connection():
        try:
            url = (
                f"mysql+pymysql://{config.mariadb.user}:{config.mariadb.password}"
                f"@{config.mariadb.host}:{config.mariadb.port}/{config.mariadb.database}"
            )
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False

    # Milvus 연결 확인
    def check_milvus_connection():
        try:
            return utility.has_collection(config.data.collection[0])
        except:
            return False

    return {
        "name": "headhunter-api",
        "version": "v1.0.0",
        "uptime": str(timedelta(seconds=int(uptime.total_seconds()))),
        "current_time": datetime.now().isoformat(),
        "mariadb_connected": check_mariadb_connection(),
        "db_table": config.mariadb.table,
        "columns": [col["name"] for col in config.data.column],
        "milvus_connected": check_milvus_connection(),
        "collections": config.data.collection
    }