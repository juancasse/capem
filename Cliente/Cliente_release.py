# %%
import tkinter as tk
from tkinter import ttk,Canvas
import time
import funciones as fn
import threading
from os.path import isfile
import csv
import datetime
Revision='Capem_Cliente_R4.ipynb'

# %%
#Funciones
def conectarsrv():
    '''Gestiona la conexión con el servidor y los estados'''
    global estados, cn, tempcolor
    txt=app.btn_conectar_srv['text']
    app.lbl_gral2.config(text='...', **neutro)
    if txt=='CONECTAR\nSERVIDOR':
        try:
            #srv.conectar(host="172.16.4.2", port=9999)
            srv.conectar(host="192.168.99.10", port=9999)
            hs=""
            hs=srv.enviar("hs")
            if hs=="hs":
                tempcolor=green
                srv.status="Conectado"
                app.btn_conectar_srv.config(text='SERVER\nCONECTADO', **verde)
                app.lbl_gral1.config(text='Conexión con servidor OK', **neutro)
                
            else:
                tempcolor='red'
                srv.status="Error"
                app.lbl_gral1.config(text=f'Error de conexión: {hs}', **neutro)
                app.btn_conectar_srv.config(text='CONECTAR\nSERVIDOR', **rojo)
        except Exception as e:
            tempcolor='red'
            srv.status="Error de conexión"
            app.lbl_gral1.config(text=str(e), **neutro)
            app.btn_conectar_srv.config(text='CONECTAR\nSERVIDOR', **rojo)
    else:
        tempcolor=standar
        srv.cerrar()
        srv.status='Desconectado'
        app.btn_conectar_srv.config(text='CONECTAR\nSERVIDOR', **neutro)
        cn=0
    estados['srvcon']=srv.status
    
def conectarlcr():
    app.lbl_gral2.config(text='...', **neutro)
    txt=app.btn_conectar_LCR['text']
    global LCR,tempcolor,flag_lcrOK
    if txt == "CONECTAR\nLCR":
        sts=LCR.LCR_inicializar('ON',port='COM6', baudrate=38400, bytesize=8, parity='N', stopbits=1, timeout=5)
        if sts=='inicializado':
            tempcolor=green
            LCR.inicializado=True
            estados['sercon']='Conectado'
            app.btn_conectar_LCR.config(text='LCR\nCONECTADO', **verde)
            app.lbl_gral1.config(text='Conexión con LCR OK', **neutro)
            flag_lcrOK=True
        else:
            tempcolor='red'
            estados['sercon']='Error'
            app.btn_conectar_LCR.config(text='CONECTAR\nLCR', **rojo)
            app.lbl_gral1.config(text=sts, **neutro)
            flag_lcrOK=False
    else:
        LCR.LCR_inicializar('OFF')
        tempcolor=standar
        LCR.inicializado=False
        estados['sercon']='Desconectado'
        app.btn_conectar_LCR.config(text='CONECTAR\nLCR', **neutro)
        app.lbl_gral1.config(text='LCR Desconectado', **neutro)
        flag_lcrOK=False


def configurar():
    app.lbl_gral2.config(text='...', **neutro)
    global estados, tfrec, ifrec, repeticion, frecuencias, repeticiones, tempcolor, archivo, comentario
    dic={True:"OK", False: "NO OK"}
    ac=fn.configurar()
    archivo, comentario, frecuencias,repeticiones,cnferror=ac.cargarconfig(r"E:\Proyectos Python\capem\Cliente\configuracion\configuracion.txt")
    if cnferror=='no':
        tempcolor=green
        estados['config']='Configurado'
        app.lbl_gral1.config(text=f'frecuencias:  {frecuencias}  |  repeticiones:  {repeticiones}  |  archivo:  {archivo}', **neutro)
        app.btn_configurar.config(**verde)
    else:
        tempcolor='red'
        estados['config']='Error'
        app.lbl_gral1.config(text=str(cnferror), **rojo)
        app.btn_configurar.config(**rojo)
    
    tfrec=len(frecuencias)
    ifrec=0
    repeticion=0
    
    

