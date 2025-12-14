"""
Fan-out Tickers Lambda 함수

get-stock-tickers Lambda 함수에서 반환된 ticker 데이터를 개별적으로 SQS로 전송합니다.
"""
import boto3
import json
import logging
from typing import Any

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SQS 설정
SQS_QUEUE_URL = "https://sqs.ap-northeast-2.amazonaws.com/879780444466/choon-prd-apne2-stock-analysis-jobs-queue"


def lambda_handler(event: dict, context: Any) -> dict:
    """
    get-stock-tickers에서 받은 ticker 데이터를 개별적으로 SQS 큐로 전송

    Args:
        event: get-stock-tickers Lambda의 반환값
            - job_id: 작업 ID
            - timestamp: 타임스탬프
            - batches: 분할된 ticker 데이터 배열
            - total_count: 전체 ticker 수

    Returns:
        dict: SQS 전송 결과
            - job_id: 작업 ID
            - sent_count: 전송된 메시지 수
            - failed_count: 실패한 메시지 수
            - status: 처리 상태
    """
    sqs = boto3.client('sqs', region_name='ap-northeast-2')

    job_id = event.get('job_id', 'unknown')
    batches = event.get('batches', [])
    timestamp = event.get('timestamp', '')
    total_count = event.get('total_count', 0)

    # batches를 평탄화하여 개별 ticker 목록 생성
    tickers = [ticker for batch in batches for ticker in batch]

    logger.info(f"작업 시작 - job_id: {job_id}, ticker 수: {len(tickers)}")

    sent_count = 0
    failed_count = 0
    failed_tickers = []

    for index, ticker_data in enumerate(tickers):
        try:
            ticker_symbol = ticker_data.get('ticker', 'unknown')

            message_body = {
                'job_id': job_id,
                'timestamp': timestamp,
                'index': index,
                'total_count': total_count,
                'ticker': ticker_data
            }

            response = sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message_body, ensure_ascii=False),
                MessageAttributes={
                    'job_id': {
                        'DataType': 'String',
                        'StringValue': job_id
                    },
                    'ticker': {
                        'DataType': 'String',
                        'StringValue': ticker_symbol
                    }
                }
            )

            logger.debug(f"ticker {ticker_symbol} 전송 완료 - MessageId: {response['MessageId']}")
            sent_count += 1

        except Exception as e:
            ticker_symbol = ticker_data.get('ticker', 'unknown')
            logger.error(f"ticker {ticker_symbol} 전송 실패: {str(e)}")
            failed_count += 1
            failed_tickers.append({
                'ticker': ticker_symbol,
                'error': str(e)
            })

    status = 'success' if failed_count == 0 else ('partial_failure' if sent_count > 0 else 'failure')

    result = {
        'job_id': job_id,
        'sent_count': sent_count,
        'failed_count': failed_count,
        'total_tickers': len(tickers),
        'status': status
    }

    if failed_tickers:
        result['failed_tickers'] = failed_tickers

    logger.info(f"작업 완료 - job_id: {job_id}, 전송: {sent_count}, 실패: {failed_count}")

    return result
