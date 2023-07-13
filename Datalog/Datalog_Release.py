# %%
import OpenOPC as OP
import pywintypes
pywintypes.datetime=pywintypes.TimeType #Se usa para OpenOPC o.o
from os.path import isfile
import threading
import csv
import datetime
import tkinter as tk
from tkinter import ttk,Canvas
import time
import os
#import numpy as np

# %% [markdown]
# ### Funciones
# 

# %%
#Funcion que se ejecuta cuando se da el boton INICIAR de hmi
#Cambia los colores y modifica la variable 'iniciar_log'
def iniciar():
    global iniciar_log
    if iniciar_log:
        iniciar_log=False
        HMI.btn_iniciar.config(text="INICIAR\nDATALOG",**neutro)
    else:
        iniciar_log=True
        HMI.btn_iniciar.config(text="DETENER\nDATALOG", **verde)

def abrircarpeta():
    os.system("explorer C:\\capem Python\Datalog\Mediciones")

# %%
#funcion que lee el OPC
def actualizar_log():
    #Conecto con el servidor de ABB...
    opc.connect('ABB.AC800MC_OpcDaServer.3')
    #...y traigo una lista de variables
    vars=list(opc.read(["Applications.CAPEM.LT035_mmH2O_GLOBAL.Value", "Applications.CAPEM.FT003_In.Value", "Applications.CAPEM.FT019_In.value",
                        "Applications.CAPEM.FT023_In.value", "Applications.CAPEM.PT030_In.value", "Applications.CAPEM.BI005a_Out.value",
                        "Applications.CAPEM.BI005b_Out.value", "Applications.CAPEM.BI005c_Out.value", "Applications.CAPEM.DPCV027_Out.value",
                        "Applications.CAPEM.DPT018_In.value", "Applications.CAPEM.DPT022_In.value", "Applications.CAPEM.DPT026_In.value",
                        "Applications.CAPEM.DPT027_In.value", "Applications.CAPEM.FV003_Out.value", "Applications.CAPEM.PT015_In.value",
                        "Applications.CAPEM.PT021_In.value", "Applications.CAPEM.TI024_In.value", "Applications.CAPEM.TT004_In.value",
                        "Applications.CAPEM.TT005_In.value", "Applications.CAPEM.TT016_In.value", "Applications.CAPEM.TT024A_In.value",
                        "Applications.CAPEM.TT024B_In.value", "Applications.CAPEM.TT061_In.value", "Applications.CAPEM.TT062_In.value",
                        "Applications.CAPEM.TT063_In.value", "Applications.CAPEM.ZI033_In.value", "Applications.CAPEM.DTIC024_Out.value",
                        "Applications.CAPEM.FT003_In_m3h.value", "Applications.CAPEM.DPT012_In.value", "Applications.CAPEM.FT019_In_m3h.value",
                        "Applications.CAPEM.PI001_In.value", "Applications.CAPEM.DPT110_corr.value", "Applications.CAPEM.DPT111_corr.value",
                        "Applications.CAPEM.SistemaGP.VG002_SP", "Applications.CAPEM.VG002_In_reg.value", "Applications.CAPEM.SistemaGP.VA003_SP",
                        "Applications.CAPEM.VA003_In_reg.value", "Applications.CAPEM.SistemaGP.VA004_SP", "Applications.CAPEM.VA004_In_reg.value",
                        "Applications.CAPEM.SC_POS_reg.value", "Applications.CAPEM.SC_TESTIGO_reg.value", "Applications.CAPEM.VT107_In.value",
                        "Applications.CAPEM.JT108_In.value", "Applications.CAPEM.TT105_In.value", "Applications.CAPEM.PT106_In.value",
                        "Applications.CAPEM.PT103_In.value", "Applications.CAPEM.FT104_In.value", "Applications.CAPEM.TBCe_In.value",
                        "Applications.CAPEM.FV067_Out.value", "Applications.CAPEM.TT101_In.value", "Applications.CAPEM.FT023_In_m3h.value",
                        "Applications.CAPEM.SistemaGP.MSAC_1.APsubida","Applications.CAPEM.SistemaGP.MSAC_1.APbajada",
                        "Applications.CAPEM.SistemaGP.MSAC_1.PTsubida","Applications.CAPEM.SistemaGP.MSAC_1.PTbajada"]))
    
    #Extraigo solamente los valores de los datos traidos
    vars2= list(map((lambda x: x[1]),vars))
    return vars2