def inimed():
    "Inicia y detiene la medicion"
    global flag_medIni
    app.lbl_gral2.config(text='...', **neutro)
    
    txt=app.btn_medir['text']
    if txt == "INICIAR\nMEDICIÓN":
        res=LCR.LCR_Configurar()
        print(res)
        if 'Error' in res:
            app.lbl_gral2.config(text=res, **rojo)
            return
        estados['medicion']='Iniciada'
        flag_medIni=True
        app.btn_medir.config(text='MEDICIÓN\nEN PROCESO', **verde)
    else:
        estados['medicion']='Detenida'
        flag_medIni=False
        app.btn_medir.config(text='INICIAR\nMEDICIÓN', **neutro)
  

#funcion para guardar una fila en csv.
#si el archivo no existe, te lo crea
def escribir_csv(archivo:str, datos:list, encabezado:list, com):
    """
    Abre un archivo CSV en modo 'append', por lo que agrega una nueva fila.
    archivo     -> string. Formato 'carpeta\\archivo.csv' ('Mediciones\probando.csv')
    fila        -> lista con los valores a guardar
    encabezado  -> Lista con los textos de los encabezados
    com         -> Comentario en forma de lista
    """
    global flag_insertarheader
    
    with open(archivo, mode='a', newline='',) as archivo_csv:
        writer = csv.writer(archivo_csv, delimiter=";")
        fecha=[str(datetime.datetime.now().date()), str(datetime.datetime.now().time())]
        if flag_insertarheader:
            l1=['Dia:',str(datetime.datetime.now().date()),'Hora:',str(datetime.datetime.now().time())]
            l2=['Repeticiones:', str(repeticiones), 'Frecuencias:', str(frecuencias)]
            l3=['Revision:',Revision]
            l4=['Comentarios:']
            writer.writerow('')
            writer.writerow(l1)
            writer.writerow(l2)
            writer.writerow(l3)
            writer.writerow('')
            writer.writerow(l4)
            for l in com:
                writer.writerow(list(l))
            writer.writerow('')
            writer.writerow(encabezado)
            flag_insertarheader=False
        writer.writerow(datos)
        
    archivo_csv.close()


def medindiv():
    'Lee una vez las mediciones'
    res=LCR.LCR_medir()
    if len(res)>=4:
        app.lbl_1.config(text=f'L: {res[0]} {res[1]}')
        app.lbl_2.config(text=f'R: {res[2]} {res[3]}')
        
def cmd_lcr():
    from time import sleep
    LCR.escribir(app.entrada.get())
    sleep(0.5)
    res=LCR.leer('RL')
    app.lbl_respuesta.config(text=res)
    

# %%
#Funcion para escribir el estado
def informacion():
    resultado=''
    if flag_medIni:
        if flag_posOK:
            if flag_cicloFin: resultado='Esperando nueva posición'
            else: resultado='Medición en proceso'
        else: resultado='Buscando nueva posición'
    else:
        if estados['config']=='Configurado':
            if estados['srvcon']=='Conectado':
                if estados['sercon']=='Conectado': resultado='Listo para comenzar a medir'
                else: resultado='El equipo serie se encuentra desconectado'
            else: resultado='El servidor se encuentra desconectado'
        else: resultado='Falta cargar configuración'
    app.lbl_gral2.config(text=resultado, **neutro)

        


