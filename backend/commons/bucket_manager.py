from google.cloud import storage
import logging

class BucketManager:
    """Gestisce l'inizializzazione e lo svuotamento di un bucket GCS."""

    def __init__(self, bucket_name: str) -> None:
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(bucket_name)
        self._validate_bucket()

    def _validate_bucket(self) -> None:
        """Verifica che il bucket esista e sia accessibile."""
        if not self.bucket.exists():
            error_msg = f"Bucket {self.bucket_name} non esiste!"
            logging.critical(error_msg)
            raise ValueError(error_msg)
    
    def empty_bucket(self) -> None:
        """Svuota completamente il bucket eliminando tutti gli oggetti."""
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            blob.delete()
        logging.info(f"Il bucket {self.bucket_name} è stato svuotato con successo.")
    
    def get_blob(self, blob_name: str):
        return self.bucket.blob(blob_name)
    
    def get_blob_uri(self, blob_name: str) -> str:
        return f"gs://{self.bucket_name}/{blob_name}"

    def list_files(self, prefix=None) -> list:
        
        return [blob.name for blob in self.bucket.list_blobs(prefix=prefix)]
    
    def delete_files_under_path(self, prefix: str) -> None:
        """
        Elimina tutti i file sotto un determinato percorso nel bucket.
        """
        blobs = self.bucket.list_blobs(prefix=prefix)
        deleted_files = [blob.name for blob in blobs]

        if not deleted_files:
            return

        for blob_name in deleted_files:
            self.bucket.blob(blob_name).delete()
    
    def upload_file(self, local_file_path: str, destination_blob_path: str) -> None:

        blob = self.bucket.blob(destination_blob_path)
        blob.upload_from_filename(local_file_path)