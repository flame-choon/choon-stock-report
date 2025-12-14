"""
Fan-out Tickers Lambda 함수

get-stock-tickers Lambda 함수에서 반환된 배치 데이터를 개별 ticker 메시지 배열로 변환합니다.
Step Functions의 Map 상태에서 SQS로 전달하기 위한 형식으로 출력합니다.
"""
import logging
from typing import Any

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: Any) -> dict:
    """
    get-stock-tickers에서 받은 배치 데이터를 개별 ticker 메시지 배열로 변환

    Args:
        event: get-stock-tickers Lambda의 반환값
            - job_id: 작업 ID
            - timestamp: 타임스탬프
            - batches: 분할된 ticker 데이터 배열
            - total_count: 전체 ticker 수

    Returns:
        dict: Step Functions Map 상태에서 SQS로 전달할 데이터
            - job_id: 작업 ID
            - timestamp: 타임스탬프
            - total_count: 전체 ticker 수
            - messages: SQS로 전송할 개별 메시지 배열
    """
    job_id = event.get('job_id', 'unknown')
    batches = event.get('batches', [])
    timestamp = event.get('timestamp', '')
    total_count = event.get('total_count', 0)

    # batches를 평탄화하여 개별 ticker 목록 생성
    tickers = [ticker for batch in batches for ticker in batch]

    logger.info(f"작업 시작 - job_id: {job_id}, ticker 수: {len(tickers)}")

    # Step Functions Map 상태에서 SQS로 전달할 메시지 배열 생성
    messages = []
    for index, ticker_data in enumerate(tickers):
        message = {
            'job_id': job_id,
            'timestamp': timestamp,
            'index': index,
            'total_count': total_count,
            'ticker': ticker_data
        }
        messages.append(message)

    logger.info(f"작업 완료 - job_id: {job_id}, 생성된 메시지 수: {len(messages)}")

    return {
        'job_id': job_id,
        'timestamp': timestamp,
        'total_count': total_count,
        'messages': messages
    }
