"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        print("Nuevo servicio authentication detectado: " + str(prx))
        # Haz lo mismo que en el announceBlobService pero con el servicio de autenticacion TAREA
        # No se puede recibir el nuestro propio porque es un blob, no un authentication TAREA

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        print("Nuevo servicio directory detectado: " + str(prx))
        # Haz lo mismo que en el announceBlobService pero con el servicio de directorio TAREA
        # No se puede recibir el nuestro propio porque es un blob, no un directory TAREA
        
    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        # Mandamos una notificacion sobre que hemos detectado un nuevo servicio blob
        print("Nuevo servicio blob detectado: " + str(prx))
        # Nos guardamos el proxy del servicio blob TAREA
        # Si se recibe nuestro propio proxy no hacemos nada, osea tenemos que comprobar que el proxy que recibimos no es el nuestro (proxy_a_enviar) TAREA