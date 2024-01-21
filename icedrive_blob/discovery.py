# discovery.py

import logging
import Ice
import IceDrive
import json
import IceStorm

class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self, almacenamiento_announcement_blob: dict, almacenamiento_announcement_directory: dict, almacenamiento_announcement_authentication: dict):
        self.almacenamiento_announcement_authentication = almacenamiento_announcement_authentication
        self.almacenamiento_announcement_directory = almacenamiento_announcement_directory
        self.almacenamiento_announcement_blob = almacenamiento_announcement_blob
        # Variable para que nuestro propio servicio no se publique/reciba a si mismo
        self.proxy_propio = None
        
    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        # Comprueba si el prx recibido no está en nuestro almacenamiento de anuncios de Authentication 
        if str(prx.ice_getIdentity().name) not in self.almacenamiento_announcement_authentication:
            self.almacenamiento_announcement_authentication[prx.ice_getIdentity().name] = prx
            logging.info("Nuevo servicio authentication detectado: %s", str(prx))

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive a Directory service announcement."""
        # Comprueba si el prx recibido no está en nuestro almacenamiento de anuncios de Directory
        if str(prx.ice_getIdentity().name) not in self.almacenamiento_announcement_directory:
            self.almacenamiento_announcement_directory[prx.ice_getIdentity().name] = prx
            logging.info("Nuevo servicio directory detectado: %s", str(prx))


    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive a Blob service announcement."""
        # Comprueba si el prx recibido no está en nuestro almacenamiento de anuncios de Blob y si no es el nuestro propio
        if str(prx.ice_getIdentity().name) not in self.almacenamiento_announcement_blob and self.proxy_propio != str(prx.ice_getIdentity().name):
            self.almacenamiento_announcement_blob[prx.ice_getIdentity().name] = prx
            logging.info("Nuevo servicio blob detectado: %s", str(prx))
