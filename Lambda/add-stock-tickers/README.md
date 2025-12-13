# Add Stock Tickers Lambda Function

실제 Ticker report 프로세스에서는 사용 되지 않으며 Ticker report 프로세스에서 필요한 
티커 정보를 DynamoDB에 저장하기 위한 목적의 AWS Lambda 함수 입니다.

## 프로젝트 구조

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions 배포 워크플로우
├── lambda_function.py           # Lambda 핸들러 함수
├── requirements.txt             # Python 의존성
├── ticker-list.json             # 조회할 티커 목록 정의
└── README.md                    # 프로젝트 문서
```

## 기능

- 주식 티커 정보를 DynamoDB 테이블(`choon-prd-apne2-stock-tickers`)에 저장
- 배치 처리 지원 (여러 티커를 한 번에 저장)
- 오류 처리 및 로깅
- GitHub Actions를 통한 자동 배포

## 요구사항

- Python 3.12
- AWS CLI (설정 및 로컬 배포용)
- GitHub Actions (자동 배포용)

## 로컬 개발 환경 설정

1. 가상 환경 생성 및 활성화:
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

## Lambda 이벤트 형식

### 입력 형식

```json
{
  "tickers": [
{
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "sector": "Technology",
      "industry": "Customer Electronics"
    },
    {
      "ticker": "GOOG",
      "name": "Alphabet Inc.",
      "exchange": "NASDAQ",
      "sector": "Communication Services",
      "industry": "Internet Content & Information"
    }
  ]
}
```

### 응답 형식

성공 시:
```json
{
  "statusCode": 200,
  "body": {
    "message": "Tickers saved successfully",
    "saved_count": 2,
    "failed_count": 0,
    "details": []
  }
}
```

실패 시:
```json
{
  "statusCode": 400,
  "body": {
    "message": "No tickers provided",
    "error": "tickers field is required and must be a non-empty list"
  }
}
```

## DynamoDB 테이블 스키마

- **테이블명**: `choon-prd-apne2-stock-tickers`
- **파티션 키**: `ticker` (String)
- **속성**:
  - `ticker`: 주식 티커 심볼 (필수)
  - `name`: 회사명
  - `exchange`: 거래소명
  - `sector`: 티커가 속한 섹터
  - `industry`: 티커가 속한 섹터 내 세부 그룹
  - `created_at`: 생성 시각 (ISO 8601 형식)
  - `updated_at`: 업데이트 시각 (ISO 8601 형식)
  - `status`: 상태 (기본값: "active")

## 초기 설정

### 1. DynamoDB 테이블 생성

```bash
./scripts/create-dynamodb-table.sh
```

이 스크립트는 `choon-prd-apne2-stock-tickers` 테이블을 생성합니다.

### 2. IAM Role 설정

```bash
./scripts/setup-iam.sh
```

이 스크립트는 Lambda 실행에 필요한 IAM Role과 정책을 생성합니다.

## 배포

### GitHub Actions를 통한 자동 배포 (권장)

1. GitHub Repository Secrets 설정:
   - `AWS_ROLE_ARN`: GitHub Actions에서 사용할 AWS IAM Role ARN
     - OIDC Provider 설정 필요
     - Role에 Lambda 업데이트 권한 필요

2. `main` 브랜치에 푸시하면 자동 배포:
```bash
git add .
git commit -m "Deploy lambda function"
git push origin main
```

3. 수동 배포 트리거:
   - GitHub Repository의 Actions 탭에서 "Deploy Lambda Function" 워크플로우를 수동으로 실행

#### GitHub Actions OIDC 설정

GitHub Actions에서 AWS 인증을 위한 OIDC Provider 설정이 필요합니다:

1. AWS IAM에서 OIDC Provider 추가:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`

2. IAM Role 생성 및 신뢰 정책 설정:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::{ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:{GITHUB_ORG}/{REPO_NAME}:*"
        }
      }
    }
  ]
}
```

3. Role에 Lambda 업데이트 권한 추가:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:PublishVersion",
        "lambda:GetFunction"
      ],
      "Resource": "arn:aws:lambda:ap-northeast-2:{ACCOUNT_ID}:function:choon-add-stock-tickers"
    }
  ]
}
```

## 테스트

### AWS Console에서 테스트

Lambda 콘솔에서 다음 테스트 이벤트를 사용:

```json
{
  "tickers": [
{
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "sector": "Technology",
      "industry": "Customer Electronics"
    }
  ]
}
```

## IAM 권한

Lambda 함수는 다음 권한이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:ap-northeast-2:*:table/choon-prd-apne2-stock-tickers"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## 환경 변수

- `DYNAMODB_TABLE_NAME`: DynamoDB 테이블명 (기본값: `choon-prd-apne2-stock-tickers`)

## 로깅

Lambda 함수는 CloudWatch Logs에 다음 정보를 기록합니다:
- 수신된 이벤트
- 각 티커 저장 성공/실패
- 오류 정보

## 문제 해결

### DynamoDB 접근 오류
- IAM 역할에 DynamoDB 접근 권한이 있는지 확인
- 테이블명이 정확한지 확인

### Timeout 오류
- Lambda 함수의 타임아웃 설정을 늘려야 할 수 있습니다 (현재: 30초)

## 라이선스

MIT
