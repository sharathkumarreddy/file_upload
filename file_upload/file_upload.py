import os
import boto3
from google.cloud import storage

class UploadFile:
    """
    A class for transferring image and media files to AWS S3 and documents to Google Cloud Storage.

    Attributes:
        aws_s3_client (boto3.client): An AWS S3 client .
        gcp_storage_client (google.cloud.storage.Client): A Google Cloud Storage client.
        gcp_bucket (google.cloud.storage.bucket.Bucket): The GCP bucket to upload files.
    """
    def __init__(self, aws_access_key, aws_secret_key, aws_s3_bucket, gcp_project_id, gcp_bucket_name):
        """
        Initialize the FileTransfer instance.

        Args:
            aws_access_key (str): AWS access key.
            aws_secret_key (str): AWS secret key.
            aws_s3_bucket (str): Name of the AWS S3 bucket
            gcp_project_id (str): Google Cloud project ID.
            gcp_bucket_name (str): Name of the Google Cloud Storage bucket.
        """
        self.aws_s3_client = boto3.client('s3', aws_access_key_id = aws_access_key, aws_secret_access_key=aws_secret_key)
        self.aws_s3_bucket_name = aws_s3_bucket
        self.gcp_storage_client = storage.Client(project=gcp_project_id)
        self.gcp_bucket_name = self.gcp_storage_client.bucket(gcp_bucket_name)

    def transfer_files(self, directory, s3_extensions, gcp_extensions):
        """
        Transfer files from a directory to AWS S3 and Google Cloud Storage based on their extensions.

        Args:
            directory (str): The directory containing files to transfer.
            s3_extensions (tuple): Tuple of file extensions to transfer to AWS S3.
            gcp_extensions (tuple): Tuple of file extensions to transfer to Google Cloud Storage.
        """
        for root_directory, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root_directory, file)
                if file.lower().endswith(s3_extensions):
                    try:
                        self.upload_to_aws_s3(file_path, file, self.aws_s3_bucket_name)
                    except Exception as e:
                        print(f"Failed to upload {file} to AWS S3: {str(e)}")
                elif file.lower().endswith(gcp_extensions):
                    try:
                        self.upload_to_gcp_storage(file_path, file)
                    except Exception as e:
                        print(f"Failed to upload {file} to Google Cloud Storage: {str(e)}")

    def upload_to_aws_s3(self, file_path, file_name, s3_bucket_name):
        """
        Upload a file to AWS S3.

        Args:
            file_path (str): Path to the file to be uploaded.
            s3_bucket_name: Name of the AWS S3 bucket
            file_name (str): Name of the uploaded file in s3.
        """
        try:
            self.aws_s3_client.upload_file(file_path, s3_bucket_name, file_name)
        except Exception as e:
            raise Exception(f"Failed to upload {file_name} to AWS S3: {str(e)}")

    def upload_to_gcp_storage(self, file_path, file_name):
        """
        Upload a file to Google Cloud Storage.

        Args:
            file_path (str): Path to the file to be uploaded.
            file_name (str): Name of the uploaded file in Google Colud Storage.
        """
        try:
            blob = self.gcp_bucket_name.blob(file_name)
            blob.upload_from_filename(file_path)
        except Exception as e:
            raise Exception(f"Failed to upload {file_name} to Google Cloud Storage: {str(e)}")
