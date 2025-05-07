class ServerMessages:
    INITIALIZE = "✅ DB 및 Milvus 초기화 시작"
    INITIALIZE_COMPLETE = "✅ DB 및 Milvus 초기화 완료"

    DB_CONNECT = "✅ MariaDB 연결"
    DB_CONNECT_ERROR = "❌ MariaDB 연결 실패: "
    DB_EXISTS = "⚠️ 이미 존재하는 MariaDB 테이블: "
    DB_COMPLETE = "✅ MariaDB 테이블 생성 완료: "

    MILVUS_CONNECT = "✅ Milvus 연결"
    MILVUS_ERROR = "❌ Milvus 연결 실패: "
    MILVUS_COL_INFO = "⚠️ 이미 존재하는 Milvus 컬렉션: "
    MILVUS_COMPLETE = "✅ Milvus 컬렉션 및 인덱스 생성 완료: "

    REGISTDATA_JSON_LOAD = "✅ Json 파일 로드"
    REGISTDATA_JSON_ERROR = "❌ Json 파일 로드 실패"
    REGISTDATA_CONVERT_COMPLETE = "✅ Json DB 변환"
    REGISTDATA_CONVERT_ERROR = "❌ Json DB 변환 실패"
    REGISTDATA_INSERT_DATA = "✅ 데이터 등록 시작"
    REGISTDATA_INSERT_COMPLETE = "✅ 데이터 등록 완료"
    REGISTDATA_INSERT_ERROR = "❌ 데이터 등록 실패"
    REGISTDATA_INSERT_DATA_INFO = "✅ 총 데이터수: {len} 배치사이즈: {batch}"

    EMBEDDING_ERROR = "❌ 데이터 임베딩 실패"

    MILVUS_SEARCH_ERROR = "❌ 밀버스 검색 실패: "
    MARIA_SEARCH_ERROR = "❌ MariaDB 검색 실패: "