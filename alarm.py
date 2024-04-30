import boto3
import re

cloudwatch = boto3.client("cloudwatch", region_name="us-west-2")

clients = ["asb", "wtfc", "snv", "zion", "zions"]


def add_tag_to_cloudwatch_alarm(alarm_name, key, value):
    try:
        cloudwatch.tag_resource(
            ResourceARN=f"arn:aws:cloudwatch:us-west-2:087633845042:alarm:{alarm_name}",
            Tags=[{"Key": key, "Value": value}],
        )
        print(f"Added tag {key}={value} to CloudWatch alarm {alarm_name}")
    except Exception as e:
        print(
            f"Error adding tag {key}={value} to CloudWatch alarm {alarm_name}: {str(e)}"
        )


def check_cloudwatch_alarms():
    alarm_names = [
        alarm["AlarmName"] for alarm in cloudwatch.describe_alarms()["MetricAlarms"]
    ]
    for alarm_name in alarm_names:
        for client in clients:
            if re.search(client, alarm_name, re.IGNORECASE):
                add_tag_to_cloudwatch_alarm(alarm_name, "client", client)
                break


check_cloudwatch_alarms()
