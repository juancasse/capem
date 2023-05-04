# %%
class configurar:
    def __init__(self, freq=[12,15,20,25,30,140,160,180,200],rep=10):
        self.freq=freq
        self.rep=rep
        
    
    def cargarconfig(self,archivo="configuracion/config.txt"):
        """ 
        Función que trae configuración de un archivo que se da como argumento.
        Si no se argumenta, toma por defecto configuracion/config.txt
        """
        self.archivo=archivo
        okf=False
        okr=False
        err=""
        try:
            with open(self.archivo) as config:
                texto="".join(config.readlines())
                u1=texto.find("$")+1
                u2=texto.find("$",u1)
                if u1>0 and u2>0:
                    frecuencias=texto[u1+1:u2-1].split(",")
                    for i, f in enumerate(frecuencias): 
                       frecuencias[i]=int(f)
                    self.freq=frecuencias
                    okf=True
                u1=texto.find("#")+1
                u2=texto.find("#",u1)
                if u1>=0 and u2>0:
                    rep=texto[u1+1:u2-1]
                    rep=int(rep)
                    self.rep=rep
                    okr=True
        except Exception as e:
            err=e
        return dict(frecuencias=self.freq, repeticiones=self.rep, okfrec=okf,okrep=okr,error=err)


# %%
class conexionsrv:
    """
    Clase conexión.
    Maneja la conexion con el servidor
    host: IP del servidor
    port: Puerto al cual apunta
    """
   

    def __init__(self, host="192.168.99.10", port = 9999):
        '''status puede ser : -> conectado
                              -> desconectado
                                '''
        #import socket
        self.host=host
        self.port=port
        self.srv=""
        self.status="desconectado"

    
    def conectar(self,host="192.168.99.10", port = 9999):
        """
        Realiza conexion con el servidor  
        """
        import socket
        self.srv=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port= port
        self.host=host
        try:
            self.srv.connect((self.host,self.port))
            self.status="conectado"
        except Exception as e:
            self.status=e
    
    def enviar(self,datos:str):
        """
        Envío comando a servidor (en formato string),
        y devuelve la respuesta en formato string
        """
        #import time
        envio=datos.encode("ascii")
        self.srv.sendall(envio)
        #time.sleep(0.1)
        data=self.srv.recv(1024).decode("ascii")
        return data
    
    def cerrar(self):
        self.srv.close()
        self.status="desconectado"
        


# %%
class equiposerie():
    """
    Clase que maneja conexion serial.
    Maneja la conexion con equipos serie, y la lectura de datos
    """
    def __init__(self, port=None, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=None):
        self.status="desconectado"
        self.port=port
        self.baudrate=baudrate
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.timeout=timeout
        self.estado={'conexion':'desconectado','puerto':'cerrado', 'init':'sin inicializar', 'lectura':'ok', 'escritura':'ok'}
    
    def conectar(self, **kwargs):
        
        if 'port' in kwargs: self.port=kwargs['port']
        if 'baudrate'in kwargs: self.baudrate=kwargs['baudrate']
        if 'bytesize'in kwargs: self.bytesize=kwargs['bytesize']
        if 'parity'in kwargs: self.parity=kwargs['parity']
        if 'stopbits'in kwargs: self.stopbits=kwargs['stopbits']
        if 'timeout' in kwargs: self.timeout=kwargs['timeout']

        from serial import Serial
        try:
            if self.con.port == None:
                self.con=Serial(port=self.port,baudrate=self.baudrate,bytesize=self.bytesize,
                                parity=self.parity,stopbits=self.stopbits, timeout=self.timeout)
            if self.con.port !=None:
                self.estado['conexion']='conectado'
        except Exception as ex:
            self.estado['conexion']=f'Error: {str(ex)}'

    
    def abrir(self):
        try:
            if self.con.isOpen()==False:
                self.con.open()
            if self.con.isOpen()==True:
                self.estado['puerto']="abierto"
            else:
                self.estado['puerto']="cerrado"
        except Exception as ex:
            self.estado['puerto']=f'Error: {str(ex)}'
    
    def cerrar(self):
        try:
            if self.con.isOpen()==True:
                self.con.close()
                self.estado['puerto']="cerrado"
        except Exception as ex:
            self.estado['puerto']=f'Error: {str(ex)}'
    
    def escribir(self, datos:str):
        try:
            #Antes de escribir vacío el buffer de salida
            self.con.flushOutput()
            if self.con.isOpen():
                self.con.write(datos.encode("ascii"))
                self.estado['escritura']='Error: falta abrir puerto'
        except Exception as ex:
            self.estado['escritura']=f'Error: {str(ex)}'

    
    def leer(self, tipo="RL", num=-1):
        """
        leer(tipo="RL", num=-1)
        tipo: Indica el tipo de lectura.
            RL: Read line, lee una linea completa, hasta que encuentra '\\n'. 
                Si se especifica num, se leeran como máximo ese numero de bytes
                CUIDADO! Si no se establece timeout, se bloquea hasta que encuentra el '\\n'.

            RLS: Read lines, devuelve varias líneas en forma de lista
                Si se especifica num, se leeran como máximo ese numero de líneas.
                

            R: Devuelve la cantidad de bytes especificados en num
                Si se especifica num, se leeran ese numero de bytes. Si no, se lee uno.
                Si no se establece timeout, se bloquea hasta que lee todos los bits especificados
        """
        #Antes de leer vacío el buffer de entrada
        self.con.flushInput()
        
        res= None
        match tipo:
            case "RL":
                try:
                    res=self.con.readline(num)
                except:
                    pass

            case "RLS":
                try:
                    res=self.con.readlines(num)
                except:
                    pass
            case "R":
                try:
                    if num==-1: num=1
                    res=self.con.read(num)
                except:
                    pass
        return res
    

