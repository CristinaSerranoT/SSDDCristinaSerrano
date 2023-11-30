"""Module for servants implementations."""

import Ice

import IceDrive
import json
import hashlib

class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""

class BlobService(IceDrive.BlobService):
    """Implementation of an IceDrive.BlobService interface."""

    def __init__(self, storage_file="blob_storage.json"):
        self.storage_file = storage_file
        self.load_storage()
    
    # Este método devuelve el número de enlaces para el blob_id proporcionado.
    def load_storage(self):
        try:  
            with open(self.storage_file, "r") as file: 
                self.blobs = json.load(file) 
        except (FileNotFoundError, json.JSONDecodeError):   
            self.blobs = {} 
    
    # Este método guarda el diccionario de blobs en el archivo de almacenamiento.
    def save_storage(self):
        with open(self.storage_file, "w") as file: 
            json.dump(self.blobs, file)
    
    # Este método devuelve el número de enlaces para el blob_id proporcionado.
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        print("link", blob_id)
        # Incrementa el conteo de enlaces para el blob
        if blob_id in self.blobs:
            self.blobs[blob_id] += 1
        else:
            self.blobs[blob_id] = 1
        self.save_storage()

    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        print("unlink", blob_id)

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        print("upload")

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        print("download", blob_id)