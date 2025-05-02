import requests
from datetime import datetime, timedelta
from pymilvus import utility
from sqlalchemy import create_engine, text

class GetInfo:
    def __init__(self, config):
        self.config = config
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus

    def check_mariadb_connection(self):
        try:
            url = (
                f"mysql+pymysql://{self.mariadb_config.user}:{self.mariadb_config.password}"
                f"@{self.mariadb_config.host}:{self.mariadb_config.port}/{self.mariadb_config.database}"
            )
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False

    def check_milvus_connection(self):
        try:
            response = requests.get(f"http://{self.milvus_config.host}:{self.milvus_config.api_port}/healthz")
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException:
            return False

    def get_server_info(self):
        return {
            "name": "headhunter-api",
            "version": "v1.0.0",
            "current_time": datetime.now().isoformat(),
            "mariadb_connected": self.check_mariadb_connection(),
            "milvus_connected": self.check_milvus_connection(),
            "db_table": {
                self.mariadb_config.table: [list(col.values())[0] for col in self.config.data.column]
            },
            "collections": self.config.data.collection
        }