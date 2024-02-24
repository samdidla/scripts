import argparse
import boto3 as boto3


def copy_item(
    source_account_profile, target_account_profile, source_table_name, target_table_name
):
    source_account_session = boto3.Session(profile_name=source_account_profile)
    source_account_dynamodb = source_account_session.client("dynamodb")

    target_account_session = boto3.Session(profile_name=target_account_profile)
    target_account_dynamodb = target_account_session.client("dynamodb")

    dynamo_paginator = source_account_dynamodb.get_paginator("scan")
    dynamo_response = dynamo_paginator.paginate(
        TableName=source_table_name,
        Select="ALL_ATTRIBUTES",
        ReturnConsumedCapacity="NONE",
        ConsistentRead=True,
    )

    for page in dynamo_response:
        for item in page["Items"]:
            target_account_dynamodb.put_item(TableName=target_table_name, Item=item)


parser = argparse.ArgumentParser()

parser.add_argument("source_account_profile", help="Source Account Profile")
parser.add_argument("target_account_profile", help="Target Account Profile")
parser.add_argument("source_table_name", help="Source Table Name")
parser.add_argument("target_table_name", help="Target Table Name")

args = vars(parser.parse_args())

copy_item(
    args["source_account_profile"],
    args["target_account_profile"],
    args["source_table_name"],
    args["target_table_name"],
)
