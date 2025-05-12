import json
import pandas as pd
import logging
from snowflake import SnowflakeGenerator
from pymilvus import Collection
from fastapi import UploadFile
from tqdm import trange
from core.messages import ServerMessages
from services.text_embedding import TextEmbeddings

logger = logging.getLogger("uvicorn.error")


class InsertData:
    """JSON 데이터를 받아 MariaDB 및 Milvus에 저장 및 임베딩하는 클래스입니다.

    Attributes:
        text_embedding (TextEmbeddings): 텍스트 임베딩 처리 클래스.
        gen (SnowflakeGenerator): 고유 ID 생성을 위한 Snowflake ID 생성기.
        initialize_db (InitializeDB): DB 초기화 및 연결 클래스.
        config (AppConfig): 전체 애플리케이션 설정 객체.
        mariadb_config (MariaDBConfig): MariaDB 설정 객체.
        milvus_config (MilvusConfig): Milvus 설정 객체.
        embedding_config (EmbeddingConfig): 임베딩 서버 설정 객체.
        data_config (DataConfig): 데이터 컬럼 및 컬렉션 설정 객체.
    """

    def __init__(self, config, initialize_db):
        """RegistData 클래스 초기화

        Args:
            config (AppConfig): 앱 설정 객체.
            initialize_db (InitializeDB): DB 연결 및 초기화 객체.
        """
        self.text_embedding = TextEmbeddings()
        self.gen = SnowflakeGenerator(42)

        self.initialize_db = initialize_db
        self.config = config
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus
        self.embedding_config = config.embedding
        self.data_config = config.data

    def _convert_data(self, data):
        """업로드된 JSON 데이터를 Pandas DataFrame으로 변환합니다.

        Args:
            data (dict): JSON 파일 파싱 결과 딕셔너리.

        Returns:
            pd.DataFrame: 변환된 DataFrame 객체.
        """
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

            logger.info(ServerMessages.JSON_CONVERT_SUCCESS)
            return df
        except Exception as e:
            logger.error(ServerMessages.JSON_CONVERT_ERROR + f"{e}")

    def data_insert(self, file: UploadFile):
        """JSONL 파일을 MariaDB와 Milvus에 삽입합니다.

        Args:
            file (UploadFile): FastAPI 업로드 객체.

        Returns:
            dict: 성공 또는 실패 결과를 담은 딕셔너리.
        """
        try:
            data = json.load(file.file)
            logger.info(ServerMessages.JSON_LOAD_SUCCESS)
        except Exception as e:
            logger.error(ServerMessages.JSON_LOAD_ERROR + f"{e}")

        df = self._convert_data(data)
        logger.info(ServerMessages.DATA_INSERT_START)
        logger.info(ServerMessages.DATA_INSERT_INFO.format(len=len(df), batch=self.embedding_config.batch_size))

        try:
            with self.initialize_db.engine.begin() as conn:
                for start in trange(0, len(df), self.embedding_config.batch_size):
                    end = start + self.embedding_config.batch_size
                    batch = df.iloc[start:end]
                    batch.to_sql(name=self.mariadb_config.table, con=conn, if_exists='append', index=False)

                    for col in self.data_config.collection:
                        embedding_result = self.text_embedding.get_embeddings(batch[col].tolist())

                        collection = Collection(col)
                        collection.insert([batch['id'].tolist(), batch[col].tolist(), embedding_result])
                        collection.flush()

                logger.info(ServerMessages.DATA_INSERT_COMPLETE)
                return {"status": "success"}

        except Exception as e:
            logger.error(ServerMessages.DATA_INSERT_ERROR + f"{e}")
            return {"status": "error", "detail": str(e)}

    def dev_embedding_insert_only(self):
        """MariaDB 데이터를 Milvus에 임베딩하여 삽입하는 개발용 메서드입니다.

        Returns:
            dict: 삽입 성공 여부 결과.
        """
        try:
            with self.initialize_db.engine.begin() as conn:
                df = pd.read_sql_table(self.mariadb_config.table, con=conn)

            logger.info(ServerMessages.DEV_EMBEDDING_DB_LOAD_SUCCESS)
            logger.info(ServerMessages.DATA_INSERT_INFO.format(len=len(df), batch=self.embedding_config.batch_size))

            for start in trange(0, len(df), self.embedding_config.batch_size):
                end = start + self.embedding_config.batch_size
                batch = df.iloc[start:end]

                for col in self.data_config.collection:
                    texts = batch[col].astype(str).tolist()
                    embedding_result = self.text_embedding.get_embeddings(texts)

                    collection = Collection(col)
                    collection.insert([batch['id'].tolist(), texts, embedding_result])
                    collection.flush()

            logger.info(ServerMessages.DATA_INSERT_COMPLETE)
            return {"status": "success"}

        except Exception as e:
            logger.error(ServerMessages.DATA_INSERT_ERROR + f"{e}")
            return {"status": "error", "detail": str(e)}