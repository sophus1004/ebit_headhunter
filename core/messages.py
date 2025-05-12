class ServerMessages:
    """서버 작업 및 상태 메시지를 정의하는 상수 클래스입니다.

    이 클래스는 MariaDB, Milvus, JSON 데이터 로딩, 데이터 삽입, 임베딩 등과 관련된
    다양한 작업의 상태 메시지를 상수로 정의하여, 로그 출력 및 사용자 응답 메시지로 사용됩니다.
    
    메시지 변수명은 도메인_동작_결과 형식을 따릅니다.
    """

    # 공통 초기화 메시지
    INIT_START = "✅ DB 및 Milvus 초기화 시작"
    INIT_COMPLETE = "✅ DB 및 Milvus 초기화 완료"

    # MariaDB 관련 메시지
    DB_CONNECT_SUCCESS = "✅ MariaDB 연결"
    DB_CONNECT_ERROR = "❌ MariaDB 연결 실패"
    DB_EXISTS = "⚠️ 이미 존재하는 MariaDB Database: {database}"
    DB_CREATE_SUCCESS = "✅ MariaDB 데이터베이스 '{database}' 생성"
    DB_CREATE_ERROR = "❌ MariaDB 데이터베이스 '{database}' 생성 실패"
    DB_TABLE_EXISTS = "⚠️ 이미 존재하는 MariaDB 테이블: "
    DB_TABLE_CREATE_SUCCESS = "✅ MariaDB 테이블 생성 완료: "
    DB_COLUMN_CREATE_ERROR = "❌ 컬럼 생성 실패"

    # Milvus 관련 메시지
    MILVUS_CONNECT_SUCCESS = "✅ Milvus 연결"
    MILVUS_CONNECT_ERROR = "❌ Milvus 연결 실패"
    MILVUS_EXISTS = "⚠️ 이미 존재하는 Milvus Database: {database}"
    MILVUS_CREATE_SUCCESS = "✅ Milvus 데이터베이스 '{database}' 생성"
    MILVUS_CREATE_ERROR = "❌ Milvus 데이터베이스 '{database}' 생성 실패"
    MILVUS_COLLECTION_EXISTS = "⚠️ 이미 존재하는 Milvus 컬렉션: "
    MILVUS_COLLECTION_CREATE_SUCCESS = "✅ Milvus 컬렉션 및 인덱스 생성 완료: "

    # JSON 파일 처리 메시지
    JSON_LOAD_SUCCESS = "✅ Json 파일 로드"
    JSON_LOAD_ERROR = "❌ Json 파일 로드 실패"
    JSON_CONVERT_SUCCESS = "✅ Json DB 변환"
    JSON_CONVERT_ERROR = "❌ Json DB 변환 실패"

    # 데이터 삽입 메시지
    DATA_INSERT_START = "✅ 데이터 등록 시작"
    DATA_INSERT_COMPLETE = "✅ 데이터 등록 완료"
    DATA_INSERT_ERROR = "❌ 데이터 등록 실패"
    DATA_INSERT_INFO = "✅ 총 데이터수: {len} 배치사이즈: {batch}"

    # 개발용 임베딩 처리 메시지
    DEV_EMBEDDING_DB_LOAD_SUCCESS = "✅ MariaDB 데이터 로드"
    DEV_EMBEDDING_MILVUS_INSERT_SUCCESS = "✅ Milvus 데이터 등록"
    DEV_EMBEDDING_MILVUS_INSERT_ERROR = "❌ Milvus 데이터 등록 실패"

    # 임베딩 오류 메시지
    EMBEDDING_ERROR = "❌ 데이터 임베딩 실패"

    # 검색 오류 메시지
    MILVUS_SEARCH_ERROR = "❌ 밀버스 검색 실패"
    MARIA_SEARCH_ERROR = "❌ MariaDB 검색 실패"