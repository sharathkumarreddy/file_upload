import os
import pytest
from unittest.mock import Mock, patch
from file_upload.file_upload import UploadFile
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_directory = BASE_DIR +'/tests/file_directory/'

# Mock the AWS S3 and Google Cloud Storage clients
@patch('boto3.client')
@patch('google.cloud.storage.Client')
def test_transfer_files(mock_boto3_client, mock_storage_client):
    aws_s3_client = Mock()
    mock_boto3_client.return_value = aws_s3_client

    gcp_storage_client = Mock()
    mock_storage_client.return_value = gcp_storage_client
    gcp_bucket = Mock()
    gcp_storage_client.bucket.return_value = gcp_bucket

    uploader = UploadFile('aws_access_key', 'aws_secret_key', 'aws_s3_bucket', 'gcp_project_id', 'gcp_bucket_name')

    s3_extensions = (".jpg", ".png", ".svg", ".webp", ".mp3", ".mp4", ".mpeg4", ".wmv", ".3gp", ".webm")
    gcp_extensions = (".doc", ".docx", ".csv", ".pdf")

    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [(file_directory, ['sub_directory'], ['test_mp4.mp3', 'test_mp3.mp4', 'test_3gp.3gp', 'test_doc.docx', 'test_file.txt']), 
                                  (file_directory+'sub_directory', [], ['test_pdf.pdf', 'test_mpeg4.mpeg4'])]
        
        with patch('file_upload.file_upload.UploadFile.upload_to_aws_s3') as mock_upload_to_aws_s3, \
             patch('file_upload.file_upload.UploadFile.upload_to_gcp_storage') as mock_upload_to_gcp_storage:
            uploader.transfer_files(file_directory, s3_extensions, gcp_extensions)

            mock_upload_to_aws_s3.assert_called_with(file_directory+'sub_directory/test_mpeg4.mpeg4', 'test_mpeg4.mpeg4', 'aws_s3_bucket')
            mock_upload_to_gcp_storage.assert_called_with(file_directory+'sub_directory/test_pdf.pdf', 'test_pdf.pdf')


@patch('boto3.client')
def test_upload_to_aws_s3_success(mock_boto3_client):
    aws_s3_client = Mock()
    mock_boto3_client.return_value = aws_s3_client
    uploader = UploadFile('aws_access_key', 'aws_secret_key', 'aws_s3_bucket', 'gcp_project_id', 'gcp_bucket_name')
    file_path = file_directory+'test_mp3.mp4'
    file_name = 'test_mp3.mp4'
    s3_bucket = 'aws_s3_bucket'

    with patch('file_upload.file_upload.UploadFile'):
        uploader.upload_to_aws_s3(file_path, file_name, s3_bucket)

    aws_s3_client.upload_file.assert_called_with(file_path, s3_bucket, file_name)


@patch('boto3.client')
def test_upload_to_aws_s3_failure(mock_boto3_client):
    aws_s3_client = Mock()
    mock_boto3_client.return_value = aws_s3_client
    uploader = UploadFile('aws_access_key', 'aws_secret_key', 'aws_s3_bucket', 'gcp_project_id', 'gcp_bucket_name')
    file_path = file_directory+'test_doc.docx'
    file_name = 'test_doc.docx'
    s3_bucket = 'aws_s3_bucket'

    aws_s3_client.upload_file.side_effect = Exception('Upload failed')

    with pytest.raises(Exception) as exc_info:
        uploader.upload_to_aws_s3(file_path, file_name, s3_bucket)

    assert f'Failed to upload {file_name} to AWS S3: Upload failed' in str(exc_info.value)

@patch('google.cloud.storage.Client')
def test_upload_to_gcp_storage_success(mock_storage_client):
    gcp_storage_client = Mock()
    mock_storage_client.return_value = gcp_storage_client
    gcp_bucket = Mock()
    gcp_storage_client.bucket.return_value = gcp_bucket
    uploader = UploadFile('aws_access_key', 'aws_secret_key', 'aws_s3_bucket', 'gcp_project_id', 'gcp_bucket_name')
    file_path = file_directory+'test_file.txt'
    file_name = 'test_file.txt'

    with patch('file_upload.file_upload.UploadFile'):
        uploader.upload_to_gcp_storage(file_path, file_name)

    gcp_bucket.blob.assert_called_with(file_name)
    gcp_bucket.blob.return_value.upload_from_filename.assert_called_with(file_path)

@patch('google.cloud.storage.Client')
def test_upload_to_gcp_storage_failure(mock_storage_client):
    gcp_storage_client = Mock()
    mock_storage_client.return_value = gcp_storage_client
    gcp_bucket = Mock()
    gcp_storage_client.bucket.return_value = gcp_bucket
    uploader = UploadFile('aws_access_key', 'aws_secret_key', 'aws_s3_bucket', 'gcp_project_id', 'gcp_bucket_name')
    file_path = file_directory+'test_pdf.pdf'
    file_name = 'test_pdf.pdf'

    gcp_bucket.blob.return_value.upload_from_filename.side_effect = Exception('Upload failed')

    with pytest.raises(Exception) as exc_info:
        uploader.upload_to_gcp_storage(file_path, file_name)

    assert f'Failed to upload {file_name} to Google Cloud Storage: Upload failed' in str(exc_info.value)
