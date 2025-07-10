import os
import argparse
import logging
from datetime import datetime

from etl.extract import fetch_earthquake_all_day
from etl.transform import clean_earthquake_data, enrich_earthquake_data
from etl.load import upload_to_bigquery

from prefect_gcp import GcpCredentials
from prefect import flow

from dotenv import load_dotenv
load_dotenv()

@flow(name="ETL Pipeline", log_prints=True)

def run_pipeline(mode:str="replace")-> None:
    """
    run the etl pipline with configure mode.
    
    Args:
        mode (str, optional): "replace", "fail", "append". Defaults to "replace".
    """
    logging.info(f"Starting ETL pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Extract
    logging.info("Extracting data...")
    raw = fetch_earthquake_all_day()
    if raw.empty:
        logging.warning("No data to fatched. Exiting...")
        return

    # 2. Transform
    logging.info("Transforming data...")
    logging.info(f"-- Data Cleanup")
    cleaned = clean_earthquake_data(raw)
    logging.info(f"-- Data Enrichment")
    enriched = enrich_earthquake_data(cleaned)

    # 3. Load
    PROJECT_ID = os.getenv("PROJECT_ID")
    TABLE_ID = os.getenv("TABLE_ID")
    

    logging.info("Loading data to BigQuery...")
    upload_to_bigquery(enriched, TABLE_ID, PROJECT_ID, mode)


    logging.info(f"Complete ETL pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return

if __name__ == "__main__":
    run_pipeline()

  
   