from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os

class BigQueryConnection():
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ottiene la directory del file corrente
        CREDENTIALS_PATH = os.path.join(BASE_DIR,  "be_credentials.json")

        with open(CREDENTIALS_PATH, 'r') as json_file:
            service_account_info = json.load(json_file)
        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        
        self.connection = self.connect_to_bigquery()

    def connect_to_bigquery(self):
        # Crea una connessione a BigQuery
        return bigquery.Client(
                credentials = self.credentials,
                project = self.credentials.project_id,
            )
        
    def execute_query(self, sql, params=None):
        try:
            query_parameters = []
            if params:
                for key, value in params.items():
                    if isinstance(value, int):
                        query_parameters.append(bigquery.ScalarQueryParameter(key, "INT64", value))
                    elif isinstance(value, float):
                        query_parameters.append(bigquery.ScalarQueryParameter(key, "FLOAT64", value))
                    elif isinstance(value, bool):
                        query_parameters.append(bigquery.ScalarQueryParameter(key, "BOOL", value))
                    else:
                        query_parameters.append(bigquery.ScalarQueryParameter(key, "STRING", value))
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
            
            print(f"query: {sql}")
            print(f"job_config: {job_config}")
            query_job = self.connection.query(sql, job_config=job_config)
            results = query_job.result()
            
            if results.total_rows is None or results.total_rows == 0:
                return []
            
            return [dict(row) for row in results]
        
        except Exception as e:
            print(f"Errore durante l'esecuzione della query: {sql}, con parametri: {params}")
            raise e
    def _create_schema(self, schema: list):
        result = []
        for element in schema:
            result.append(bigquery.SchemaField(element['name'], element['type'], mode="NULLABLE"))

        return result

    def execute_job(self, sql_query, dwh_project, dwh_dataset, dwh_table, mode="WRITE_TRUNCATE"):

        try:
            # Configura il job
            job_config = bigquery.QueryJobConfig()
            job_config.destination = f"{dwh_project}.{dwh_dataset}.{dwh_table}"
            job_config.write_disposition = mode
            job_config.use_legacy_sql = False

            # Esegue il job
            query_job = self.connection.query(
                sql_query,
                job_config=job_config
            )
            
            # Attende il completamento del job
            query_job.result()
            
            return query_job
            
        except Exception as e:
            print(f"Errore durante l'esecuzione del job: {str(e)}")
            raise e