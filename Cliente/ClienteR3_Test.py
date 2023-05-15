# %%
import tkinter as tk
from tkinter import ttk, Canvas
import time
import funciones as fn
import threading
from os.path import isfile
import csv
import datetime

# %%
def conectar():
    """Gestiona la conexión con el servidor y los estados"""
    global estados, cn
    txt=app.btn_conectar['text']
    if txt=='CONECTAR SRV':
        try:
            srv.conectar(host="172.16.4.2", port=9999)
            hs=""
            hs=srv.enviar("hs")
            if hs=="hs":
                #app.lbl_sts.config(text="Conectado con servidor")
                srv.status="Conectado"
                #app.lbl_stssrv.config(text="Conectado")
                app.btn_conectar['text']="DESCONECTAR SRV"
            else:
                srv.status="Error"
                #app.lbl_stssrv.config(text="Error")
        except Exception as e:
            srv.status=f"Desconectado con error {e}"
            #app.lbl_stssrv.config(text="Desconectado con error")
    else:
        srv.cerrar()
        srv.status="Desconectado"
        app.btn_conectar['text']="CONECTAR SRV"
        cn=0
    estados['srvcon']=srv.status
    app.lbl_stssrv.config(text=srv.status)
    
def inicializar():
    global LCR
    LCR.inicializar('COM3', 19200, 8, 'N', 1)
    LCR.inicializado=True
    


def configurar():
    global estados, tfrec, ifrec, repeticion, configuracion
    dic={True:"OK", False: "NO OK"}
    ac=fn.configurar()
    configuracion=ac.cargarconfig("configuracion/config.txt")
    estados['config']=f"Frec: {dic[configuracion['okfrec']]}, rep: {dic[configuracion['okrep']]}"
    app.lbl_stsconf.config(text=estados['config'])
    app.lbl_gral.config(text=str(configuracion))
    tfrec=len(configuracion['frecuencias'])
    ifrec=0
    repeticion=0
    

def inimed():
    "Inicia la medicion"
    global flag_medIni
    flag_medIni=True
    app.lbl_stsmed.config(text="Medición iniciada")

def detener():
    "Detiene la medicion"
    global flag_medIni
    flag_medIni=False
    app.lbl_stsmed.config(text="Medición detenida")    

#funcion para guardar una fila en csv.
#si el archivo no existe, te lo crea
def escribir_csv(archivo:str, datos:list, encabezado:list):
    """
    Abre un archivo CSV en modo 'append', por lo que agrega una nueva fila.
    archivo     -> string. Formato 'carpeta\\archivo.csv' ('Mediciones\probando.csv')
    fila        -> lista con los valores a guardar
    encabezado  -> Lista con los textos de los encabezados
    """

    aux=isfile(archivo)
    
    with open(archivo, mode='a', newline='',) as archivo_csv:
        writer = csv.writer(archivo_csv, delimiter=";")
        if not aux:
            writer.writerow(encabezado)
        writer.writerow(datos)
        
    archivo_csv.close()

