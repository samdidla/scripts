import boto3
import csv
import concurrent.futures
import botocore.exceptions

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
                        if success is not None:  # Check if it's not None
                            error_snap.append(snap)
            writer.writerow(error_snap)
            print("Error snapshots written to error.csv")


def process_snap(snap):
    try:
        snap_response = client.describe_snapshots(SnapshotIds=[snap])
        snapshots = snap_response["Snapshots"]
        if not snapshots:
            print(f"Snapshot {snap} not found.")
            create_tags(snap, "d3orphaned", "03-15-2024")
            return snap, None  # Return None to indicate skipping

        for snapshot in snapshots:
            volumes = [snapshot.get("VolumeId")]
            if not volumes[0]:  # Ensure volumes is not empty
                print(f"Snapshot {snap} is not attached to any volume")
                create_tags(snap, "d3orphaned", "03-15-2024")
                return snap, None  # Return None to indicate skipping
            try:
                vol_response = client.describe_volumes(VolumeIds=volumes)
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "InvalidVolume.NotFound":
                    print(f"Volume not found for snapshot {snap}")
                    create_tags(snap, "d3orphaned", "03-15-2024")
                    return snap, None  # Return None to indicate skipping
            # If volume exists, proceed with processing
            volume = vol_response["Volumes"][0]
            InstanceID = volume["Attachments"][0]["InstanceId"]
            inst_response = client.describe_instances(InstanceIds=[InstanceID])
            vpcID = inst_response["Reservations"][0]["Instances"][0]["VpcId"]
            vpc_response = client.describe_vpcs(VpcIds=[vpcID])
            for tags in vpc_response["Vpcs"][0]["Tags"]:
                if tags["Key"] in ["client", "customer"]:
                    print(tags["Key"])
                    print(tags["Value"])
            return snap, True

    except Exception as e:
        print(f"Error processing snapshot {snap}: {str(e)}")
        return snap, False


def create_tags(snap, k, v):
    try:
        client.create_tags(Resources=[snap], Tags=[{"Key": k, "Value": v}])
        print(f"Added tag {k}={v} to snapshot {snap}")
    except Exception as e:
        print(f"Error adding tag to snapshot {snap}: {str(e)}")


open_file()
