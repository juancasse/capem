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
                if okf and okr:
                    err='no'
                elif not okf and not okr:
                    err='Frecuencias y repeticiones no definidas'
                elif not okf:
                    err='Frecuencias no definidas'
                else:
                    err='Repeticiones no definidas'
        except Exception as e:
            err=e
        return self.freq, self.rep,err


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
        try:
            self.srv.settimeout(10.0)
            envio=datos.encode("ascii")
            self.srv.sendall(envio)
            data=self.srv.recv(1024).decode("ascii")
        except Exception as e:
            self.status=e
            data='error'
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
    def __init__(self, port=None, baudrate=38400, bytesize=8, parity='N', stopbits=1, timeout=3):
        self.status="desconectado"
        self.port=port
        self.baudrate=baudrate
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.timeout=timeout
        self.estado={'conexion':'desconectado', 'init':'sin inicializar', 'lectura':'ok', 'escritura':'ok'}
    
    def conectar(self, **kwargs):
        
        if 'port' in kwargs: self.port=kwargs['port']
        if 'baudrate'in kwargs: self.baudrate=kwargs['baudrate']
        if 'bytesize'in kwargs: self.bytesize=kwargs['bytesize']
        if 'parity'in kwargs: self.parity=kwargs['parity']
        if 'stopbits'in kwargs: self.stopbits=kwargs['stopbits']
        if 'timeout' in kwargs: self.timeout=kwargs['timeout']

        from serial import Serial
        try:
            ret=0
            self.con=Serial(port=self.port,baudrate=self.baudrate,bytesize=self.bytesize,
                            parity=self.parity,stopbits=self.stopbits, timeout=self.timeout)
            if self.con.port !=None:
                self.estado['conexion']='conectado'
                ret=1
        except Exception as ex:
            self.estado['conexion']=str(ex)
            ret=2
        return ret

    def desconectar(self):
        del self.con
    
    def abrir(self):
        try:
            if self.con.isOpen()==False:
                self.con.open()
            if self.con.isOpen()==True:
                #self.estado['puerto']="abierto"
                pass
            else:
                #self.estado['puerto']="cerrado"
                pass
        except Exception as ex:
            #self.estado['puerto']=f'Error: {str(ex)}'
            pass
    
    def cerrar(self):
        try:
            if self.con.isOpen()==True:
                self.con.close()
                #self.estado['puerto']="cerrado"
        except Exception as ex:
            #self.estado['puerto']=f'Error: {str(ex)}'
            pass
    
    def escribir(self, datos:str):
        try:
            #Antes de escribir vacío el buffer de salida y de entrada
            self.con.flushOutput()
            self.con.flushInput()
            dts=f'{datos}\n\r'
            if self.con.isOpen():
                self.con.write(dts.encode())
                self.estado['escritura']='ok'
            else:
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
        res= None
        match tipo:
            case "RL":
                try:
                    res=self.con.readline(num).decode()
                except Exception as e:
                    res=str(e)

            case "RLS":
                try:
                    res=self.con.readlines(num).decode()
                except Exception as e:
                    res=str(e)
            case "R":
                try:
                    if num==-1: num=1
                    res=self.con.read(num).decode()
                except Exception as e:
                    res=str(e)
        return res   

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
        try: 
            from time import sleep
            freal=freq/1000.0
            cmd="MAIN:FREQ {:.5f}".format(freal)
            print(cmd)
            self.escribir(cmd)
            sleep(0.5)
            ret=self.leer('RL')
            return ret
        except Exception as e:
            return str(e)
    
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
                self.escribir(f"MAIN:TRIG:{cmd}")

            elif modo in ["RQ","CD","CR","LQ","LR","ZQ"]:
                cmd=modo
                self.escribir(f"MAIN:MODE:{cmd}")
        else: self.mensaje='Error: El puerto está cerrado'

    def LCR_inicializar(self,m='ON',**kwargs):
        """Ejecuta las funciones necesarias para inicializar:
            -Conectar
            -Enviar comando de iniciar comunicacion (COMU?)
            -Ver que responde correctamente(COMU:ON)
            -Enviar comando de finalizar inicializacion (COMU:OVER)
            -Ver que responde correctamente (COMU:OVER) 
            -Setear modo automático"""
        
        if 'port' in kwargs: self.port=kwargs['port']
        if 'baudrate'in kwargs: self.baudrate=kwargs['baudrate']
        if 'bytesize'in kwargs: self.bytesize=kwargs['bytesize']
        if 'parity'in kwargs: self.parity=kwargs['parity']
        if 'stopbits'in kwargs: self.stopbits=kwargs['stopbits']
        if 'timeout' in kwargs: self.timeout=kwargs['timeout']
        #self.estado={'conexion':'desconectado','puerto':'cerrado', 'init':'sin inicializar', 'lectura':'ok', 'escritura':'ok'}

        from time import sleep
        try:
            if m=='OFF':
                self.escribir('COMU:OFF.')
                self.inicializado=0
                self.desconectar()
                self.estado['conexion']='desconectado'
                self.estado['init']='sin inicializar'
            else:
                sts=self.conectar()
                sleep(0.3)
                if sts==1:
                    self.escribir('COMU?')
                    sleep(0.5)
                    resp=self.leer('RL')
                    if 'COMU:ON' in resp:
                        self.escribir('COMU:OVER')
                        sleep(0.5)
                        resp=self.leer('RL')
                        if 'COMU:OVER' in resp:
                            self.estado['init']='inicializado'
                            self.inicializado=1
                        else: self.estado['init']=f'respuesta incorrecta: {resp}'
                    else: self.estado['init']=f'respuesta incorrecta: {resp}'
        except Exception as e:
            self.inicializado=4
            self.status=str(e)
            self.estado['init']=f'error: {str(e)}'
        return self.estado['init']

    def LCR_Configurar(self):
        from time import sleep
        #Frecuencia
        res=self.LCR_cambiarfreq(12)
        if not 'MAIN:FREQ' in res:
            return "Error en seteo de frecuencia"
        
        #Velocidad
        self.escribir('MAIN:SPEE:SLOW')
        sleep(0.3)
        lect=self.leer()
        if not ('MAIN:SPEE:SLOW' in lect):
            return "Error en cambiar velocidad"
        
        #Tensión
        self.escribir('MAIN:VOLT 1.250')
        sleep(0.3)
        lect=self.leer()
        if not ('MAIN:VOLT 1.250' in lect):
            return "Error en ajustar tensión"

        #trigger

        #display
        self.escribir('MAIN:DISP:VALU')
        #circuit

        #modo (man/auto)

        #modo LR

        #CV

        #BIAS
        return 'configuracion exitosa'
    def LCR_medir(self):
        """Mide los parámetros precargados del LCR"""
        from time import sleep
        self.escribir('MAIN:STAR')
        sleep(1)
        r1=self.leer('RL')
        r2=self.leer('RL')
        if 'MAIN:PRIM' in r1 and 'MAIN:SECO' in r2:
            prim=r1[11:17]
            uprim=r2[16:18]
            if r2[18]=='k':
                sec=str(round(float(r2[11:16])*100,3))
            else:
                sec=r2[11:16]
            usec='Ohm'
        else :
            prim,uprim,sec,usec='error','error','error','error'
        return prim,uprim,sec,usec

# %%
lcr=LCR()
lcr.LCR_inicializar(port='COM6')

# %%
lcr.LCR_cambiarfreq(50)

# %%
test=lcr.escribir('MAIN:DISP:VALU')
test

# %%
print(test)

# %%
lcr.leer('RL')

# %%
lcr.LCR_inicializar('OFF')


