import os
import threading

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException

from api.api import api_router
from database.db import create_db_and_tables, drop_db_and_tables
from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from events.event_receiver import EventReceiver
from services.async_services import AsyncServices
from models import models

logger = utility_functions.get_logger(logger_config)

app = FastAPI()
app.include_router(api_router)


def main():
    try:
        EventReceiver(
            host=os.getenv("RABBITMQ_HOST"),
            port=int(os.getenv("RABBITMQ_PORT")),
            username=os.getenv("RABBITMQ_USERNAME"),
            password=os.getenv("RABBITMQ_PASSWORD"),
            service=AsyncServices,
            logger=logger,
            queue_name=os.getenv("ASYNCQUEUE_NAME", "async_queue"),
        )
    except Exception as e:
        logger.exception(e)


@app.on_event("startup")
def on_startup():
    logger.debug(f"on_startup")
    try:
        # drop_db_and_tables(db_engine)
        create_db_and_tables(db_engine)

        main_thread = threading.Thread(target=main, daemon=True)
        main_thread.start()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to setup database.") from e


if __name__ == "__main__":
    logger.debug(f"run uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=80)
