from typing import Optional, Sequence
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud import storage

def process_image_source_quality_check(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    bucket_name: str,
    blob_name: str,
    mime_type: str,
) -> None:
    """
    Process a document using the Image Source Quality Check processor.

    Args:
        project_id: The Google Cloud project ID.
        location: The location of the processor.
        processor_id: The ID of the processor.
        processor_version: The version of the processor.
        bucket_name: The name of the GCS bucket.
        blob_name: The name of the blob (file) in GCS.
        mime_type: The MIME type of the file.
    """
    # Import documentai module here
    from google.cloud import documentai

    client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )

    name = client.processor_version_path(project_id, location, processor_id, processor_version)

    # Download the image file from GCS
    file_path = "temp_image.jpg"  # Temporary local file
    download_blob(bucket_name, blob_name, file_path)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Configure the process request
    process_options = documentai.ProcessOptions(
        ocr_config=documentai.OcrConfig(
            enable_image_quality_scores=True,
        )
    )

    document = process_document(project_id, location, processor_id, processor_version, image_content, mime_type, process_options=process_options)

    print("Full document text:")
    print(document.text)
    print(f"There are {len(document.pages)} page(s) in this document.")

    for page in document.pages:
        if page.image_quality_scores:
            print("Image Quality Scores:")
            print_image_quality_scores(page.image_quality_scores)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f'Blob {source_blob_name} downloaded to {destination_file_name}.')

def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    content: bytes,
    mime_type: str,
    process_options: Optional[documentai.ProcessOptions] = None,
) -> documentai.Document:
    client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )

    name = client.processor_version_path(project_id, location, processor_id, processor_version)

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(content=content, mime_type=mime_type),
        process_options=process_options,
    )

    result = client.process_document(request=request)

    return result.document

def print_image_quality_scores(
    image_quality_scores: documentai.Document.Page.ImageQualityScores,
) -> None:
    print(f"    Quality score: {image_quality_scores.quality_score:.7f}")
    print("    Detected defects:")

    for detected_defect in image_quality_scores.detected_defects:
        print(f"        {detected_defect.type_}: {detected_defect.confidence:.7f}")

# Example usage
process_image_source_quality_check(
    project_id="project-id",
    location="us",
    processor_id="your-processor-id",
    processor_version="rc",
    bucket_name="input-bucketname",
    blob_name="filname.png",
    mime_type="image/jpeg"
)
