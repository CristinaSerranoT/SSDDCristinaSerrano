# discovery.py

import Ice
import IceDrive
import json
import IceStorm

class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self, proxy_a_enviar: IceStorm.TopicPrx, persistence_file="blob_persistence.json"):
        self.proxy_a_enviar = None
        self.persistence_file = persistence_file
        self.load_persistence()
        
    def load_persistence(self):
        try:
            with open(self.persistence_file, "r") as f:
                self.persistence_data = json.load(f)
        except FileNotFoundError:
            self.persistence_data = {}

    def save_persistence(self):
        with open(self.persistence_file, "w") as f:
            json.dump(self.persistence_data, f, indent=4)

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        print("Nuevo servicio authentication detectado: " + str(prx))

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive a Directory service announcement."""
        print("Nuevo servicio directory detectado: " + str(prx))

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive a Blob service announcement."""
        print("Nuevo servicio blob detectado: " + str(prx))
  
        self.persistence_data["blob_service"] = prx.ice_toString()
        self.save_persistence()
