from threading import Thread
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from infra.queue_service import receive_messages, send_to_response_queue
from libraries import logger
from models.request_input import RequestInput
from models.reques_response import RequestResponse
from models.run import Run
from models.sqs_message import SQSMessage
from processes.process import WorkflowProcess
from setup.environment import Config

load_dotenv()

config = Config()
infra_variable = config.get_environment()

REQUEST_QUEUE_URL = infra_variable.get("REQUEST_QUEUE_URL")
RESPONSE_QUEUE_URL = infra_variable.get("RESPONSE_QUEUE_URL")

app = FastAPI()

def start_sqs_consumer_with_recovery():
    while True:
        try:
            logger.info("Iniciando consumidor da fila SQS")
        except Exception as e:
            logger.error(f"Erro no consumidor da fila SQS: {str(e)}. Reiniciando...")
            time.sleep(5)

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando o thread do consumidor da fila SQS")
    consumer_thread = Thread(target=start_consumer, daemon=True)
    consumer_thread.start()

@app.post("/process")
async def process_request(request_input: SQSMessage) -> JSONResponse:
    try:
        config = Config()
        request_input.data["product"] = request_input.product
        if not request_input.id:
            request_input.id = request_input.data.get("id")
        logger.info(request_input)

        request_parse_obj = RequestInput(**request_input.data)
        request_object = request_parse_obj.to_request_object()

        logger.info(request_object)
        run = Run(request_data=request_object, response_data=RequestResponse())
        process = WorkflowProcess(
            credentials=config.get_environment(), run=run, request=request_object
        )

        logger.info(f"Inicializando fluxo de {request_input.type}")
        process.start_workflow()
        response = process.export_response()

        request_input.response = response.to_dict()
        send_to_response_queue(request_input)

        return response.to_json_response()
    except Exception as e:
        logger.error("Erro durante o processamento da requisição")
        response = RequestResponse()
        response.status_code = 500
        response.message = str(e)
        request_input.response = response.to_dict()
        send_to_response_queue(request_input)
        return response.to_json_response()
    
@app.get("/health")
async def health():
    return JSONResponse(content={"status": True}, status_code=200)

def start_consumer():
    """Inicia o consumidor para a fila de requests."""
    while True:
        try:
            logger.info("Iniciando o consumer da fila...")
            receive_messages(REQUEST_QUEUE_URL)
        except Exception as e:
            logger.error(f"Erro no consumidor da fila: {str(e)}. Reiniciando...")
            time.sleep(5)