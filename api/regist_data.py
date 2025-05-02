import json
import requests
import pandas as pd
import logging
from tqdm import tqdm
from snowflake import SnowflakeGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection, utility
from fastapi import UploadFile
from tqdm import trange
from core.messages import ServerMessages
from services.text_embedding import TextEmbeddings

logger = logging.getLogger("uvicorn.error")

class RegistData:
    def __init__(self, config, initialize_db):
        self.config = config
        self.text_embedding = TextEmbeddings()
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus
        self.embedding_config = config.embedding
        self.batch_size = self.embedding_config.batch_size
        self.data_config = config.data
        self.db = initialize_db
        self.engine = initialize_db.engine
        self.session = initialize_db.session
        self.connection = initialize_db.connection
        self.gen = SnowflakeGenerator(42)

    def convert_data(self, data):
        try:
            column_map = {list(d.keys())[0]: d[list(d.keys())[0]] for d in self.data_config.column}
            df = pd.DataFrame([
                {"FileName": k, **v["CategoricalValues"], "DetailedSummary": v["DetailedSummary"]}
                for k, v in data.items()
            ])
            df['id'] = [next(self.gen) for _ in range(len(df))]
            df.rename(columns=column_map, inplace=True)

            columns_to_convert = [col for col in df.columns if col != 'id']
            for col in columns_to_convert:
                df[col] = df[col].astype(str)

            logger.info(ServerMessages.REGISTDATA_CONVERT_COMPLETE)
            return df
        except Exception as e:
            logger.error(ServerMessages.REGISTDATA_CONVERT_ERROR + f"{e}")


    def data_insert(self, file: UploadFile):
        try:
            data = json.load(file.file)
            logger.info(ServerMessages.REGISTDATA_JSON_LOAD)
        except Exception as e:
            logger.error(ServerMessages.REGISTDATA_JSON_ERROR + f"{e}")

        df = self.convert_data(data)
        logger.info(ServerMessages.REGISTDATA_INSERT_DATA)
        logger.info(ServerMessages.REGISTDATA_INSERT_DATA_INFO.format(len=len(df), batch=self.batch_size))
        try:
            for start in trange(0, len(df), self.batch_size):
                end = start + self.batch_size
                batch = df.iloc[start:end]
                batch.to_sql(name=self.mariadb_config.table, con=self.engine, if_exists='append', index=False)

                for col in self.data_config.collection:
                    embedding_result = self.text_embedding.get_embeddings(batch[col].tolist())
                    collection = Collection(col)
                    collection.insert([batch['id'].tolist(), batch[col].tolist(), embedding_result])
                    collection.flush()
            logger.info(ServerMessages.REGISTDATA_INSERT_COMPLETE)
            return {"status": "success"}
        except Exception as e:
            logger.error(ServerMessages.REGISTDATA_INSERT_ERROR + f"{e}")
            return {"status": "error", "detail": str(e)}
        
