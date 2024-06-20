import logging

from database.db import create_db_and_tables, db_engine
from kpi_calculation_services import run_kpi_calculations

if __name__ == "__main__":
    try:
        create_db_and_tables(db_engine)
    except Exception as e:
        logging.error(f"Error during calling the create_db_and_tables in the main function: {repr(e)}")

    try:
        run_kpi_calculations()
    except Exception as e:
        logging.error(f"Error during calling the run_kpi_calculations in the main function: {repr(e)}")
