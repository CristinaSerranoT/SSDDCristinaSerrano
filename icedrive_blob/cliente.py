#!/usr/bin/env python3
# -- coding: utf-8 --

import sys
import Ice
#Ice.loadSlice('icedrive.ice')

import IceDrive

import os

from .blob import DataTransfer



class Client(Ice.Application):
    def run(self, args):

        #Creamos el proxy para el servicio de autenticacion y lo invocamos
        proxy = self.communicator().stringToProxy(args[1])
        servicioBlob = IceDrive.BlobServicePrx.checkedCast(proxy)
        
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
            elif opcion == "3":
                try:
                    file_path = input("Ingrese la ruta del archivo para subir como Blob: ")
                    # Verificar si el archivo existe
                    if os.path.exists(file_path):
                        # Crear un proxy para el objeto DataTransfer y registrarlo con el adaptador
                        adapter = self.communicator().createObjectAdapterWithEndpoints(file_path, "tcp")

                        servant = DataTransfer(file_path)
                        print(f"Objeto DataTransfer creado correctamente. Ruta del archivo: {file_path}")

                        proxy = adapter.addWithUUID(servant)
                        data_transfer_proxy = IceDrive.DataTransferPrx.checkedCast(proxy)
                        print(f"Objeto DataTransferProxy antes de llamar a upload: {data_transfer_proxy}")

                        # Iniciar la comunicación del adaptador
                        adapter.activate()

                        # Utilizar el proxy para enviar los datos al servicio
                        with open(file_path, "rb") as file:
                            blob_id = servicioBlob.upload(data_transfer_proxy)
                            print(f"Blob subido con éxito. ID: {blob_id}")
                            #Todo objeto DataTransfer() debe ser destruido después de que se haya completado la transferencia de datos.
                            adapter.destroy() 
                    else:
                        raise FileNotFoundError(file_path)
                except Exception as e:
                    print(f"Error al subir el archivo: {e}")
            elif opcion == "4":
                try:
                    blob_id = input("Ingrese el Blob ID para descargar: ")
                    # Descargar el blob utilizando el servicioBlob
                    data_transfer_proxy = servicioBlob.download(blob_id)

                    # Utilizar el proxy para recibir los datos del servicio y guardarlos en un archivo local
                    with open(f"download_{blob_id}.txt", "wb") as file:
                        while True:
                            data = data_transfer_proxy.read(1024)
                            if not data:
                                break
                            file.write(data)
                    print(f"Blob descargado con éxito. Se ha guardado como download_{blob_id}.txt")
                except Exception as e:
                    print(f"Error al descargar el archivo: {e}")

            elif opcion == "5":
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida. Intente de nuevo.")



def main():
    app = Client()
    app.main(sys.argv) 
    #print("Bienvenido al cliente")

if __name__ == "__main__":
    main()