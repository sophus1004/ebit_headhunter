# core/config.py

class MariaDBConfig:
    """MariaDB 관련 설정을 구성하는 클래스입니다.

    Attributes:
        host (str): MariaDB 호스트 주소.
        port (int): MariaDB 포트 번호.
        user (str): MariaDB 사용자 이름.
        password (str): MariaDB 비밀번호.
        database (str): 사용할 MariaDB 데이터베이스 이름.
        table (str): 사용할 기본 테이블 이름.
        pool_size (int): 커넥션 풀의 초기 사이즈.
        max_overflow (int): 커넥션 풀 초과 허용 수.
        pool_timeout (int): 커넥션 풀에서 커넥션 요청 대기 시간(초).
        pool_recycle (int): 커넥션 재활용 시간(초).
    """

    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 3306
        self.user = "root"
        self.password = "testdb"
        self.database = "headhunter"
        self.table = "person_info"

        self.pool_size = 5
        self.max_overflow = 10
        self.pool_timeout = 30
        self.pool_recycle = 1800


class MilvusConfig:
    """Milvus 관련 설정을 구성하는 클래스입니다.

    Attributes:
        host (str): Milvus 서버 호스트 주소.
        port (int): Milvus gRPC 포트 번호.
        api_port (int): Milvus HTTP API 포트 번호.
        database (str): 사용할 Milvus 데이터베이스 이름.
    """

    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 19530
        self.api_port = 9091
        self.database = "base_model"


class EmbeddingConfig:
    """임베딩 서버 설정을 구성하는 클래스입니다.

    Attributes:
        host (str): 임베딩 서버 호스트 주소.
        port (int): 임베딩 서버 포트 번호.
        batch_size (int): 임베딩 요청 시 배치 크기.
    """

    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 3201
        self.batch_size = 32


class DataConfig:
    """데이터 컬럼 및 컬렉션 설정을 구성하는 클래스입니다.

    Attributes:
        column (list): 데이터 컬럼 정의 목록. 각 항목은 딕셔너리 형태로 구성됨.
        collection (list): Milvus 컬렉션에 사용할 필드 목록.
    """

    def __init__(self):
        self.column = [
            { "FileName": "file_name", "type": "String", "length": 512 },
            { "Name": "name", "type": "String", "length": 512 },
            { "Age": "age", "type": "String", "length": 512 },
            { "Nationality": "nationality", "type": "String", "length": 512 },
            { "SchoolName": "school_name", "type": "String", "length": 512 },
            { "EducationLevel": "education_level", "type": "String", "length": 512 },
            { "FieldOfStudy": "field_of_study", "type": "String", "length": 512 },
            { "PreferredPosition": "preferred_position", "type": "String", "length": 512 },
            { "Experience": "experience", "type": "String", "length": 512 },
            { "TechnicalSkills": "technical_skills",  "type": "String", "length": 2048 },
            { "LanguageProficiency": "language_proficiency", "type": "String", "length": 512 },
            { "PreferredJobType": "preferred_job_type", "type": "String", "length": 512 },
            { "DetailedSummary": "detailed_summary", "type": "Text" },
        ]
        
        self.collection = [
            "detailed_summary"
        ]


class AppConfig:
    """전체 애플리케이션 설정을 묶는 구성 클래스입니다.

    MariaDB, Milvus, Embedding 서버, 데이터 스키마에 대한 설정 클래스를 포함합니다.

    Attributes:
        mariadb (MariaDBConfig): MariaDB 설정 인스턴스.
        milvus (MilvusConfig): Milvus 설정 인스턴스.
        embedding (EmbeddingConfig): 임베딩 서버 설정 인스턴스.
        data (DataConfig): 데이터 컬럼 및 컬렉션 설정 인스턴스.
    """

    def __init__(self):
        self.mariadb = MariaDBConfig()
        self.milvus = MilvusConfig()
        self.embedding = EmbeddingConfig()
        self.data = DataConfig()