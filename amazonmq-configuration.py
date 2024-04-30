import boto3
import json

# Create an Amazon MQ client
client = boto3.client("mq")

# Get a list of all the Amazon MQs
brokers = client.list_brokers()

# Iterate through the Amazon MQs
for broker in brokers["BrokerSummaries"]:
    # Get the Amazon MQ ID
    broker_id = broker["BrokerId"]

    # Describe the Amazon MQ broker to get its configurations
    broker_description = client.describe_broker(BrokerId=broker_id)
    configurations = broker_description["Configurations"]

    config_id = configurations["Current"]["Id"]

    tags = client.list_tags(ResourceArn=broker["BrokerArn"])
    response = client.describe_configuration(ConfigurationId=config_id)
    config_arn = response["Arn"]

    client.create_tags(
        ResourceArn=config_arn,
        Tags={key: value for key, value in tags["Tags"].items()},
    )
    print(f"Added tags to configuration {config_id}: {tags['Tags']}")
