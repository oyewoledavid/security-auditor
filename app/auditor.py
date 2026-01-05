import boto3
from botocore.exceptions import ClientError
from app.config import settings

class S3Auditor:
    def __init__(self):
        self.s3_client = boto3.client("s3", region_name=settings.AWS_REGION)

    def list_buckets(self) -> list[str]:
        """
        BLOCKING: Returns a list of bucket names.
        """
        try:
            response = self.s3_client.list_buckets()
            return [b["Name"] for b in response.get("Buckets", [])]
        except ClientError as e:
            print(f"Error listing buckets: {e}")
            return []

    def check_bucket_versioning(self, bucket_name: str) -> dict:
        """
        BLOCKING function. Checks if versioning is enabled.
        Returns a dict suitable for creating an AuditResult model.
        """
        try:
            response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            
            status = response.get("Status", "Disabled")
            is_compliant = (status == "Enabled")

            return {
                "aws_service": "s3",
                "resource_id": bucket_name,
                "check_name": "bucket_versioning_check",
                "is_compliant": is_compliant,
                "details": f"Versioning status is: {status}"
            }

        except ClientError as e:
            # If the bucket doesn't exist or we lack permissions
            return {
                "aws_service": "s3",
                "resource_id": bucket_name,
                "check_name": "bucket_versioning_check",
                "is_compliant": False,
                "details": f"Error auditing bucket: {str(e)}"
            }
        
class IAMAuditor:
    def __init__(self):
        self.iam_client = boto3.client("iam", region_name=settings.AWS_REGION)

    def list_users(self) -> list[str]:
        """
        BLOCKING: Returns a list of IAM usernames.
        """
        try:
            paginator = self.iam_client.get_paginator('list_users')
            users = []
            for page in paginator.paginate():
                for user in page['Users']:
                    users.append(user['UserName'])
            return users
        except ClientError as e:
            print(f"Error listing IAM users: {e}")
            return []

    def check_mfa_enabled(self, username: str) -> dict:
        """
        BLOCKING: Checks if a user has MFA devices enabled.
        """
        try:
            # list_mfa_devices returns a list of devices. If empty, MFA is off.
            response = self.iam_client.list_mfa_devices(UserName=username)
            mfa_devices = response.get('MFADevices', [])
            is_compliant = len(mfa_devices) > 0
            
            return {
                "aws_service": "iam",
                "resource_id": username,
                "check_name": "iam_user_mfa_check",
                "is_compliant": is_compliant,
                "details": f"User has {len(mfa_devices)} MFA device(s) enabled."
            }
        except ClientError as e:
            return {
                "aws_service": "iam",
                "resource_id": username,
                "check_name": "iam_user_mfa_check",
                "is_compliant": False,
                "details": f"Error auditing user: {str(e)}"
            }
        
class EC2Auditor:
    def __init__(self):
        self.ec2_client = boto3.client("ec2", region_name=settings.AWS_REGION)

    def list_security_groups(self) -> list[str]:
        """
        BLOCKING: Returns a list of Security Group IDs.
        """
        try:
            response = self.ec2_client.describe_security_groups()
            return [sg['GroupId'] for sg in response['SecurityGroups']]
        except ClientError as e:
            print(f"Error listing Security Groups: {e}")
            return []

    def check_ssh_open_to_world(self, group_id: str) -> dict:
        """
        BLOCKING: Checks if Port 22 is open to 0.0.0.0/0
        """
        try:
            # fetch the specific SG details to see permissions
            response = self.ec2_client.describe_security_groups(GroupIds=[group_id])
            sg = response['SecurityGroups'][0]
            permissions = sg.get('IpPermissions', [])
            
            is_open_to_world = False
            
            for perm in permissions:
                # Check if Port 22 (SSH) is included in this rule
                from_port = perm.get('FromPort')
                to_port = perm.get('ToPort')
                
                # If FromPort is None, it means ALL ports. 
                # Otherwise check if 22 is inside the range.
                if (from_port is None) or (from_port <= 22 and to_port >= 22):
                    # Now check if 0.0.0.0/0 is in the IP ranges
                    for ip_range in perm.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            is_open_to_world = True
                            break
            
            is_compliant = not is_open_to_world

            return {
                "aws_service": "ec2",
                "resource_id": group_id,
                "check_name": "sg_ssh_open_check",
                "is_compliant": is_compliant,
                "details": "Port 22 is open to the world" if is_open_to_world else "Port 22 is restricted"
            }

        except ClientError as e:
            return {
                "aws_service": "ec2",
                "resource_id": group_id,
                "check_name": "sg_ssh_open_check",
                "is_compliant": False,
                "details": f"Error auditing SG: {str(e)}"
            }