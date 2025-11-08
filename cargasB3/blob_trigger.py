import azure.functions as func
import logging
import load.transform_load as transform_load

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="b3-dados-brutos",
                               connection="AZURE_CONNECTION_STRING") 
def load_b3_trigger(myblob: func.InputStream):
    logging.info('Iniciando processo de transformacao e carga dos dados B3.')
    transform_load.run(myblob)

    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")