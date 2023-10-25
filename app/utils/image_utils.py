from PIL import Image
from io import BytesIO
from google.cloud import storage
from app.utils.gcp_utils import storage_client

def create_thumbnail(file, blob_path, bucket_name):
    # Open the image file
    image = Image.open(file)
    
    # Perform thumbnail operation
    image.thumbnail((100, 100))
    
    # Save the thumbnail to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='JPEG')
    
    # Move the cursor to the beginning of the BytesIO object
    byte_stream.seek(0)
    
    # Create a blob object
    blob = storage.Blob(blob_path, bucket=storage_client.bucket(bucket_name))
    
    # Upload the thumbnail to GCS
    blob.upload_from_file(byte_stream, content_type='image/jpeg')
    