# %%
class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #self.daemon=True
        self.start()

    def callback(self):
        self.root.quit()

    def btn_enter(self,event):
        global tempcolor
        tempcolor=event.widget['bg']
        if event.widget['state'] != tk.DISABLED:
            event.widget.config(bg=blue)
        else:
            pass

    def btn_leave(self,event):
        global tempcolor
        event.widget.config(bg=tempcolor)

    def popup(self):
        if self.root['width']==800:
            self.root.config(width=549)
            self.canvas.configure(width=549)
            self.btn_info.config(text='>>')
        else:
            self.root.config(width=800)
            self.canvas.configure(width=800)
            self.btn_info.config(text='<<')

    def run(self):

        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.title("ADQUISIDOR CAPEM")
        self.root.config(width=549, height=375,bg='#f5f5f5')
        self.canvas=Canvas(self.root,width=549, height=375)

        #BOTONES
        self.btn_configurar= tk.Button(text="CARGAR\nCONFIGURACION", command=configurar,relief="groove", activebackground='#9ACBFB', **neutro)
        self.btn_configurar.place(x=20, y=30,width=110, height=40)
        self.btn_configurar.bind('<Enter>',self.btn_enter)
        self.btn_configurar.bind('<Leave>',self.btn_leave)

        self.btn_conectar_srv= tk.Button(text="CONECTAR\nSERVIDOR", command=conectarsrv,relief="groove", **neutro)
        self.btn_conectar_srv.place(x=20, y=70,width=110, height=40)
        self.btn_conectar_srv.bind('<Enter>',self.btn_enter)
        self.btn_conectar_srv.bind('<Leave>',self.btn_leave)

        self.btn_conectar_LCR= tk.Button(text="CONECTAR\nLCR", command=conectarlcr,relief="groove", **neutro)
        self.btn_conectar_LCR.place(x=20, y=110,width=110, height=40)
        self.btn_conectar_LCR.bind('<Enter>',self.btn_enter)
        self.btn_conectar_LCR.bind('<Leave>',self.btn_leave)

        self.btn_medir= tk.Button(text="INICIAR\nMEDICIÓN", command=inimed, relief="groove", **neutro, state=tk.DISABLED)
        self.btn_medir.place(x=20, y=210,width=110, height=90)
        self.btn_medir.bind('<Enter>',self.btn_enter)
        self.btn_medir.bind('<Leave>',self.btn_leave)
        
        self.btn_info= tk.Button(text='>>', command=self.popup,relief="flat", overrelief="groove",borderwidth=2, background='#E8E8E8', foreground='black',font=("Arial",9))
        self.btn_info.place(x=495, y=30,width=50, height=50)

        #SEMAFORO

        self.btn_SEMAFORO= tk.Button(text="EN\nCONFIGURACIÓN", command=informacion, relief="flat", bg=gray, fg='black' ,font=("Arial",13, 'bold'))
        self.btn_SEMAFORO.place(x=200, y=30,width=270, height=270)


        #ETIQUETAS DE INFO
        self.lbl_gral1=ttk.Label(text="...", padding=2, relief="groove",borderwidth=1,width=77,**neutro)
        self.lbl_gral1.place(x=3, y=334)      

        self.lbl_gral2=ttk.Label(text="...", padding=2, relief="groove",borderwidth=1,width=77,**neutro)
        self.lbl_gral2.place(x=3, y=355)  

        #Info adicional
        self.lbl_1=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_1.place(x=557, y=20)
        self.lbl_2=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_2.place(x=557, y=45)
        self.lbl_3=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_3.place(x=557, y=70)
        self.lbl_4=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_4.place(x=557, y=95)
        self.lbl_5=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_5.place(x=557, y=120)
        self.lbl_6=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_6.place(x=557, y=145)
        self.lbl_7=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_7.place(x=557, y=170)
        self.lbl_8=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_8.place(x=557, y=195)

        global cmd_manual
        self.entrada=ttk.Entry()
        self.entrada.place(x=557, y=220,width=180, height=20)
        cmd_manual=self.entrada.get()
        
        self.lbl_respuesta=ttk.Label(relief="sunken",width=25,**neutro)
        self.lbl_respuesta.place(x=557, y=245)

        self.btn_cmd_manual=tk.Button(text="ENVIAR", command=cmd_lcr, relief="groove", **neutro)
        self.btn_cmd_manual.place(x=557, y=300,width=100, height=30)

        #self.btn_medirindiv= tk.Button(text="UN DISPARO", command=medindiv, relief="groove", **neutro)
        #self.btn_medirindiv.place(x=557, y=220,width=100, height=40)


        self.canvas.create_line(552,20,552,380)
        self.canvas.pack(expand=tk.YES)

        self.root.mainloop()
    
    

# %%
flag_medIni=False       #Flag para iniciar medicion desde HMI (A)
flag_posOK=False        #Flag para indicar que la posicion está OK (B). Se actualiza mediante OPC
flag_comOK= False       #Flag que indic que la comunicación es actual y está OK (C)
flag_cicloFin=False     #Flag para indicar cuándo finalizó las n repeticiones con todas las frecuencias
flag_lcrOK=False        #Flag que indic que la comunicación con el LCR esta OK

frecuencias=[]          #En esta lista se cargan las frecuencias.
repeticiones=0          #Se carga el numero de repeticiones

srv=fn.conexionsrv()    #Genero el objeto servidor, que tiene todas las funciones para conectarse
cn=0                    #cn es el numero de control que se usa para chequear que la info leida  de srv es la correcta 
LCR=fn.LCR()            #creo el objeto lcr

#Variables que se van actualizando con los barridos de frecuencia
tfrec=0                 #cantidad de frecuencias totales en la config
ifrec=0                 #Indice de frecuencia actual
repeticion=0            #repeticion actual
filtroPos01=0           #Fitro para determinar el cambio de posicion OK a no OK
filtroPos10=0           #Fitro para determinar el cambio de posicion no OK a OK

