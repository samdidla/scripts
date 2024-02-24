import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-east-2")


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
                        error_vol.append(vol)
            writer.writerow(error_vol)
            print(error_vol)


def process_vol(vol):
    try:

        vol_response = client.describe_volumes(VolumeIds=[vol])
        InstanceID = vol_response["Volumes"][0]["Attachments"][0]["InstanceId"]
        inst_response = client.describe_instances(
            InstanceIds=[
                InstanceID,
            ]
        )
        vpcID = inst_response["Reservations"][0]["Instances"][0]["VpcId"]
        vpc_response = client.describe_vpcs(VpcIds=[vpcID])
        for tags in vpc_response["Vpcs"][0]["Tags"]:
            if tags["Key"] in ["client", "customer"]:
                create_tags(vol, tags["Key"], tags["Value"])
                print(tags["Key"])
                print(tags["Value"])
        return vol, True
    except Exception as e:
        return vol, False


def create_tags(vol, k, v):
    client.create_tags(Resources=[vol], Tags=[{"Key": k, "Value": v}])
    print("done")


open_file()
