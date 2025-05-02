# core/config.py
class MariaDBConfig:
    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 3306
        self.user = "root"
        self.password = "testdb"
        self.database = "headhunter"
        self.table = "person_info"

class MilvusConfig:
    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 19530
        self.api_port = 9091

class EmbeddingConfig:
    def __init__(self):
        self.host = "host.docker.internal"
        self.port = 3201
        self.batch_size = 4

class DataConfig:
    def __init__(self):
        self.column = [
            { "FileName": "file_name", "type": "String", "length": 256 },
            { "Name": "name", "type": "String", "length": 64 },
            { "Age": "age", "type": "String", "length": 64 },
            { "Nationality": "nationality", "type": "String", "length": 64 },
            { "SchoolName": "school_name", "type": "String", "length": 64 },
            { "EducationLevel": "education_level", "type": "String", "length": 64 },
            { "FieldOfStudy": "field_of_study", "type": "String", "length": 256 },
            { "PreferredPosition": "preferred_position", "type": "String", "length": 256 },
            { "Experience": "experience", "type": "String", "length": 512 },
            { "TechnicalSkills": "technical_skills",  "type": "String", "length": 512 },
            { "LanguageProficiency": "language_proficiency", "type": "String", "length": 256 },
            { "PreferredJobType": "preferred_job_type", "type": "String", "length": 256 },
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