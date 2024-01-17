import logging
import sys
import Ice
from typing import List
from .blob import BlobService
from .discovery import Discovery


class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        # Inicia el adaptador del objeto
        adapter = self.communicator().createObjectAdapterWithEndpoints("BlobAdapter", "tcp -h localhost -p 10000")
        adapter.activate()

        # Crea una instancia del servicio de Blob
        blob_service = BlobService()

        # Añade el servicio al adaptador
        blob_proxy = adapter.add(blob_service, self.communicator().stringToIdentity("BlobService"))
        
        # Añade el adaptador a la interfaz de descubrimiento
        discovery_proxy = self.communicator().stringToProxy("Discovery/Discovery")
        discovery = Discovery.IceDrive.DiscoveryPrx.checkedCast(discovery_proxy)
        discovery.announceBlobService(blob_proxy)

        logging.info("BlobService proxy: %s", blob_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    sys.exit(app.main(sys.argv))
