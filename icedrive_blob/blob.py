"""Module for servants implementations."""

import Ice

import IceDrive
import json


class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "rb")

    # Este método lee un bloque de datos del archivo abierto y lo devuelve como una lista de bytes.
    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file."""
        data = self.file.read(size)
        if not data:
            raise IceDrive.FailedToReadData()
        return data
    # Este método cierra el archivo abierto.
    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        self.file.close()
        
        
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
        with open(self.storage_file, "w") as file: # Guarda el contenido del diccionario en el archivo
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

    # Este método decrementa el número de enlaces para el blob_id proporcionado y elimina el blob si ya no está enlazado.
    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        print("unlink", blob_id)
        # Decrementa el conteo de enlaces y elimina el blob si ya no está enlazado
        if blob_id in self.blobs:
            self.blobs[blob_id] -= 1
            if self.blobs[blob_id] == 0:
                del self.blobs[blob_id]
        self.save_storage()

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