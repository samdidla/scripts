import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-west-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_vol = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_vol = {
                    executor.submit(process_vol, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_vol):
                    vol, success = future.result()
                    if not success:
                        if success is None:
                            error_vol.append([vol])
            writer.writerows(error_vol)
            print("Error volumes written to error.csv")


def process_vol(vol):
    try:
        vol_response = client.describe_volumes(VolumeIds=[vol])
        attachments = vol_response["Volumes"][0].get("Attachments", [])
        if not attachments:
            print(f"Volume {vol} is not attached to any EC2 instance")
            create_tags(vol, "d3orphaned", "03-15-2024")
            return vol, False

        InstanceID = attachments[0]["InstanceId"]
        inst_response = client.describe_instances(InstanceIds=[InstanceID])
        vpcID = inst_response["Reservations"][0]["Instances"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])
        for tags in vpc_response["Vpcs"][0]["Tags"]:
            if tags["Key"] in ["client", "customer"]:
                if tags["Key"] == "d3orphaned":
                    print(
                        f"Skipping volume {vol} as it is already tagged as d3orphaned"
                    )
                    return vol, None
                create_tags(vol, tags["Key"], tags["Value"])
                print(f"Tagged volume {vol} with {tags['Key']}={tags['Value']}")
        return vol, True
    except Exception as e:
        print(f"Error processing volume {vol}: {str(e)}")
        return vol, False


def create_tags(vol, k, v):
    try:
        client.create_tags(Resources=[vol], Tags=[{"Key": k, "Value": v}])
        print(f"Created tag {k}={v} for volume {vol}")
    except Exception as e:
        print(f"Error tagging volume {vol}: {str(e)}")


open_file()
