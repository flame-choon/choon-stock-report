import boto3
import logging
from datetime import datetime
from typing import Any


def get_batch_size(item_count: int) -> int:
    """데이터 수에 따라 배치 사이즈 결정"""
    if item_count <= 50:
        return 10
    elif item_count <= 200:
        return 25
    else:
        return 50


def split_into_batches(items: list, batch_size: int) -> list[list]:
    """아이템을 배치 사이즈에 맞게 분할"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def lambda_handler(event: dict, context: Any) -> dict:
    """
    DynamoDB에서 stock ticker 데이터를 조회하고 배치로 분할하여 반환

    Returns:
        dict: Step Functions에서 사용할 배치 데이터
            - batches: 분할된 ticker 데이터 배열
            - total_count: 전체 ticker 수
            - batch_size: 적용된 배치 사이즈
            - batch_count: 배치 개수
    """
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    table = dynamodb.Table('choon-prd-apne2-stock-tickers')

    # DynamoDB 전체 스캔 (페이지네이션 처리)
    items = []
    response = table.scan()
    items.extend(response.get('Items', []))

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    total_count = len(items)
    batch_size = get_batch_size(total_count)
    batches = split_into_batches(items, batch_size)

    # 작업 ID 생성 (추적용)
    job_id = f"stock-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    return {
        'job_id': job_id,
        'timestamp': datetime.now().isoformat(),
        'batches': batches,
        'total_count': total_count,
        'batch_size': batch_size,
        'batch_count': len(batches)
    }
