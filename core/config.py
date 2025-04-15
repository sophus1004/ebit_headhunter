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
            { "name": "name", "type": "String", "length": 32 },
            { "name": "sex", "type": "String", "length": 32 },
            { "name": "age", "type": "Integer" },
            { "name": "nationality", "type": "String", "length": 32 },
            { "name": "city", "type": "String", "length": 32 },
            { "name": "education_degree", "type": "String", "length": 8 },
            { "name": "doctorate", "type": "String", "length": 32 },
            { "name": "doctorate_university", "type": "String", "length": 32 },
            { "name": "master", "type": "String", "length": 32 },
            { "name": "master_university", "type": "String", "length": 32 },
            { "name": "bachelor", "type": "String", "length": 32 },
            { "name": "bachelor_university", "type": "String", "length": 32 },
            { "name": "self_introduction", "type": "Text" },
            { "name": "work_experience", "type": "Text" }
        ]
        self.collection = [
            "self_introduction",
            "work_experience"
        ]

class AppConfig:
    def __init__(self):
        self.mariadb = MariaDBConfig()
        self.milvus = MilvusConfig()
        self.data = DataConfig()