# %%
class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #self.daemon=True
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title("ADQUISIDOR CAPEM")
        self.root.config(width=500, height=380)

        self.lbl_comandos = ttk.Label(text="COMANDOS:",font=("Arial", 13))
        self.lbl_comandos.place(x=20, y=20)

        #BOTONES
        self.btn_configurar= ttk.Button(text="CONFIGURAR", command=configurar)
        self.btn_configurar.place(x=20, y=50,width=100, height=30)

        self.btn_conectar= ttk.Button(text="CONECTAR SRV", command=conectar)
        self.btn_conectar.place(x=20, y=80,width=100, height=30)

        self.btn_inicializar= ttk.Button(text="INICIALIZAR LCR", command=inicializar)
        self.btn_inicializar.place(x=20, y=110,width=100, height=30)

        self.btn_medir= ttk.Button(text="MEDIR", command=inimed)
        self.btn_medir.place(x=20, y=140,width=100, height=30)

        self.btn_detener= ttk.Button(text="DETENER", command=detener)
        self.btn_detener.place(x=20, y=170,width=100, height=30)

        #ETIQUETAS FIJAS DE ESTADO
        self.lbl_comandos = ttk.Label(text="ESTADOS:",font=("Arial",13))
        self.lbl_comandos.place(x=20, y=240)

        self.lbl_sts_srv=ttk.Label(text="Servidor:")
        self.lbl_sts_srv.place(x=20, y=265)

        self.lbl_sts_serie=ttk.Label(text="Instrumento:")
        self.lbl_sts_serie.place(x=20, y=285)

        self.lbl_sts_conf=ttk.Label(text="Configuracion:")
        self.lbl_sts_conf.place(x=20, y=305)

        self.lbl_sts_med=ttk.Label(text="Medición:")
        self.lbl_sts_med.place(x=20, y=325)

        #ETIQUETAS variables DE ESTADO
        self.lbl_stssrv=ttk.Label(text="Desconectado")
        self.lbl_stssrv.place(x=130, y=265)

        self.lbl_stsserie=ttk.Label(text="Desconectado")
        self.lbl_stsserie.place(x=130, y=285)

        self.lbl_stsconf=ttk.Label(text="Sin configurar")
        self.lbl_stsconf.place(x=130, y=305)

        self.lbl_stsmed=ttk.Label(text="Detenida")
        self.lbl_stsmed.place(x=130, y=325)

        self.lbl_gral=ttk.Label(text="...", relief="ridge",width=100)
        self.lbl_gral.place(x=0, y=360)
        

        #Etiquetas con valores para PEM
        self.lbl_enpos_=ttk.Label(text="En posición:")
        self.lbl_enpos_.place(x=300, y=265) 

        self.lbl_enpos=ttk.Label(text="--")
        self.lbl_enpos.place(x=380, y=265)        

        self.lbl_pos_=ttk.Label(text="Posición:")
        self.lbl_pos_.place(x=300, y=285) 

        self.lbl_pos=ttk.Label(text="--")
        self.lbl_pos.place(x=380, y=285) 


        self.canvas=Canvas(width=145, height=145)
        self.canvas.configure(background="gray")
        self.canvas.pack()
        self.canvas.place(x=155, y=50)
      

        self.root.mainloop()
    
    

# %%
flag_medIni=False       #Flag para iniciar medicion desde HMI (A)
flag_posOK=False        #Flag para indicar que la posicion está OK (B). Se actualiza mediante OPC
flag_comOK= False       #Flag que indic que la comunicación es actual y está OK (C)
flag_cicloFin=False     #Flag para indicar cuándo finalizó las n repeticiones con todas las frecuencias

configuracion={}        #en este diccinario se cargan las configuraciones. Las claves son:
                        #'frecuencias' (lista), 'repeticiones' (int), 'okfrec' (bool) y 'okr' (bool)

srv=fn.conexionsrv()    #Genero el objeto servidor, que tiene todas las funciones para conectarse
#stsprev=srv.status
cn=0                    #cn es el numero de control que se usa para chequear que la info leida es la correcta 
LCR=fn.LCR()

#Variables que se van actualizando con los barridos de frecuencia
tfrec=0                 #cantidad de frecuencias totales en la config
ifrec=0                 #Indice de frecuencia actual
repeticion=0            #repeticion actual
filtroPos01=0           #Fitro para determinar el cambio de posicion OK a no OK
filtroPos10=0           #Fitro para determinar el cambio de posicion no OK a OK

estados=dict(srvcon="Desconectado",sercon="Desconectado", 
             config="Sin configurar", medicion="Detenido")

encabezado=['Repetición', 'Frecuencia','Posicion', 'Temperatura1', 'Temperatura2', 'Temperatura3',
                        'Inductancia', 'Resistencia', 'Dia', 'Hora']

datos_guardar=[]

# %%
app = App()

# %%
time.sleep(3)
while app.is_alive():       #Se finaliza cuando la interfaz se cierra
    if flag_medIni:         #Iniciar medición desde HMI (A)

        #if not LCR.inicializado or srv.status

        #Pido datos a OPC:
        cn+=1               #mando un numero de confirmación para que lo devuelva y saber si el valor devuelto es actual
        if cn>999: cn=0
        dts=srv.enviar(str(cn))                     #Me devuelve los datos solicitados
        datosOPC=list(dts[1:-1].split(sep=","))     #Hago un arreglo para quitarle los corchetes de la lista
        for n,x in enumerate(datosOPC):             #y los convierto en numeros 
            if n>1:                           
                datosOPC[n]=float(x)
                
            else:
                datosOPC[n]=int(x)             #el primero queda entero porque lo comparo con cn

        
        #Escribo los vlaores para mostrar
        app.lbl_enpos.config(text=datosOPC[1])
        app.lbl_pos.config(text=datosOPC[2])
        



        app.lbl_gral.config(text=f'OPC: {datosOPC}   Guardados:{datos_guardar}')    
        if datosOPC[1]==1.0:
            app.canvas.config(background="red")
        else:
            app.canvas.config(background="green")
        
    else:
        app.canvas.config(background="gray")

#Cuando cierra la aplicacion, manda el comando de cerrar el servidor para que no de problemas
srv.cerrar()
        


