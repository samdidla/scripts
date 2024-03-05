import boto3
import csv
import concurrent.futures

client = boto3.client("ec2", region_name="us-west-2")


def open_file():
    with open("new.csv") as file_obj:
        reader_obj = csv.reader(file_obj)
        error_snap = []
        with open("error.csv", "w") as f:
            writer = csv.writer(f)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_snap = {
                    executor.submit(process_snap, row[0]): row[0] for row in reader_obj
                }
                for future in concurrent.futures.as_completed(future_to_snap):
                    snap, success = future.result()
                    if not success:
                        error_snap.append(snap)
            writer.writerow(error_snap)
            print(error_snap)


def process_snap(snap):
    try:

        snap_response = client.describe_snapshots(SnapshotIds=[snap])
        VolId = snap_response["Snapshots"][0]["VolumeId"]
        vol_response = client.describe_volumes(VolumeIds=[VolId])
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
                # create_tags(snap, tags["Key"], tags["Value"])
                print(tags["Key"])
                print(tags["Value"])
        return snap, True
    except Exception as e:
        return snap, False


def create_tags(snap, k, v):
    client.create_tags(Resources=[snap], Tags=[{"Key": k, "Value": v}])
    print("done")


open_file()
