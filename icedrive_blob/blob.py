"""Module for servants implementations."""

import Ice

import IceDrive
import json
import hashlib
import os

ARCHIVOS = "archivosCopiados"

class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "rb")

    # Este método lee un bloque de datos del archivo abierto y lo devuelve como una lista de bytes.
    def read(self, size: int, current: Ice.Current = None) -> bytes:
            """Returns a list of bytes from the opened file."""
            data = self.file.read(size)
            return data if data else b''  # Devuelve b'' cuando no hay más datos
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
        with open(self.storage_file, "w") as file:
            file.write("{\n")
            for i, (blob_id, enlaces) in enumerate(self.blobs.items()):
                file.write(f'    "{blob_id}": {enlaces}')
                if i < len(self.blobs) - 1:
                    file.write(",")
                file.write("\n")
            file.write("}\n")
    
    # Este método devuelve el número de enlaces para el blob_id proporcionado.
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
            # Verifica si el blob_id es válido antes de incrementar los enlaces
        if blob_id not in self.blobs:
            raise IceDrive.UnknownBlob(blob_id)

        # Incrementa el conteo de enlaces para el blob
        self.blobs[blob_id] += 1
        self.save_storage()
        print(f"Enlace exitoso para el blob con ID: {blob_id}. Total de enlaces: {self.blobs[blob_id]}")


    # Este método decrementa el número de enlaces para el blob_id proporcionado y elimina el blob si ya no está enlazado.
    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        # Decrementa el conteo de enlaces y elimina el blob si ya no está enlazado
        if blob_id in self.blobs:
            self.blobs[blob_id] -= 1
            if self.blobs[blob_id] == 0:
                del self.blobs[blob_id]
                os.remove(os.path.join(ARCHIVOS, f"{blob_id}.txt"))
            self.save_storage()
        else:
            print(f"Desenlace exitoso para el blob con ID: {blob_id}. Total de enlaces: {self.blobs[blob_id]}")
            raise IceDrive.UnknownBlob(blob_id)
            


    def upload(
        self, user: IceDrive.UserPrx, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
            """Register a DataTransfer object to upload a file to the service."""
            try:
                if blob:
                    # Calcula el hash del blob usando SHA256 como identificador
                    blob_data = bytearray()
                    size = 1024  # Tamaño del bloque para leer
                    while True:
                        data = blob.read(size)
                        if not data:
                            break
                        blob_data.extend(data)
                    
                    # Calcula el hash del blob usando SHA256 como identificador
                    blob_id = hashlib.sha256(blob_data).hexdigest()

                    # Verifica que el blob_id coincida con el hash SHA256 del contenido del blob
                    if blob_id != hashlib.sha256(blob_data).hexdigest():
                        raise IceDrive.InvalidBlobId("El blob_id no coincide con el hash SHA256 del contenido del blob.")

                    # Crea la carpeta de guardado si no existe
                    os.makedirs(ARCHIVOS, exist_ok=True)
                    
                    # Guarda el contenido del blob en un archivo en la carpeta de guardado
                    file_path = os.path.join(ARCHIVOS, f"{blob_id}.txt")
                    
                    with open(file_path, "wb") as file:
                        file.write(blob_data)
                else:
                    raise IceDrive.FailedToReadData(blob_id)
            except IceDrive.FailedToReadData as exception:
                print(f"Error al subir el blob: {exception}")
            except IceDrive.InvalidBlobId as exception:
                print(f"Error al subir el blob: {exception}")
            else:
                print("Blob subido con éxito. Blob ID:", blob_id)
                blob.close() # Para cerrar el archivo abierto y que no de error al cerrar el cliente
                self.blobs[blob_id] = 1
                self.save_storage()
                return blob_id
            
    def download(
        self, user: IceDrive.UserPrx, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer object to enable the client to download the given blob_id."""
        # Verifica si el blob_id es válido antes de devolver el proxy
        if blob_id in self.blobs:
            file_path = os.path.join(ARCHIVOS, f"{blob_id}.txt")
            servant = DataTransfer(file_path)
            proxy = current.adapter.addWithUUID(servant)
            data_transfer_proxy = IceDrive.DataTransferPrx.checkedCast(proxy)
            return data_transfer_proxy
        else: # Si el blob_id no es válido, lanza una excepción
            raise IceDrive.UnknownBlob(blob_id)
