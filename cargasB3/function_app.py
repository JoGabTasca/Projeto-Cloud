import logging
import azure.functions as func
import extract.extract as extract
import load.transform_load as transform_load

app = func.FunctionApp()

# teste "0/20 * * * * *"
# correto "0 30 21 * * 1-5"
@app.timer_trigger(schedule="0 30 21 * * 1-5", arg_name="myTimer", run_on_startup=False,
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

@app.blob_trigger(
    arg_name="myblob",
    path="b3-dados-brutos/{name}.xml",
    connection="AZURE_CONNECTION_STRING",
)
def load_b3_trigger(myblob: func.InputStream):
    """Processa arquivos XML do B3 quando detectados no blob storage."""
    blob_name = myblob.name.split('/')[-1]
    
    logging.info("="*80)
    logging.info(f"[BLOB TRIGGER] Novo arquivo XML detectado: {blob_name}")
    logging.info(f"[BLOB TRIGGER] Tamanho: {myblob.length / (1024*1024):.2f} MB")
    logging.info("="*80)
    
    try:
        logging.info("[BLOB TRIGGER] Iniciando processamento (pode demorar alguns minutos)...")
        
        # Chama a funcao que busca e processa o blob mais recente, ou pode passar o blob como parametro
        transform_load.run(myblob)
        
        logging.info("="*80)
        logging.info(f"[BLOB TRIGGER] ✓ Processamento concluído com sucesso: {blob_name}")
        logging.info("="*80)
    except Exception as e:
        logging.error("="*80)
        logging.error(f"[BLOB TRIGGER] ✗ ERRO no processamento de {blob_name}")
        logging.error(f"[BLOB TRIGGER] Erro: {str(e)}")
        logging.error("="*80)
        logging.exception(e)
        raise