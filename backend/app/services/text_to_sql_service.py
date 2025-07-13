import pandas as pd
import sqlalchemy
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class TextToSQLService:
    def __init__(self, db_path: str = settings.SQLITE_DB_PATH):
        self.db_path = db_path
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_path}")
        self.table_name = None

    def load_csv_to_sql(self, file_path: str):
        try:
            df = pd.read_csv(file_path)
            df.columns = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df.columns]
            self.table_name = os.path.splitext(os.path.basename(file_path))[0]
            logger.info(f"Loading data into SQLite table: {self.table_name}")
            df.to_sql(self.table_name, self.engine, if_exists='replace', index=False)
            logger.info(f"Successfully loaded CSV to SQL.")
            return True
        except Exception as e:
            logger.error(f"Failed to load CSV to SQL: {e}")
            return False

    def get_db_uri(self) -> str:
        return f"sqlite:///{self.db_path}"

text_to_sql_service = TextToSQLService()
