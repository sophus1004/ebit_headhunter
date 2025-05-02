import requests
from tqdm import tqdm
from snowflake import SnowflakeGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from fastapi import UploadFile
import re
from core.config import AppConfig

class MilvusRequest:
    def __init__(self):
        self.config = AppConfig()
        self.url = f"http://{self.config.milvus.host}:{self.config.milvus.port}/embed"