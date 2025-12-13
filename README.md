# Choon Stock Report

주식 티커(Ticker) 정보를 관리하고 분석 리포트를 생성하기 위한 AWS 서버리스 프로젝트입니다.

## 개요

이 프로젝트는 AWS Lambda와 DynamoDB를 활용하여 주식 티커 데이터를 관리하고, Step Functions를 통해 배치 처리하는 시스템입니다.

## 아키텍처

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  add-stock-tickers  │────▶│      DynamoDB       │◀────│  get-stock-tickers  │
│      (Lambda)       │     │ (stock-tickers DB)  │     │      (Lambda)       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                                                  │
                                                                  ▼
                                                        ┌─────────────────────┐
                                                        │   Step Functions    │
                                                        │   (배치 처리)        │
                                                        └─────────────────────┘
```

## 프로젝트 구조

```
.
├── Lambda/
│   ├── add-stock-tickers/      # 티커 추가 Lambda 함수
│   │   ├── lambda_function.py  # 메인 핸들러
│   │   ├── ticker-list.json    # 샘플 티커 목록
│   │   ├── requirements.txt    # Python 의존성
│   │   └── README.md           # 함수 문서
│   │
│   └── get-stock-tickers/      # 티커 조회 Lambda 함수
│       ├── lambda_function.py  # 메인 핸들러
│       ├── requirements.txt    # Python 의존성
│       └── README.md           # 함수 문서
│
├── .gitignore
├── README.md                   # 프로젝트 문서 (현재 파일)
└── CLAUDE.md                   # Claude Code 작업 가이드
```

## Lambda 함수

### 1. add-stock-tickers

DynamoDB에 주식 티커 정보를 저장하는 함수입니다.

- **용도**: 티커 데이터 초기 적재 및 관리
- **테이블**: `choon-prd-apne2-stock-tickers`
- **입력**: 티커 정보 배열 (ticker, name, exchange, sector, industry)

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

### 2. get-stock-tickers

DynamoDB에서 티커 데이터를 조회하고 배치로 분할하여 Step Functions에 전달하는 함수입니다.

- **용도**: Step Functions의 첫 번째 단계로 데이터 조회 및 배치 분할
- **배치 사이즈**: 데이터 수에 따라 동적 결정 (10/25/50)
- **출력**: job_id, batches, total_count, batch_size, batch_count

## 기술 스택

- **Runtime**: Python 3.12+
- **Cloud**: AWS (Lambda, DynamoDB, Step Functions)
- **CI/CD**: GitHub Actions
- **인증**: AWS OIDC

## AWS 리소스

| 리소스 | 이름 | 리전 |
|--------|------|------|
| DynamoDB Table | `choon-prd-apne2-stock-tickers` | ap-northeast-2 |
| Lambda | `choon-add-stock-tickers` | ap-northeast-2 |
| Lambda | `choon-prd-apne2-get-stock-tickers` | ap-northeast-2 |

## 배포

각 Lambda 함수는 GitHub Actions를 통해 자동 배포됩니다.

1. Repository Secrets에 `AWS_ROLE_ARN` 설정
2. `main` 브랜치에 push 시 자동 배포

자세한 배포 방법은 각 Lambda 함수의 README.md를 참조하세요.

## 로컬 개발

```bash
# 가상 환경 생성
python3.12 -m venv venv
source venv/bin/activate

# 의존성 설치 (각 Lambda 폴더에서)
cd Lambda/add-stock-tickers
pip install -r requirements.txt
```

## 라이선스

MIT
