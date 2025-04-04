from unittest.mock import patch, MagicMock
from services.s3 import upload_to_s3, delete_from_s3


@patch("services.s3.get_s3_client")
def test_upload_to_s3_success(mock_get_s3_client):
    mock_s3 = MagicMock()
    mock_get_s3_client.return_value = mock_s3

    result = upload_to_s3(
        file_bytes=b"test content",
        key="test-file.pdf",
        content_type="application/pdf",
        tags="test=1"
    )

    mock_s3.put_object.assert_called_once()
    assert result is True


@patch("services.s3.get_s3_client")
def test_upload_to_s3_client_error(mock_get_s3_client):
    from botocore.exceptions import ClientError

    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Denied!"}},
        operation_name="PutObject"
    )
    mock_get_s3_client.return_value = mock_s3

    result = upload_to_s3(
        file_bytes=b"test content",
        key="test-file.pdf",
        content_type="application/pdf",
        tags="test=1"
    )

    mock_s3.put_object.assert_called_once()
    assert result is False


@patch("services.s3.get_s3_client")
def test_delete_from_s3_success(mock_get_s3_client):
    mock_s3 = MagicMock()
    mock_get_s3_client.return_value = mock_s3

    result = delete_from_s3(
        key="test-file.pdf",
    )

    mock_s3.delete_object.assert_called_once()
    assert result is True

@patch("services.s3.get_s3_client")
def test_delete_from_s3_client_error(mock_get_s3_client):
    from botocore.exceptions import ClientError

    mock_s3 = MagicMock()
    mock_s3.delete_object.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDenied", "Message": "Denied!"}},
        operation_name="DeleteObject"
    )
    mock_get_s3_client.return_value = mock_s3

    result = delete_from_s3(
        key="test-file.pdf",
    )

    mock_s3.delete_object.assert_called_once()
    assert result is False