# %%
#Clase donde se programa la HMI
#Se crea a partir de Thread para que se ejecute en un hilo aparte
class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #self.daemon=True
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        #VENTANA PRINCIPAL
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title("LOG CAPEM")
        self.root.config(width=250, height=200,bg='#f5f5f5')
        #self.canvas=Canvas(self.root,width=549, height=375)

        #BOTONES
        self.btn_iniciar= tk.Button(text="INICIAR\nDATALOG", command=iniciar,relief="groove", activebackground='#9ACBFB', **neutro, state=tk.DISABLED)
        self.btn_iniciar.place(x=20, y=100,width=100, height=60)

        self.btn_abrir= tk.Button(text="ABRIR\nCARPETA", command=abrircarpeta,relief="groove", activebackground='#9ACBFB', **neutro)
        self.btn_abrir.place(x=120, y=100,width=100, height=60)

        #LABELS
         
        self.lbl_gral1=ttk.Label(text="...", padding=2, relief="groove",borderwidth=1,width=34,**neutro)
        self.lbl_gral1.place(x=3, y=175)  
        

        #ENTRADAS DE TEXTO
        self.lbl_etiqueta=ttk.Label(text="Nombre de archivo:", relief='flat', **neutro)
        self.lbl_etiqueta.place(x=3, y=3)

        self.entrada=ttk.Entry()
        self.entrada.place(x=3, y=23,width=244, height=20)

        self.lbl_delay=ttk.Label(text="Tiempo agregado [ms]:", relief='flat', **neutro)
        self.lbl_delay.place(x=3, y=50) 

        self.time=ttk.Entry()
        self.time.place(x=171, y=50,width=76, height=20)
    
        self.root.mainloop()
    

# %% [markdown]
# ### Definicion de variables globales

# %%
#Header del excel
encabezado=["Fecha", "Hora", "LT035_mmH2O", "FT003_In", "FT019_In", "FT023_In", "PT030_In", "BI005a_Out", "BI005b_Out", "BI005c_Out", "DPCV027_Out",
            "DPT018_In", "DPT022_In", "DPT026_In","DPT027_In", "FV003_Out", "PT015_In", "PT021_In", "TI024_In", "TT004_In","TT005_In", "TT016_In",
            "TT024A_In","TT024B_In", "TT061_In", "TT062_In", "TT063_In", "ZI033_In", "DTIC024_Out","FT003_In_m3h", "DPT012_In", "FT019_In_m3h",
            "PI001_In", "DPT110_corr", "DPT111_corr", "VG002_SP", "VG002_In_reg", "VA003_SP","VA003_In_reg", "VA004_SP", "VA004_In_reg","SC_POS_reg",
            "SC_TESTIGO_reg", "VT107_In","JT108_In", "TT105_In", "PT106_In", "PT103_In", "FT104_In", "TBCe_In","FV067_Out", "TT101_In", "FT023_In_m3h",
            "APsubida_ms","APbajada_ms","PTsubida_ms","PTbajada_ms"]

#Colores para HMI
verde={'background':'#4BF24B', 'foreground':'black','font':("Arial",9,'bold')}
neutro={'background':'#f0f0f0', 'foreground':'black','font':("Arial",9)}

#Variable que inicia el guardado de datos (se activa con la funcion iniciar ligada al boton)
iniciar_log=False

#Defino el objeto servidor OPC
opc=OP.client()
opcserver = "ABB.AC800MC_OpcDaServer.3"

# %%
#Se crea el objeto HMI (crea y ejecuta la clase creada mas arriba)
HMI = App()
time.sleep(2)

# %%
#Mientras no se cierre la HMI...
while HMI.is_alive():
    try:
        #Una vez que se le da iniciar desde el boton, se abre el archivo CSV para ir guardando datos
        if iniciar_log:
            HMI.lbl_gral1.config(text='LOG INICIADO')
            archivocsv=open(archivo, mode='a', newline='',)
            writer = csv.writer(archivocsv, delimiter=",")

            if not aux:
                #Si no existe existia el archivo, lo primero que hace es escribir el headeer
                writer.writerow(encabezado)
                
            while True:
                tmp=(HMI.time.get())    #Entrada de tiempo agregado desde HMI
                if tmp=='':
                    tmp='0'
                tiempo=int(tmp)/1000
                
                try:
                    #Lee datos de OPC y agrega fecha y hora al principio
                    datos_guardar=[str(datetime.datetime.now().date()),str(datetime.datetime.now().time())]+ actualizar_log()
                    writer.writerow(datos_guardar)

                    if not iniciar_log or not HMI.is_alive():
                        #Cuando se desactiva la orden de realizar log, cierra el archivo y sale del segundo while
                        archivocsv.close()
                        HMI.lbl_gral1.config(text='LOG DETENIDO')
                        break
                    time.sleep(tiempo)
                except:
                    break
            
        else:
            #Si no esta con la orden de medir, va generando el nombre del archivo y chequeando si existe
            archivo=f'Mediciones\{HMI.entrada.get()}.csv'
            aux=isfile(archivo)
            if archivo=='Mediciones\.csv': #Esto se hace para que se ponga un nombre de archivo, si no tiene nada deshabilita el boton
                HMI.btn_iniciar.config(state=tk.DISABLED)
            else:
                HMI.btn_iniciar.config(state=tk.NORMAL)
    except Exception as e:
        #Si se llega a generar algun error (el try no se puede completar), se muestra en la HMI y se detiene el guardado de datos
        HMI.lbl_gral1.config(text=str(e))
        iniciar_log=False
    


