# %%
import OpenOPC as OP
#import threading as th
import pywintypes
#import time
pywintypes.datetime=pywintypes.TimeType
import socket

# %% [markdown]
# ### Definicion de variables globales

# %%
opcserver = "ABB.AC800MC_OpcDaServer.3"

#lista de comandos:
#cerrar: finaliza el programa
close="5"
#iniciar: inicia la medicion
start= "1"
#detener: detiene la medicion
stop="2"
#Diccionario para mensajes luego de los comandos
comdic={start:"Interfaz iniciada", stop:"Interfaz detenida", close:"Cerrando programa"}
comando=stop
comprev=comando
variables=[]

# %% [markdown]
# Conecto con el servidor OPC

# %%
opc=OP.client()
#opc.connect('ABB.AC800MC_OpcDaServer.3')

# %% [markdown]
# ### Funciones
# 

# %%
#funcion que lee el OPC
def actualizar():
    opc.connect('ABB.AC800MC_OpcDaServer.3')
    vars=list(opc.read(["Applications.CAPEM.SC_TESTIGO.Value","Applications.CAPEM.SC_POS_Val.Value","Applications.CAPEM.SC_ERROR.Value",
                        "Applications.CAPEM.PT030_In.Value","Applications.CAPEM.LT035_mmH2O_GLOBAL.Value","Applications.CAPEM.TT024B_In.Value",
                        "Applications.CAPEM.TT024A_In.Value","Applications.CAPEM.TBCe_In.Value"]))
    vars2= [0]+list(map((lambda x: 1 if x[1]==True else (0 if x[1]==False else x[1])),vars))
    return vars2

# %% [markdown]
# ### Rutina principal

# %%
##### Thread 2, Busca comandos
#th2=th.Thread(target=comandos,name="th2")
#th2.start()
#th1=th.Thread(target=comandos,name="th1")
host="172.16.4.9"
port=9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", port))
    ## Loop principal
    while True:
        s.listen()
        conn, addr = s.accept()
        with conn:
            try:
                print(f"Connected by {addr}")
                while True:
                    datos=actualizar()
                    data = conn.recv(1024).decode("ascii")
                    if not data or data=="cerrar":
                        break
                    #print(data)
                    if data=="hs":
                        resp=b"hs"
                    elif 0<=int(data)<=1000 and datos!=None:
                        cn=int(data)
                        datos[0]=cn
                        #res=data+","+str(datos)
                        #print(res)
                        resp=str(datos).encode("ascii")
                    ##resp=str(actualizar()).encode("ascii")
                    #resp=responder(data) 
                    #resp=b'25.75,5.45,12.152,456,456.2,1,3215,123,123,123,515,15,681,6,313,6,5558, abcde,int32,mi vieja mula ya no es lo que era'
                    conn.sendall(resp)  
            except Exception as e:
                print(str(e))


