import logging
import json
import typing
import os

from custom_encoder import EnhancedJSONEncoder
from service import url_service

ENV_NAME = os.environ.get('ENV_NAME')

logger = logging.getLogger(__name__)

match ENV_NAME:
    case 'Prod':
        logger.setLevel(logging.ERROR)
    case 'Dev':
        logger.setLevel(logging.DEBUG)
    case 'Test':
        logger.setLevel(logging.DEBUG)


def build_response(statusCode: int, body: typing.Union[None, dict] = None) -> dict:
    return {
        'statusCode': statusCode,
        'body': json.dumps(body, cls=EnhancedJSONEncoder)
    }


def redirect_to(api_key: str, id: str):
    try:
        obj = url_service.fetch(api_key, id)

        if not obj:
            return build_response(404, {'message': 'Link not found.'})

        return {
            'statusCode': 302,
            'headers': {
                'Location': obj.url
            }
        }
    except Exception:
        logger.exception(f'Cannot redirect to {id}:')


def get_urls(api_key: str):
    try:
        return build_response(200, url_service.fetch_all(api_key))
    except Exception:
        logger.exception(f'Cannot do GET on /urls')


def get_url(api_key: str, id: str):
    try:
        obj = url_service.fetch(api_key, id)

        if obj:
            return build_response(200, obj)
        else:
            return build_response(404, {'message': 'Link not found.'})
    except Exception:
        logger.exception(f'Cannot do GET on /url/{id}:')


def post_url(api_key: str, requestBody: dict):
    try:
        return build_response(
            200,
            url_service.create(api_key, json.loads(requestBody))
        )
    except ValueError as ve:
        return build_response(
            400,
            {'message': str(ve)}
        )
    except Exception:
        logger.exception('Cannot do POST on /url')


def lambda_handler(event, context):

    logger.debug('------------')
    logger.debug('Event info')

    logger.debug(event)

    logger.debug('------------')
    # HTTP Method of event.
    resource = event['resource']
    path = event['path']
    httpMethod = event['httpMethod']
    api_key = event['headers'].get('x-api-key', None)

    if not api_key:
        return build_response(
            403,
            {'message': 'x-api-key header value missing, CAUTION: x-api-key should be lowercase!'}
        )

    # URL route
    if resource == '/url':
        match httpMethod:
            case 'POST':
                return post_url(api_key, event['body'])
    elif resource == '/url/{LinkId}':
        match httpMethod:
            case 'DELETE':
                url_service.delete(api_key, path.split('/')[-1])
                return build_response(200, {'message': 'Link deleted'})
            case 'GET':
                return get_url(api_key, path.split('/')[-1])
    elif resource == '/u/{LinkId}':
        return redirect_to(api_key, path.split('/')[-1])
    elif resource == '/urls':
        match httpMethod:
            case 'GET':
                return get_urls(api_key)
