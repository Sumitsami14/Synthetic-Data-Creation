import os
import pandas as pd
from utils.logger import logger

def export_to_csv(df: pd.DataFrame, filename: str, output_dir: str = "data"):
    """Exports a DataFrame to a CSV file."""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Data exported to {filepath}")
    except OSError as e:
        logger.error(f"Failed to export CSV to {filename}: {e}")
        raise

def export_to_json(df: pd.DataFrame, filename: str, output_dir: str = "data"):
    """Exports a DataFrame to a JSON file."""
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filepath = os.path.join(output_dir, filename)
        df.to_json(filepath, orient="records", indent=4)
        logger.info(f"Data exported to {filepath}")
    except OSError as e:
        logger.error(f"Failed to export JSON to {filename}: {e}")
        raise
