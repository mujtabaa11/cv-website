import boto3
import json
import traceback
from decimal import Decimal  # Import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cvWebsiteCounter')

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) # Convert to int (or float if needed)
        return json.JSONEncoder.default(self, obj)


def lambda_handler(event, context):
    try:
        response = table.update_item(
            Key={'GlobalCount': 'GlobalCount'},
            UpdateExpression='SET VisitCount = VisitCount + :incr',
            ExpressionAttributeValues={':incr': 1},
            ReturnValues='UPDATED_NEW',
            ConditionExpression='attribute_exists(VisitCount)'
        )

        new_count = response['Attributes']['VisitCount']

        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',  # Change to your frontend origin if needed
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
            'body': json.dumps({'count': new_count}, cls=DecimalEncoder) # Use custom encoder
        }

    except Exception as e:
        if "ConditionalCheckFailedException" in str(e):
            try:
                # Initialize VisitCount to 1
                response = table.update_item(
                    Key={'GlobalCount': 'GlobalCount'},
                    UpdateExpression='SET VisitCount = :initial',
                    ExpressionAttributeValues={':initial': 1},
                    ReturnValues='UPDATED_NEW'
                )
                new_count = response['Attributes']['VisitCount']
                return {
                    'statusCode': 200,
                    'body': json.dumps({'count': new_count}, cls=DecimalEncoder)  # Use custom encoder here as well
                }
            except Exception as e2:
                print(f"Error initializing VisitCount: {e2}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Error initializing VisitCount', 'details': str(e2)}, cls=DecimalEncoder)  # Use custom encoder
                }
        else:
            # Capture other errors
            error_message = str(e)
            error_traceback = traceback.format_exc()

            print(f"Error while updating count: {error_message}")
            print(f"Error traceback: {error_traceback}")

            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error updating the count', 'details': error_message, 'traceback': error_traceback}, cls=DecimalEncoder)  # Use custom encoder
            }
