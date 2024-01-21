import logging
import sys
import os
import time

from typing import List
from .blob import BlobService
from .discovery import Discovery
import IceStorm

import Ice
Ice.loadSlice(os.path.join(os.path.dirname(__file__), "icedrive.ice"))
import IceDrive

class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""
        
        # Inicia el adaptador del objeto
        adapter = self.communicator().createObjectAdapterWithEndpoints("BlobAdapter", "tcp")
        adapter.activate()

        # Obtiene las propiedades del fichero de configuración (communicator)
        propiedades = self.communicator().getProperties()
        # Extraemos dos propiedades del fichero de configuración
        TopicDiscovery = propiedades.getProperty("DiscoveryTopic")
        # Obtiene el topic manager el cual es el manejador de los topics
        propiedad = self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(propiedad)

        # Te creas el canal de eventos para publicarte en el discovery
        try:  # En caso de que ya exista el topic te suscribes
            topic = topic_manager.retrieve(TopicDiscovery)
            logging.info("Conexion establecida al topic %s", TopicDiscovery)
        except IceStorm.NoSuchTopic:  # En caso de que no exista el topic te creas uno nuevo
            topic = topic_manager.create(TopicDiscovery)
            logging.info("Conexion creada al topic %s", TopicDiscovery)

        # Creamos los diccionarios que van a almacenar los anuncios de los servicios
        almacenamiento_announcement_blob = {}
        almacenamiento_announcement_directory = {}
        almacenamiento_announcement_authentication = {}

        # Creacion del publicador (el que controla los announcements, es decir la clase discovery)
        # Ahora vamos a crear un objeto de la clase discovery que va a ser el que mande los mensajes de nuestro proxy de nuestro servicio
        discovery = Discovery(almacenamiento_announcement_blob, almacenamiento_announcement_directory, almacenamiento_announcement_authentication)
        discovery_proxy = adapter.addWithUUID(discovery)
        # Nos declaramos como suscriptor y publicador del topic
        topic.subscribeAndGetPublisher(None, discovery_proxy)  # Te suscribes al topic
        discovery_publicador = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher())  # Sacamos el publicador del topic

        # Crea una instancia del servicio de Blob
        blob_service = BlobService(almacenamiento_announcement_blob, almacenamiento_announcement_authentication)
        sirviente = adapter.addWithUUID(blob_service)
        # Añade el servicio al adaptador
        proxy_a_enviar = IceDrive.BlobServicePrx.checkedCast(sirviente)

        # La variable proxy_propio es para que el servicio no se publique a si mismo
        discovery.proxy_propio = str(proxy_a_enviar.ice_getIdentity().name)
        
        # Publica el servicio en el topic cada 5 segundos y recibe los anuncios de los otros servicios
        try:
            while True:
                # Publica el servicio en el topic
                discovery_publicador.announceBlobService(proxy_a_enviar)
                print("Publicando mi servicio blob: " + str(proxy_a_enviar))
                time.sleep(5)

        except KeyboardInterrupt:
            # Manejar la excepción de interrupción de teclado 
            logging.info("Interrupción de teclado. Saliendo del bucle.")

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    sys.exit(app.main(sys.argv))
