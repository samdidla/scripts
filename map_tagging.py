import boto3
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

tag_key = "map-migrated"
tag_value = "migJSS6YI14AN"


def tag_ec2_snapshots(region_name):
    try:
        ec2_client = boto3.client("ec2", region_name=region_name)
        next_token = None

        while True:
            if next_token:
                response = ec2_client.describe_snapshots(
                    OwnerIds=["self"], NextToken=next_token
                )
            else:
                response = ec2_client.describe_snapshots(OwnerIds=["self"])

            snapshots = response["Snapshots"]
            for snapshot in snapshots:
                snapshot_id = snapshot["SnapshotId"]
                existing_tags = snapshot.get("Tags", [])
                tag_present = any(tag["Key"] == tag_key for tag in existing_tags)

                if not tag_present:
                    ec2_client.create_tags(
                        Resources=[snapshot_id],
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"Snapshot {snapshot_id} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"Snapshot {snapshot_id} already has the tag {tag_key}."
                    )

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        logger.error(f"Error tagging EC2 snapshots in {region_name}: {e}")


def process_cloudwatch_alarms(region_name):
    try:
        cloudwatch_client = boto3.client("cloudwatch", region_name=region_name)
        next_token = None

        while True:
            if next_token:
                response = cloudwatch_client.describe_alarms(NextToken=next_token)
            else:
                response = cloudwatch_client.describe_alarms()

            alarms = response["MetricAlarms"]
            for alarm in alarms:
                alarm_name = alarm["AlarmName"]
                tags = cloudwatch_client.list_tags_for_resource(
                    ResourceARN=alarm["AlarmArn"]
                ).get("Tags", [])
                tag_present = any(
                    tag["Key"] == tag_key and tag["Value"] == tag_value for tag in tags
                )

                if not tag_present:
                    cloudwatch_client.tag_resource(
                        ResourceARN=alarm["AlarmArn"],
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"CloudWatch Alarm {alarm_name} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"CloudWatch Alarm {alarm_name} already has the tag {tag_key}."
                    )

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        logger.error(f"Error tagging CloudWatch Alarms in {region_name}: {e}")


def tag_ssm_parameters(region_name):
    try:
        ssm_client = boto3.client("ssm", region_name=region_name)
        next_token = None

        while True:
            if next_token:
                response = ssm_client.describe_parameters(NextToken=next_token)
            else:
                response = ssm_client.describe_parameters()

            parameters = response["Parameters"]
            for parameter in parameters:
                parameter_name = parameter["Name"]
                existing_tags = ssm_client.list_tags_for_resource(
                    ResourceType="Parameter", ResourceId=parameter_name
                ).get("TagList", [])
                tag_present = any(tag["Key"] == tag_key for tag in existing_tags)

                if not tag_present:
                    ssm_client.add_tags_to_resource(
                        ResourceId=parameter_name,
                        ResourceType="Parameter",
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"SSM parameter {parameter_name} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"SSM parameter {parameter_name} already has the tag {tag_key}."
                    )

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        logger.error(f"Error tagging SSM parameters in {region_name}: {e}")


def tag_ec2_network_interfaces(region_name):
    try:
        ec2_client = boto3.client("ec2", region_name=region_name)
        next_token = None

        while True:
            if next_token:
                response = ec2_client.describe_network_interfaces(NextToken=next_token)
            else:
                response = ec2_client.describe_network_interfaces()

            network_interfaces = response["NetworkInterfaces"]
            for interface in network_interfaces:
                interface_id = interface["NetworkInterfaceId"]
                existing_tags = interface.get("TagSet", [])
                tag_present = any(tag["Key"] == tag_key for tag in existing_tags)

                if not tag_present:
                    ec2_client.create_tags(
                        Resources=[interface_id],
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"EC2 network interface {interface_id} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"EC2 network interface {interface_id} already has the tag {tag_key}."
                    )

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        logger.error(f"Error tagging EC2 network interfaces in {region_name}: {e}")


def tag_rds_snapshots(region_name):
    try:
        rds_client = boto3.client("rds", region_name=region_name)
        next_token = None

        while True:
            if next_token:
                response = rds_client.describe_db_snapshots(Marker=next_token)
            else:
                response = rds_client.describe_db_snapshots()

            db_snapshots = response["DBSnapshots"]
            for snapshot in db_snapshots:
                snapshot_arn = snapshot["DBSnapshotArn"]
                existing_tags = rds_client.list_tags_for_resource(
                    ResourceName=snapshot_arn
                ).get("TagList", [])
                tag_present = any(tag["Key"] == tag_key for tag in existing_tags)

                if not tag_present:
                    rds_client.add_tags_to_resource(
                        ResourceName=snapshot_arn,
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"RDS DB snapshot {snapshot_arn} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"RDS DB snapshot {snapshot_arn} already has the tag {tag_key}."
                    )

            next_token = response.get("Marker")
            if not next_token:
                break

        next_token = None
        while True:
            if next_token:
                response = rds_client.describe_db_cluster_snapshots(Marker=next_token)
            else:
                response = rds_client.describe_db_cluster_snapshots()

            cluster_snapshots = response["DBClusterSnapshots"]
            for snapshot in cluster_snapshots:
                snapshot_arn = snapshot["DBClusterSnapshotArn"]
                existing_tags = rds_client.list_tags_for_resource(
                    ResourceName=snapshot_arn
                ).get("TagList", [])
                tag_present = any(tag["Key"] == tag_key for tag in existing_tags)

                if not tag_present:
                    rds_client.add_tags_to_resource(
                        ResourceName=snapshot_arn,
                        Tags=[{"Key": tag_key, "Value": tag_value}],
                    )
                    logger.info(
                        f"RDS cluster snapshot {snapshot_arn} tagged with {tag_key}={tag_value}."
                    )
                else:
                    logger.info(
                        f"RDS cluster snapshot {snapshot_arn} already has the tag {tag_key}."
                    )

            next_token = response.get("Marker")
            if not next_token:
                break

    except Exception as e:
        logger.error(f"Error tagging RDS snapshots in {region_name}: {e}")


def tag_resources_in_region(region_name):
    tag_ec2_snapshots(region_name)
    process_cloudwatch_alarms(region_name)
    tag_ssm_parameters(region_name)
    tag_ec2_network_interfaces(region_name)
    tag_rds_snapshots(region_name)


def lambda_handler(event, context):
    regions = ["us-west-2", "us-east-2", "us-east-1"]

    with ThreadPoolExecutor(max_workers=len(regions)) as executor:
        futures = [
            executor.submit(tag_resources_in_region, region) for region in regions
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Exception occurred: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps(
            "EC2 snapshots, CloudWatch alarms, SSM parameters, EC2 network interfaces, and RDS snapshots tagged successfully."
        ),
    }
