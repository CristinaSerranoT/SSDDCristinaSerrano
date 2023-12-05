#!/usr/bin/env python3
# -- coding: utf-8 --


import sys
import Ice
#Ice.loadSlice('icedrive.ice')

import IceDrive


class Client(Ice.Application):
    def run(self, args):

        #Creamos el proxy para el servicio de autenticacion y lo invocamos
        proxy = self.communicator().stringToProxy(args[1])
        servicioBlob = IceDrive.BlobServicePrx.checkedCast(proxy)
        
        #Aqui se pueden probar los metodos del proxy de BlobService que se han implementado en el servidor
    
        #servicioBlob.link("blob_id")
        servicioBlob.unlink("blob_id")
        
        #servicioBlob.upload(servicioBlob.blob_id)
        #servicioBlob.download(servicioBlob.blob_id)  
        
        #Comprobamos que el proxy es correcto
        
        if not servicioBlob:
            print("El proxy es incorrecto")
            sys.exit(1)
            
        while True:
            print("\nMenú:")
            print("1. Link Blob")
            print("2. Unlink Blob")
            print("3. Upload Blob")
            print("4. Download Blob")
            print("5. Salir")

            opcion = input("Seleccione una opción (1-5): ")

            if opcion == "1":
                blob_id = input("Ingrese el Blob ID para enlazar: ")
                servicioBlob.link(blob_id)
            elif opcion == "2":
                blob_id = input("Ingrese el Blob ID para desenlazar: ")
                servicioBlob.unlink(blob_id)
            elif opcion == "5":
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida. Intente de nuevo.")



def main():
    app = Client()
    app.main(sys.argv) 
    print("Bienvenido al cliente")