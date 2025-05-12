import requests
from datetime import datetime
from sqlalchemy import create_engine, text


class GetInfo:
    """서버 및 외부 서비스 상태 정보를 제공하는 클래스입니다.

    MariaDB, Milvus 연결 상태 확인 및 현재 서버 정보(시간, 버전, 테이블 스키마 등)를 반환합니다.

    Attributes:
        config (AppConfig): 전체 애플리케이션 설정 객체.
        mariadb_config (MariaDBConfig): MariaDB 설정 객체.
        milvus_config (MilvusConfig): Milvus 설정 객체.
    """

    def __init__(self, config):
        """GetInfo 인스턴스를 초기화합니다.

        Args:
            config (AppConfig): 설정 객체에서 MariaDB 및 Milvus 설정을 불러옵니다.
        """
        self.config = config
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus

    def _check_mariadb_connection(self) -> bool:
        """MariaDB 연결 여부를 확인합니다.

        Returns:
            bool: MariaDB가 정상적으로 연결되면 True, 그렇지 않으면 False.
        """
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

    def _check_milvus_connection(self) -> bool:
        """Milvus 연결 여부를 확인합니다.

        Returns:
            bool: Milvus의 `/healthz` 엔드포인트가 200 응답이면 True, 아니면 False.
        """
        try:
            response = requests.get(f"http://{self.milvus_config.host}:{self.milvus_config.api_port}/healthz")
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException:
            return False

    def get_server_info(self) -> dict:
        """현재 서버 상태 및 외부 서비스 연결 정보를 반환합니다.

        Returns:
            dict: 서버 이름, 버전, 현재 시간, DB 및 Milvus 연결 상태, 테이블 컬럼, Milvus 컬렉션 목록 등을 포함하는 정보.
        """
        return {
            "name": "headhunter-api",
            "version": "v1.0.0",
            "current_time": datetime.now().isoformat(),
            "mariadb_connected": self._check_mariadb_connection(),
            "milvus_connected": self._check_milvus_connection(),
            "db_table": {
                self.mariadb_config.table: [list(col.values())[0] for col in self.config.data.column]
            },
            "collections": self.config.data.collection
        }