estados=dict(srvcon="Desconectado",sercon="Desconectado",   #diccionario  para indicar los estados de las conexiones y funciones
             config="Sin configurar", medicion="Detenido")

encabezado=['Repeticion', 'Frecuencia_Hz','En posicion','Posicion_mm', 'Error SC', 'Presion_bar', 'Nivel agua_mmh2o', 
            'T recipiente_C', 'T subenfriada_C', 'T Estimada_C', 'Inductancia','Unidad', 'Resistencia', 'Unidad', 'Dia', 'Hora']

datos_guardar=[]
cmd_manual=''

#Diccionarios creados para dar estilos a los labels
verde={'background':'#4BF24B', 'foreground':'black','font':("Arial",9,'bold')}
rojo={'background':'red', 'foreground':'white','font':("Arial",9,'bold')}
amarillo={'background':'#ffe000', 'foreground':'black','font':("Arial",9,'bold')}
neutro={'background':'#f0f0f0', 'foreground':'black','font':("Arial",9)}
standar='#f0f0f0'
green="#4BF24B"
yellow='#ffe000'
gray='#c0c0c0'
blue='#D7EAFF'
tempcolor=''
bgcolor=blue

# %%
app = App()
time.sleep(1)

# %%
configurar()
try:
    while app.is_alive():       #Se finaliza cuando la interfaz se cierra
        #Habilita o deshabilita el boton de medir en función de los estados de las conexiones
        if estados['srvcon']=='Conectado' and estados['sercon']=='Conectado' and estados['config']=='Configurado':
            app.btn_medir.config(state=tk.NORMAL)
        else:
            app.btn_medir.config(text="INICIAR\nMEDICIÓN", state=tk.DISABLED)
            flag_medIni=False
        #Iniciar medición desde HMI (A)
        if flag_medIni:        
            app.btn_configurar['state']=tk.DISABLED         #Deshabilito los botones de config y conexion
            app.btn_conectar_srv['state']=tk.DISABLED
            app.btn_conectar_LCR['state']=tk.DISABLED
            #Pido datos a OPC:
            cn+=1               #mando un numero de confirmación para que lo devuelva y saber si el valor devuelto es actual
            if cn>999: cn=1
            dts=srv.enviar(str(cn))
            if dts=='error':
                app.lbl_gral1.config(text=srv.status, **rojo)
                app.btn_conectar_srv.config(text= 'CONECTAR\nSERVIDOR',**rojo)
                estados['srvcon']='Error'
                continue                    #Con continue vuelvo al while, saltando todo lo de abajo
            else:
                app.lbl_gral1.config(text='...', **neutro)

        
            datosOPC=list(dts[1:-1].split(sep=","))     #Hago un arreglo para quitarle los corchetes de la lista
            for n,x in enumerate(datosOPC):             #y los convierto en numeros 
                if n>1:                           
                    datosOPC[n]=float(x)
                else:
                    datosOPC[n]=int(x)             #el primero queda entero porque lo comparo con cn

            #Analizo el dato de posición traido de OPC. Si está en posición, se activa un flag (B)
            if datosOPC[1]==1:         #El bit de posición tiene que estar en el lugar 1 de la lista enviada
                filtroPos01+=1
                if filtroPos01>=10:     #Espera un tiempo... considerando las demoras, filtroPos01>=10 es un poco menos de 5 segundos
                    flag_posOK=True
            else:
                flag_posOK=False
                filtroPos01=0
        
            #Comparo el numero de confirmación para chequear comunicacion (C)
            if datosOPC[0]==cn and datosOPC[0]>0:        #Activa el flag comOK si esta todo OK
                #app.lbl_stssrv.config(text="Conectado")
                app.lbl_1.config(text=f'En posicion: {datosOPC[1]}')
                app.lbl_2.config(text=f'Posicion: {datosOPC[2]}')
                app.lbl_3.config(text=f'Error SC: {datosOPC[3]}')
                app.lbl_4.config(text=f'Presion: {datosOPC[4]}')
                app.lbl_5.config(text=f'Nivel: {datosOPC[5]}')
                flag_comOK=True
            else:
                flag_comOK=False    #Si no lo desactiva y deja un mensaje en HMI
                app.lbl_gral1.config(text="Error de datos desde OPC",**rojo)
        

            #Chequeo cuándo se cumplen las n repeticiones de los barridos de frecuencia (D)
            if repeticion>=repeticiones:
                flag_cicloFin=True
            app.lbl_7.config(text=f'Repetición: {repeticion}')
            app.lbl_8.config(text=f'PosOK: {flag_posOK}, ComOK:{flag_comOK}, CicloFin:{flag_cicloFin}',width=40)

            if flag_cicloFin:           #Si se finaliza el ciclo...
                repeticion=0
                ifrec=0        
                if not flag_posOK:      #...Espera a que salga de la posición para reiniciarlo
                    filtroPos10+=1
                    if filtroPos10>=10:    #Espera un tiempo... considerando las demoras, filtroPos10>=10 es un poco menos de 5 segundos
                        flag_cicloFin=False
                        filtroPos10=0
                else: filtroPos10=0

            #Colores y textos para la etiqueta general
            if flag_cicloFin:
                app.btn_SEMAFORO.config(text='FIN DE MEDICIÓN\nSE PUEDE MOVER',background=green)
        
            if flag_posOK and not flag_cicloFin:
                #app.canvas.config(background=yellow)
                app.btn_SEMAFORO.config(text='MIDIENDO\nNO MOVER',background='red')
            if not flag_posOK:
                app.btn_SEMAFORO.config(text='BUSCANDO\nPOSICION',background=yellow)
    
            # Chequeo que se den las condiciones para medir (A=1 -siempre está porque es el if principal- , B=1 ,C=1 y D=0)
            if flag_posOK and flag_comOK and flag_lcrOK and not flag_cicloFin:                        
                #Si se cumplen las condiciones, empiezo a medir
            
                #Primero traigo la frecuencia configurada
                frecuencia=frecuencias[ifrec]      #no hago un 'for x in frecuencias' porque no pararía hasta terminar todos los valores
                app.lbl_6.config(text=f'Frecuencia: {frecuencia}')
                LCR.LCR_cambiarfreq(frecuencia)
                time.sleep(1)
                datosLCR=LCR.LCR_medir()
                app.lbl_gral2.config(text=f'Repetición: {repeticion+1} de {repeticiones} | frec: {frecuencia}Hz | {datosLCR[0]} {datosLCR[1]}, {datosLCR[2]} {datosLCR[3]}',**neutro)
                #Chequeo si hay algun error en la medición del LCR
                if 'error' in datosLCR:
                    flag_lcrOK=False
                    conectarlcr()       #desconecta el LCR
                    app.lbl_gral2.config(text='Error de datos en LCR',**rojo)
                
                else:
                    #armo la cadena de datos para guardar, con los datos de OPC y de equipo a medir
                    fecha=[str(datetime.datetime.now().date()), str(datetime.datetime.now().time())]
                    filename=rf'E:\Proyectos Python\capem\Cliente\Mediciones\{archivo}'
            
                    datos_guardar=[repeticion, frecuencia]       #datos básicos
                    datos_guardar=datos_guardar+datosOPC[1:]     #Datos de OPC a partir del 1 (el cero es el check de comunicacion)
                    datos_guardar=datos_guardar+list(datosLCR)   #Datos de LCR
                    datos_guardar=datos_guardar+fecha            #Fecha y hora
                    a=comentario.split('\n')
                    comentariol=[]
                    for x in a:
                        c=[]
                        c.append(x)  
                        comentariol.append(c)
                    
                    #Guardo los datos en csv
                    escribir_csv(filename,datos_guardar,encabezado,comentariol)
                    ifrec+=1
                    if ifrec>=tfrec:        #límite para las frecuencias
                        ifrec=0
                        repeticion+=1
        else:
            flag_insertarheader=True
            if estados['srvcon']=='Conectado' and estados['sercon']=='Conectado' and estados['config']=='Configurado':
                app.btn_SEMAFORO.config(text='LISTO PARA\nMEDIR',background='white')
    
            else:
                app.btn_SEMAFORO.config(text='EN\nCONFIGURACIÓN',background=gray)
            flag_posOK=False
            flag_cicloFin=False
            app.btn_configurar['state']=tk.NORMAL
            app.btn_conectar_srv['state']=tk.NORMAL
            app.btn_conectar_LCR['state']=tk.NORMAL
except Exception as e:
    print(str(e))
LCR.LCR_inicializar('OFF')
del app
#Cuando cierra la aplicacion, manda el comando de cerrar el servidor para que no de problemas
#srv.cerrar()
        


