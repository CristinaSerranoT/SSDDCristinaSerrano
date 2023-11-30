#!/usr/bin/env python3
# -- coding: utf-8 --


import sys
import Ice
#Ice.loadSlice('icedrive.ice')

import IceDrive


def solicitar_operando(opName: str='') -> float:
    '''Solicitad un valor por stdin y lo convierte a flotante'''
    try: 
        return float(input(f'Operando {opName}: '))
    except ValueError as error:
        print(f'Not valid number: {error}')
        sys.exit()
    except KeyboardInterrupt:
        print('\nCancelado por el usuario')
        sys.exit()



class Client(Ice.Application):
    def run(self, args):

        #Creamos el proxy para el servicio de autenticacion y lo invocamos
        proxy = self.communicator().stringToProxy(args[1])
        servicioBlob = IceDrive.BlobServicePrx.checkedCast(proxy)
        
        #Aqui se pueden probar los metodos del proxy de BlobService que se han implementado en el servidor
    
        servicioBlob.link("/escritorio/hola.txt")
        
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