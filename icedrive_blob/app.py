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

class Otros_Servicios():
    """Object for a proxy"""
    def __init__(self, proxy_a_enviar: IceDrive.BlobServicePrx):
        self.service_id = str(proxy_a_enviar.ice_getIdentity().name)
        self.proxy_a_enviar = proxy_a_enviar
        self.timer = None

class Almacenamiento():
    def __init__(self):
        self.authentications_dict = {}
        self.directory_services_dict = {}
        self.blob_services_dict = {}
        self.lock = threading.Lock()

    def update_service(self, service_type, proxy):
        service_id = str(proxy.ice_getIdentity().name)
        new_service = Servicios_Externos(proxy)
        with self.lock:
            if service_type == 'Authentication':
                self.authentications_dict[service_id] = new_service
            elif service_type == 'Directory':
                self.directory_services_dict[service_id] = new_service
            elif service_type == 'Blob':
                if service_id not in self.blob_services_dict:
                    new_service.timer = self.service_timer(service_id, self.blob_services_dict)
                    new_service.timer.start()
                self.blob_services_dict[service_id] = new_service

    def service_timer(self, service_id, services_dict):
        def timer_function():
            # Aquí puedes realizar acciones periódicas para el servicio
            print(f"Timer function for {service_id}")
            with self.lock:
                del services_dict[service_id]
        return threading.Timer(10.0, timer_function)  # Cambia 10.0 por el intervalo deseado

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
        discovery = Discovery(None, "blob_persistence.json")
        discovery_proxy = adapter.addWithUUID(discovery)
        # Nos declaramos como subcriptor y publicador del topic
        topic.subscribeAndGetPublisher(None, discovery_proxy) #Te suscribes al topic
        discovery_publicador = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher()) # Sacamos el publicador del topic
        
        # Crea una instancia del servicio de Blob
        blob_service = BlobService()

        # Añade el servicio al adaptador
        blob_proxy = adapter.add(blob_service, self.communicator().stringToIdentity("BlobService"))
        proxy_a_enviar = IceDrive.BlobServicePrx.uncheckedCast(blob_proxy)
        
        # Crea una instancia de la clase Discovery y pásale el propio proxy del servicio Blob
        discovery = Discovery(proxy_a_enviar, "blob_persistence.json")
        discovery_proxy = adapter.addWithUUID(discovery)
        
        # Nos declaramos como suscriptor y publicador del topic
        topic.subscribeAndGetPublisher(None, discovery_proxy)
        discovery_publicador = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher())
        
        # Publica el servicio en el topic
        # Hay que hacer que esto se repita cada 5 segundos
        #discovery_publicador.announceBlobService(proxy_a_enviar)
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
    #app = BlobApp(Otros_Servicios)
    #sys.exit(app.main(sys.argv))
