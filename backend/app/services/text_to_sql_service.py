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
        self.schema = None

    def load_csv_to_sql(self, file_path: str):
        """
        Loads a CSV file into a SQLite database, overwriting the table if it exists.
        """
        try:
            df = pd.read_csv(file_path)
            # Sanitize column names for SQL compatibility
            df.columns = [col.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') for col in df.columns]
            
            # Use the filename (without extension) as the table name
            self.table_name = os.path.splitext(os.path.basename(file_path))[0]
            
            logger.info(f"Loading data into SQLite table: {self.table_name}")
            df.to_sql(self.table_name, self.engine, if_exists='replace', index=False)
            
            # Store the schema for later use in prompts
            self.schema = pd.io.sql.get_schema(df, self.table_name, con=self.engine)
            logger.info(f"Successfully loaded CSV to SQL. Schema:\n{self.schema}")
            return True
        except Exception as e:
            logger.error(f"Failed to load CSV to SQL: {e}")
            return False

    def get_schema(self) -> str:
        """Returns the schema of the loaded table."""
        if not self.schema:
            logger.warning("Schema not available. Please load a CSV file first.")
            return "No schema loaded."
        return self.schema

    def execute_sql_query(self, sql_query: str) -> str:
        """
        Executes a given SQL query against the database and returns just the raw result.
        """
        try:
            print(sql_query)
            with self.engine.connect() as connection:
                result = pd.read_sql_query(sql_query, connection)

                # If the result is a single value (e.g., COUNT, SUM), extract it
                if result.shape == (1, 1):
                    return str(result.iat[0, 0])  # Get the only cell in the DataFrame

                # Otherwise, return the full table as string
                return result.to_string(index=False)  # Drop index from display
        except Exception as e:
            logger.error(f"Error executing SQL query '{sql_query}': {e}")
            return f"Error: Could not execute the query. Details: {e}"


# Create a single instance of the service
text_to_sql_service = TextToSQLService()
