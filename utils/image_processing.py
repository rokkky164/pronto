import logging
import os
from datetime import timedelta
import zipfile
import io
from exam import constants
from google.cloud import storage

logger = logging.getLogger(__name__)


class ImageProcessingConsumer:
    """
    A class to process and handle user images related to a specific exam using Google Cloud Storage.

    Methods:
        get_user_images(exam_id: int, user_id: int) -> dict:
            Retrieves a list of user images for a specific exam and user.

        get_bucket() -> google.cloud.storage.bucket.Bucket:
            Returns the Google Cloud Storage bucket used for storing and retrieving images.
    """

    @staticmethod
    def get_user_images(exam_id: int, user_id: int) -> dict:
        """
        Retrieves a list of user images for a specific exam and user.

        Args:
            exam_id (int): The identifier of the exam.
            user_id (int): The identifier of the user.

        Returns:
            dict: A dictionary containing two keys: "url_list" and "zip_url".
                - "url_list" contains a list of dictionaries, where each dictionary represents an image URL along with
                  additional information about the image (time and movement).
                - "zip_url" contains the signed URL to download a ZIP archive of all user images.

        """
        bucket = ImageProcessingConsumer.get_bucket()
        files_list = list(bucket.list_blobs(prefix=f'{user_id}/{exam_id}/images'))

        url_list = [{
            "url": blob.generate_signed_url(
                version='v4',
                expiration=timedelta(days=7),
                method='GET'),
            "time": blob.name.split("/")[-1].split('_')[-1].split('.')[0].split()[-1],
            "movement": "Face not found" if blob.name.split("/")[-1].split('_')[2] == 'blank' else
            "Looking " + blob.name.split("/")[-1].split('_')[2]
        } for blob in files_list]

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zip_obj:
            for blob in files_list:
                image_data = blob.download_as_bytes()
                image_filename = blob.name.split('/')[-1]
                zip_obj.writestr(image_filename, image_data)

        blob = bucket.blob(str(user_id) + '/' + str(exam_id) + '/zip/images.zip')
        blob.upload_from_string(zip_file.getvalue(), content_type='application/zip')

        zip_url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(days=7),
            method='GET'
        )

        return {"url_list": url_list, "zip_url": zip_url}

    @staticmethod
    def get_bucket():
        """
        Returns the Google Cloud Storage bucket used for storing and retrieving images.

        Returns:
            google.cloud.storage.bucket.Bucket: The Google Cloud Storage bucket object.

        """

        file_path = "prepstudyAPI/prep-study-eac899977c9b.json"

        storage_client = storage.Client.from_service_account_json(file_path)
        bucket = storage_client.bucket(constants.BUCKET_NAME)
        return bucket
