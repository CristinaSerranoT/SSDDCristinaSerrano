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
        
        #Extraemos dos propiedades del fichero de configuración
        TopicDiscovery = propiedades.getProperty("DiscoveryTopic")

        # Obtiene el topic manager el cual es el manejador de los topics
        propiedad = self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(propiedad)

        # Te creas el canal de eventos para publicarte en el discovery
        try: #En caso de que ya exista el topic te suscribes
            topic = topic_manager.retrieve(TopicDiscovery)
            logging.info("Conexion establecida al topic %s", TopicDiscovery)
        except IceStorm.NoSuchTopic: #En caso de que no exista el topic te creas uno nuevo
            topic = topic_manager.create(TopicDiscovery)
            logging.info("Conexion creada al topic %s", TopicDiscovery)

        # Creacion del publicador (el que controla los announcements, es decir la clase discovery)
        # Ahora vamos a crear un objeto de la clase discovery que va a ser el que mande los mensajes de nuestro proxy de nuestro servicio
        discovery = Discovery()
        discovery_proxy = adapter.addWithUUID(discovery)
        # Nos declaramos como subcriptor y publicador del topic
        topic.subscribeAndGetPublisher(None, discovery_proxy) #Te suscribes al topic
        discovery_publicador = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher()) # Sacamos el publicador del topic
        
        # Crea una instancia del servicio de Blob
        blob_service = BlobService()

        # Añade el servicio al adaptador
        blob_proxy = adapter.add(blob_service, self.communicator().stringToIdentity("BlobService"))
        proxy_a_enviar = IceDrive.BlobServicePrx.uncheckedCast(blob_proxy)
        
        # Publica el servicio en el topic
        # Hay que hacer que esto se repita cada 5 segundos
        discovery_publicador.announceBlobService(proxy_a_enviar)
        print("Nuevo servicio blob detectado: " + str(proxy_a_enviar))
        
        #Se tiene que publicar el sercicio cada 5 segundos
        try:
            while True:
                # Publica el servicio en el topic
                discovery_publicador.announceBlobService(proxy_a_enviar)
                print("Nuevo servicio blob detectado: " + str(proxy_a_enviar))
                time.sleep(5)

        except KeyboardInterrupt:
            # Manejar la excepción de interrupción de teclado (Ctrl+C)
            logging.info("Interrupción de teclado. Saliendo del bucle.")

        logging.info("BlobService proxy: %s", proxy_a_enviar)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    sys.exit(app.main(sys.argv))
