# choon-get-stock-tickers

AWS Step Functions의 첫 번째 단계를 담당하는 Lambda 함수입니다. DynamoDB에서 stock ticker 데이터를 조회하고 배치로 분할하여 다음 Lambda 함수에 전달합니다.

## 기능

- DynamoDB 테이블에서 전체 ticker 데이터 조회
- 데이터 수에 따른 동적 배치 사이즈 결정
- 배치 단위로 데이터 분할하여 Step Functions에 반환

## 배치 사이즈 규칙

| 데이터 수 | 배치 사이즈 |
|-----------|-------------|
| 50개 이하 | 10 |
| 200개 이하 | 25 |
| 200개 초과 | 50 |

## 반환값

```json
{
  "job_id": "stock-analysis-20241201-143052",
  "timestamp": "2024-12-01T14:30:52.123456",
  "batches": [[{ticker1}, {ticker2}, ...], ...],
  "total_count": 150,
  "batch_size": 25,
  "batch_count": 6
}
```

## 프로젝트 구조

```
.
├── lambda_function.py      # Lambda 핸들러
├── requirements.txt        # Python 의존성
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml      # GitHub Actions 배포 워크플로우
```

## 배포

### 사전 요구사항

1. AWS Lambda 함수 `choon-prd-apne2-get-stock-tickers` 생성
2. Lambda 실행 역할에 DynamoDB 읽기 권한 부여
3. GitHub Secrets 설정:
   - `AWS_ROLE_ARN`: OIDC 인증용 IAM Role ARN

### 자동 배포

`main` 브랜치에 push하면 GitHub Actions를 통해 자동 배포됩니다.

### Lambda 설정

| 항목 | 값 |
|------|-----|
| Runtime | Python 3.14 |
| Timeout | 30초 |
| Memory | 256MB |
| Region | ap-northeast-2 |


