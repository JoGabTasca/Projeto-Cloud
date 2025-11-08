import azure.storage.blob as BlobServiceClient
import os

AZURE_BLOB_CONNECTION = os.getenv("AZURE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

def upload_to_azure(file_name, local_pathe_file):
    service = BlobServiceClient.BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(BLOB_CONTAINER_NAME)
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    with open(local_pathe_file, "rb") as data:
        container.upload_blob(name=file_name, data=data, overwrite=True) # Faz upload do arquivo
        print(f"LOAD_AZURE: [OK] Arquivo {file_name} enviado para o Azure Blob Storage no container {BLOB_CONTAINER_NAME}")

def get_file_from_blob(file_name):
    service = BlobServiceClient.BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION)
    container = service.get_container_client(BLOB_CONTAINER_NAME)
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    blob_client = container.get_blob_client(file_name)

    try:
        download_stream = blob_client.download_blob()
        blob_content = download_stream.readall().decode('utf-8')
        return blob_content
    except Exception as e:
        print(f'Error reading blob {e}')