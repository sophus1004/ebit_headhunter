# core/config.py
class MariaDBConfig:
    def __init__(self):
        self.host = "121.126.210.5"
        self.port = 3306
        self.user = "root"
        self.password = "testdb"
        self.database = "headhunter"
        self.table = "person_info"

        self.pool_size=5
        self.max_overflow=10
        self.pool_timeout=30
        self.pool_recycle=1800

class MilvusConfig:
    def __init__(self):
        self.host = "121.126.210.5"
        self.port = 19530
        self.api_port = 9091

class EmbeddingConfig:
    def __init__(self):
        self.host = "121.126.210.5"
        self.port = 3201
        self.batch_size = 16

class DataConfig:
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
    def __init__(self):
        self.mariadb = MariaDBConfig()
        self.milvus = MilvusConfig()
        self.embedding = EmbeddingConfig()
        self.data = DataConfig()