# %%
#from serial import Serial

# %%
class LCR(equiposerie):
    """
    Herencia de 'equiposerie' adaptado a las funciones de LCR

    """
    def __init__(self):
        equiposerie.__init__(self)
        self.inicializado=False
    
    def LCR_cambiarfreq(self, freq):
        """
        Función para cambiar la frecuencia del LCR.
        No tiene tiempo de estabilizacion.
        """
        if self.con.port!=None:
            if self.status=="desconectado":
                self.conectar()
        freal=freq/1000.0
        cmd=f"MAIN:FREQ {freal}<^END^M"
        if self.con.isOpen()==False:
            self.abrir()
            self.escribir(cmd)
            self.cerrar()
        else: self.escribir(cmd)
    
    def LCR_modo(self, modo:str="A"):
        """
        Funcion que define el modo de funcionamiento.
        Hay dos usos: Poner el equipo en manual o atumático, y setearle que variables medir

        modo:   "A"-> Equipo en Automático
                "M"-> Equipo en Manual

        modo:   "RQ"-> mide Resistencia y Calidad 
                "CD"-> mide Capacitancia y Disipasión
                "CR"-> mide Capacitancia y Resistencia
                "LQ"-> mide Inductancia y Calidad
                "LR"-> mide Inductancia y Resistencia
                "ZQ"-> mide impedancia y Angulo  
        """
        if self.status=="abierto":
            if modo in ["M","A"]:
                if modo=="M": cmd="MANU"
                else: cmd="AUTO"
                self.escribir(f"MAIN:TRIG:{cmd}<^END^M>")

            elif modo in ["RQ","CD","CR","LQ","LR","ZQ"]:
                cmd=modo

                self.escribir(f"MAIN:MODE:{cmd}<^END^M>")
        else: self.mensaje='Error: El puerto está cerrado'

    def LCR_inicializar(self, port, baudrate, bytesize, parity, stopbits, timeout):
        """Ejecuta las funciones necesarias para inicializar:
            -Conectar
            -Abrir puerto
            -Enviar comando de iniciar comunicacion (COMU?)
            -Ver que responde correctamente(COMU:ON)
            -Enviar comando de finalizar inicializacion (COMU:OVER)
            -Ver que responde correctamente (COMU:OVER) 
            -Setear modo automático
        """
        from time import sleep
        try:
            self.conectar(port, baudrate, bytesize, parity, stopbits, timeout)
            
            self.modo("LR")
            sleep(1)
            self.modo("A")
            sleep(1)
            self.inicializado=1
        except Exception as e:
            self.inicializado=4
            self.status=str(e)


    def medir(self):
        """Mide los parámetros precargados del LCR"""
        #resp=self.leer()   #Completar cuando tenga en claro como se mide
        resp=list(1,2,3)
        return resp

            


# %%
class archivo_csv(csv):
    from os.path import isfile
    """
    Clase heredada de CSV.
    """
    def __init__(self,archivo):
        self.archivo=archivo

    def  __agregar__(self,file,line):
        with open(file, mode='a', newline='',) as archivo_csv:
            writer = self.writer(archivo_csv, delimiter=";")
            writer.writerow(line)
        archivo_csv.close()
        
    def escribir(self,fila:str, encabezado:str):
        #from os.path import isfile
        if isfile(self.archivo):
            self.__agregar__(self.archivo, fila.split(","))
        else:
            self.__agregar__(self.archivo, encabezado.split(","))
            self.__agregar__(self.archivo, fila.split(","))



