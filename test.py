# %%
import tkinter as tk
from tkinter import ttk, Canvas
import time
import funciones as fn
import threading

# %%
def conectar():
    """Gestiona la conexión con el servidor y los estados"""
    global estados, cn
    txt=app.btn_conectar['text']
    if txt=='CONECTAR SRV':
        try:
            srv.conectar(host="192.168.99.10", port=9999)
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
        except:
            srv.status="Desconectado con error"
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
    


def configurar():
    global estados, ctf, ifa, ra, configuracion
    dic={True:"OK", False: "NO OK"}
    ac=fn.configurar()
    configuracion=ac.cargarconfig("configuracion/config.txt")
    estados['config']=f"Frecuencias {dic[configuracion['okfrec']]}, repeticiones {dic[configuracion['okrep']]}"
    app.lbl_stsconf.config(text=estados['config'])
    ctf=configuracion['frecuencias'].count()
    ifa=0
    ra=0
    app.lbl.config(text=f"cf={str(configuracion['frecuencias'])}, rep= {str(configuracion['repeticiones'])}")

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
        self.root.config(width=320, height=380)

        self.lbl_comandos = ttk.Label(text="COMANDOS:",font=("Arial", 13))
        self.lbl_comandos.place(x=20, y=20)

        #BOTONES
        self.btn_configurar= ttk.Button(text="CONFIGURAR", command=configurar)
        self.btn_configurar.place(x=20, y=50,width=100, height=30)

        self.btn_conectar= ttk.Button(text="CONECTAR SRV", command=conectar)
        self.btn_conectar.place(x=20, y=80,width=100, height=30)

        self.btn_inicializar= ttk.Button(text="INICIALIZAR LCR", command=conectar)
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
        

        self.canvas=Canvas(width=145, height=145)
        self.canvas.configure(background="gray")
        self.canvas.pack()
        self.canvas.place(x=155, y=50)
        #self.canvas.create_oval(0,0,80,80,width=2, fill="gray")

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
ctf=0                   #cantidad de frecuencias totales en la config
ifa=0                   #Indice de frecuencia actual
ra=0                    #repeticion actual


estados=dict(srvcon="Desconectado",sercon="Desconectado", config="Sin configurar", medicion="Detenido")

# %%
app = App()

# %%
while app.is_alive():       #Se finaliza cuando la interfaz se cierra
    if flag_medIni:         #Iniciar medición desde HMI (A)
        cn+=1               #mando un numero de confirmación para que lo devuelva y saber si el valor devuelto es actual
        if cn>999: cn=0
        dts=srv.enviar(str(cn))                 #Me devuelve los datos solicitados
        datos=list(dts[1:-1].split(sep=","))    #Hago un arreglo para quitarle los corchetes de la lista
        
        for n,x in enumerate(dts):             #y los convierto en numeros 
            if n!=0:                           #el primero queda entero porque lo comparo con cn
                datos[n]=float(x)
            else:
                datos[n]=int(x)
    
        #Analizo el dato de posición traido de OPC. Si está en posición, se activa un flag (B)
        if datos[1]==1:         #El bit de posición tiene que estar en el lugar 1 de la lista enviada
            flag_posOK=True
        else:
            flag_posOK=False
        
        #Comparo el numero de confirmación para chequear comunicacion (C)
        if datos[0]==cn and datos[0]>0:        #Activa el flag comOK si esta todo OK
            flag_comOK=True
            app.lbl_stssrv.config(text="Conectado")
        else:
            flag_comOK=False    #Si no lo desactiva y deja un mensaje en HMI
            app.lbl_stssrv.config(text="Error de datos")
            app.lbl_gral.config(text="Error de datos")
        

        #Chequeo cuándo se cumplen las n repeticiones de los barridos de frecuencia (D)
        if ra>=configuracion['repeticiones']:
            flag_cicloFin=True
        

        # Chequeo que se den las condiciones para medir (A=1, B=1 ,C=1 y D=0)
        if flag_posOK and flag_comOK and not flag_cicloFin:
            #Si se cumplen las condiciones, empiezo a medir
            LCR.cambiarfreq(configuracion['frecuencias'][ifa])
            





        if dts[0]==1:
            app.canvas.config(background="red")
        else:
            app.canvas.config(background="green")
        
        print(estados['srvcon'])
    else:
        app.canvas.config(background="gray")

        
input()

