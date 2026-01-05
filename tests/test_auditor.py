import pytest
from unittest.mock import MagicMock
from app.auditor import S3Auditor

def test_s3_auditor_compliance_logic():
    # Create the auditor
    auditor = S3Auditor()

    # Replace the real boto3 client with a MagicMock
    mock_response = {
        'Status': 'Suspended', # We simulate a BAD bucket
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }
    
    auditor.s3_client.get_bucket_versioning = MagicMock(return_value=mock_response)

    # Run the function with a fake bucket name
    result = auditor.check_bucket_versioning("test-bucket")

    # Verify the result is what we expect
    assert result["resource_id"] == "test-bucket"
    assert result["is_compliant"] is False
    assert result["aws_service"] == "s3"