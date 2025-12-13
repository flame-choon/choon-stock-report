# CLAUDE.md

이 파일은 Claude Code가 이 프로젝트에서 작업할 때 참고해야 할 가이드입니다.

## 프로젝트 개요

주식 티커 데이터를 AWS Lambda와 DynamoDB로 관리하는 서버리스 프로젝트입니다.

## 프로젝트 구조

```
Lambda/
├── add-stock-tickers/    # 티커 저장 함수
└── get-stock-tickers/    # 티커 조회 및 배치 분할 함수
```

## 핵심 파일

- `Lambda/add-stock-tickers/lambda_function.py`: DynamoDB에 티커 저장
- `Lambda/get-stock-tickers/lambda_function.py`: DynamoDB에서 티커 조회 및 배치 처리
- `Lambda/add-stock-tickers/ticker-list.json`: 샘플 티커 데이터

## 코딩 컨벤션

### Python

- Python 3.12+ 사용
- 타입 힌트 사용 (`typing` 모듈)
- 함수/클래스에 docstring 작성 (한국어)
- 로깅은 `logging` 모듈 사용
- AWS SDK는 `boto3` 사용

### 네이밍

- Lambda 함수명: `choon-{env}-{region}-{function-name}` 패턴
- DynamoDB 테이블: `choon-{env}-{region}-{table-name}` 패턴
- 변수/함수: snake_case
- 클래스: PascalCase

## AWS 설정

### 리전

- 기본 리전: `ap-northeast-2` (서울)

### DynamoDB

- 테이블: `choon-prd-apne2-stock-tickers`
- 파티션 키: `ticker` (String)
- 주요 속성: ticker, name, exchange, sector, industry, status, created_at, updated_at

### Lambda 설정

| 항목 | 값 |
|------|-----|
| Runtime | Python 3.12 |
| Timeout | 30초 |
| Memory | 256MB |

## 작업 시 주의사항

1. **AWS 리소스명 변경 금지**: 기존 리소스명(테이블명, Lambda명)은 변경하지 않기
2. **리전 확인**: 모든 AWS 작업은 `ap-northeast-2` 리전 기준
3. **의존성 관리**: 새 패키지 추가 시 `requirements.txt` 업데이트
4. **에러 처리**: 모든 Lambda 함수에서 적절한 에러 처리 및 로깅 구현
5. **테스트**: Lambda 함수 수정 시 로컬 테스트 후 배포

## 자주 사용하는 명령어

```bash
# 의존성 설치
pip install -r requirements.txt

# AWS CLI로 Lambda 함수 호출 테스트
aws lambda invoke --function-name choon-add-stock-tickers \
  --payload '{"tickers": [{"ticker": "TEST", "name": "Test Corp"}]}' \
  response.json

# DynamoDB 테이블 스캔
aws dynamodb scan --table-name choon-prd-apne2-stock-tickers
```

## 배포 프로세스

1. 코드 수정
2. 로컬 테스트
3. `main` 브랜치에 push
4. GitHub Actions 자동 배포

## 향후 확장 계획

- Step Functions 워크플로우 추가
- 주식 분석 리포트 생성 Lambda 추가
- API Gateway 연동
