import logging
import azure.functions as func
import extract.extract as extract
import load.transform_load as transform_load

app = func.FunctionApp()

@app.timer_trigger(schedule="0/20 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_b3_trigger(myTimer: func.TimerRequest) -> None:
    try:
        logging.info('Executando extracao arquivos b3.')
        extract.run()
        logging.info('Extracao de arquivos B3 concluida com sucesso.')
    except Exception as e:
        logging.error(f'Erro na extracao de arquivos B3: {str(e)}')
        logging.exception(e)  # Loga o stack trace completo
        raise  # Re-lança a exceção para o Azure registrar como falha

@app.blob_trigger(arg_name="myblob", path="b3-dados-brutos/{name}.xml",
                  connection="AZURE_CONNECTION_STRING") 
def load_b3_trigger(myblob: func.InputStream):
    logging.info(f'Iniciando processo de transformacao e carga dos dados B3 para: {myblob.name}')
    transform_load.run(myblob)
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")