import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import boto3
from botocore.exceptions import ClientError

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'choon-prd-apne2-stock-tickers'


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러 함수
    DynamoDB에 주식 티커 정보를 저장합니다.

    Args:
        event: Lambda 이벤트 데이터
            예상 형식:
            {
                "tickers": [
                    {
                        "ticker": "AAPL",
                        "name": "Apple Inc.",
                        "exchange": "NASDAQ"
                    },
                    ...
                ]
            }
        context: Lambda 컨텍스트 객체

    Returns:
        응답 딕셔너리
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # 이벤트에서 티커 리스트 추출
        tickers = event.get('tickers', [])

        if not tickers:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'No tickers provided',
                    'error': 'tickers field is required and must be a non-empty list'
                })
            }

        # DynamoDB에 티커 저장
        result = save_tickers_to_dynamodb(tickers)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Tickers saved successfully',
                'saved_count': result['saved_count'],
                'failed_count': result['failed_count'],
                'details': result.get('errors', [])
            })
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        }


def save_tickers_to_dynamodb(tickers: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    주식 티커 리스트를 DynamoDB에 저장합니다.

    Args:
        tickers: 저장할 티커 정보 리스트

    Returns:
        저장 결과 딕셔너리
    """
    table = dynamodb.Table(TABLE_NAME)
    timestamp = datetime.utcnow().isoformat()

    saved_count = 0
    failed_count = 0
    errors = []

    for ticker_info in tickers:
        try:
            # 필수 필드 검증
            if 'ticker' not in ticker_info:
                failed_count += 1
                errors.append({
                    'ticker_info': ticker_info,
                    'error': 'Missing required field: ticker'
                })
                continue

            ticker = ticker_info['ticker']

            # DynamoDB 아이템 구성
            item = {
                'ticker': ticker,
                'name': ticker_info.get('name', ''),
                'exchange': ticker_info.get('exchange', ''),
                'created_at': timestamp,
                'updated_at': timestamp,
                'status': 'active'
            }

            # 추가 필드가 있다면 포함
            for key, value in ticker_info.items():
                if key not in ['ticker', 'name', 'exchange']:
                    item[key] = value

            # DynamoDB에 저장
            table.put_item(Item=item)
            saved_count += 1
            logger.info(f"Successfully saved ticker: {ticker}")

        except ClientError as e:
            failed_count += 1
            error_msg = f"DynamoDB error for {ticker_info.get('ticker', 'unknown')}: {e.response['Error']['Message']}"
            logger.error(error_msg)
            errors.append({
                'ticker_info': ticker_info,
                'error': error_msg
            })
        except Exception as e:
            failed_count += 1
            error_msg = f"Unexpected error for {ticker_info.get('ticker', 'unknown')}: {str(e)}"
            logger.error(error_msg)
            errors.append({
                'ticker_info': ticker_info,
                'error': error_msg
            })

    return {
        'saved_count': saved_count,
        'failed_count': failed_count,
        'errors': errors if errors else None
    }
