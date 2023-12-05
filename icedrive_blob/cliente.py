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
    
        servicioBlob.link("link")
        servicioBlob.unlink("cris")
        
        #servicioBlob.upload(servicioBlob.blob_id)
        #servicioBlob.download(servicioBlob.blob_id)  
        
        #Comprobamos que el proxy es correcto
        
        if not servicioBlob:
            print("El proxy es incorrecto")
            sys.exit(1)
        
        #num1 = solicitar_operando('1')
        #num2 = solicitar_operando('2')
        #print(f'La suma de ambos es: {cliente.div(num1, num2)}')


def main():
    app = Client()
    app.main(sys.argv) 
    print("Bienvenido al cliente")