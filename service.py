import os
import dataclasses
import typing
import uuid
import logging
import boto3

from models import URLModel

TBL_NAME = os.environ.get('DYNAMODB_TBL_NAME')

dynamodb = boto3.resource('dynamodb')
urlTable = dynamodb.Table(TBL_NAME)
logger = logging.getLogger(__name__)


class URLService:

    def fetch_all(self, api_key: str) -> typing.List[URLModel]:
        logger.debug("---------")
        logger.debug(f"Get all links for {api_key}")

        response = urlTable.query(
            KeyConditionExpression='apiKey = :apiKey',
            ExpressionAttributeValues={
                ':apiKey': api_key
            }
        )

        logger.debug('Getting all links done.')
        logger.debug("---------")
        return [URLModel(**item) for item in response['Items']]

    def fetch(self, api_key: str, shortLinkId: int) -> typing.Union[URLModel, None]:
        logger.debug("---------")
        logger.debug(f'Get link id: {shortLinkId}')

        response = urlTable.get_item(
            Key={
                'apiKey': api_key,
                'shortLinkId': shortLinkId
            },
        )

        logger.debug(response)
        logger.debug('Getting link done.')
        logger.debug("---------")

        if 'Item' in response:
            return URLModel(**response['Item'])
        else:
            return None

    def create(self, api_key: str, requestBody: dict) -> URLModel:
        logger.debug("---------")
        logger.debug('Post a link')

        # TODO: Find better method to validate on Lambda functions. Maybe use Marshmallow/Pydantic?
        if 'url' not in requestBody.keys():
            raise ValueError('Missing URL!')

        m = URLModel(api_key,  str(
            uuid.uuid1()).split('-')[0], requestBody['url'])

        response = urlTable.put_item(Item=dataclasses.asdict(m))

        logger.debug(response)
        logger.debug('Post link done.')
        logger.debug("---------")
        return m

    def delete(self, api_key: str, shortLinkId: str):
        logger.debug("---------")
        logger.debug("Delete link")
        response = urlTable.delete_item(
            Key={
                'apiKey': api_key,
                'shortLinkId': shortLinkId
            },
            ReturnValues='ALL_OLD'
        )
        logger.debug(response)
        logger.debug('Delete link done.')
        logger.debug("---------")


url_service = URLService()
