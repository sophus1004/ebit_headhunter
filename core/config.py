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
        self.port = "19530"

class DataConfig:
    def __init__(self):
        self.column = [
            { "name": "file_name", "type": "String", "length": 512 },
            { "name": "name", "type": "String", "length": 512 },
            { "name": "age", "type": "String", "length": 128 },
            { "name": "nationality", "type": "String", "length": 256 },
            { "name": "school_name", "type": "String", "length": 512 },
            { "name": "education_level", "type": "String", "length": 256 },
            { "name": "field_of_study", "type": "String", "length": 256 },
            { "name": "career_highlights", "type": "Text" },
            { "name": "preferred_position", "type": "String", "length": 512 },
            { "name": "experience", "type": "String", "length": 256 },
            { "name": "technical_skills", "type": "Text" },
            { "name": "language_proficiency", "type": "String", "length": 256 },
            { "name": "detailed_summary", "type": "Text" },
        ]
        
        self.collection = [
            "detailed_summary"
        ]


class AppConfig:
    def __init__(self):
        self.mariadb = MariaDBConfig()
        self.milvus = MilvusConfig()
        self.data = DataConfig()