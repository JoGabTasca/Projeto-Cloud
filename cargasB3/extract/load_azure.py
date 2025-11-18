import os

import azure.storage.blob as BlobServiceClient

DEFAULT_CONTAINER = "b3-dados-brutos"


def _get_connection_string():
    conn = os.getenv("AZURE_CONNECTION_STRING") or os.getenv("AzureWebJobsStorage")
    if not conn:
        raise RuntimeError(
            "Defina AZURE_CONNECTION_STRING (ou AzureWebJobsStorage) para acessar o Blob Storage."
        )
    return conn


def _get_container_client():
    container_name = os.getenv("BLOB_CONTAINER_NAME") or DEFAULT_CONTAINER
    service = BlobServiceClient.BlobServiceClient.from_connection_string(
        _get_connection_string()
    )
    return service.get_container_client(container_name)


def upload_to_azure(file_name, local_pathe_file):
    container = _get_container_client()
    try:
        container.create_container() # Tenta criar o container
    except Exception:
        pass  # Container(Pasta) já existe

    with open(local_pathe_file, "rb") as data:
        container.upload_blob(name=file_name, data=data, overwrite=True) # Faz upload do arquivo
        print(
            f"LOAD_AZURE: [OK] Arquivo {file_name} enviado para o Azure Blob Storage no container {container.container_name}"
        )

def get_file_from_blob(file_name):
    container = _get_container_client()
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
