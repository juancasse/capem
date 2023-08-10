# %%
class configurar:
    def __init__(self, freq=[12,15,20,25,30,140,160,180,200],rep=10):
        self.freq=freq
        self.rep=rep
        
    
    def cargarconfig(self,archivo="configuracion/configuracion.txt"):
        """ 
        Función que trae configuración de un archivo que se da como argumento.
        Si no se argumenta, toma por defecto configuracion/config.txt
        """
        self.archivo=archivo
        okf=False
        okr=False
        okn=False
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
                u1=texto.find("&")+1
                u2=texto.find("&",u1)
                if u1>0 and u2>0:
                    nombre=texto[u1+1:u2-1]
                    if not '.csv' in nombre:
                        nombre=nombre.join('.csv')
                    self.nombre=nombre
                    okn=True
                u1=texto.find("*")+1
                u2=texto.find("*",u1)
                if u1>0 and u2>0:
                    comentario=texto[u1+1:u2-1]
                    self.comentario=''.join(comentario)
                if okf and okr and okn:
                    err='no'
                elif not okf and not okr:
                    err='Frecuencias y repeticiones no definidas'
                elif not okf:
                    err='Frecuencias no definidas'
                elif not okn:
                    err='Nombre de archivo sin definir'
                else:
                    err='Repeticiones no definidas'
        except Exception as e:
            err=e
        return self.nombre, self.comentario, self.freq, self.rep,err


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
            self.status=str(e)
            data=str(e)
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
        #self.status="desconectado"
        self.port=port
        self.baudrate=baudrate
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.timeout=timeout
        self.estado={'conexion':'desconectado', 'init':'sin inicializar', 'lectura':'ok', 'escritura':'ok'}
    
    def conectar(self, **kwargs):
        """
        Función que realiza la conexión del equipo.
        Si no se declara configuración, toma las configuraciones declaradas al crear la clase
        KWARGS:
            -port       ('PORT6')
            -baudrate   (38400)
            -bytesize   (8)
            -parity     ('N')
            -stopbits   (1)
            -timeout    (3)
        """
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
            ret=str(ex)
        return ret

    def desconectar(self):
        del self.con
    
    def escribir(self, datos:str):
        '''
        Agrega a 'datos' un LF y CR, y envía la cadena al equipo serie.
        No devuelve nada, pero guarda el estado en estado['escritura']
        '''
        try:
            #Antes de escribir vacío el buffer de salida y de entrada
            self.con.flushOutput()
            self.con.flushInput()
            dts=f'{datos}\r\n'
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
    Cuando se crea el objeto LCR se cargan las configuraciones estandar,
    por lo que se deben modificar al inicializar
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
            self.escribir(cmd)
            sleep(0.5)
            ret=self.leer('RL')
            return ret
        except Exception as e:
            return str(e)
    
    def LCR_inicializar(self,m='ON',**kwargs):
        """Si el parámetro m es 'OFF', desconecta el equipo y elimina la conexion.
        Si el parámetro m es 'ON, crea la conexión y ejecuta las funciones necesarias para inicializar:
            -Conectar
            -Enviar comando de iniciar comunicacion (COMU?)
            -Ver que responde correctamente(COMU:ON)
            -Enviar comando de finalizar inicializacion (COMU:OVER)
            -Ver que responde correctamente (COMU:OVER) 
            KWARGS:
                -port       ('PORT6')
                -baudrate   (38400)
                -bytesize   (8)
                -parity     ('N')
                -stopbits   (1)
                -timeout    (3)
            """
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
                else: self.estado['init']=sts
        except Exception as e:
            self.inicializado=4
            self.estado['conexion']=str(e)
            self.estado['init']=f'error: {str(e)}'
        return self.estado['init']
    
    def LCR_modo(self, modo:str="M"):
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
        from time import sleep
        if self.estado['init']=='inicializado':
            if modo in ["M","A"]:
                if modo=="M": cmd="MANU"
                else: cmd="AUTO"
                self.escribir(f"MAIN:TRIG:{cmd}")
                sleep(0.3)
                res=self.leer('RL')
                if f'MAIN:TRIG:{modo}' in res: return 'OK'
                else: return f'error al setear el modo {modo}'

            elif modo in ["RQ","CD","CR","LQ","LR","ZQ"]:
                cmd=modo
                self.escribir(f"MAIN:MODE:{cmd}")
                sleep(0.3)
                res=self.leer('RL')
                if f'MAIN:MODE:{modo}' in res: return 'OK'
                else: return f'error al setear el modo {modo}'
            else: self.mensaje='parámetro no encontrado'
        else: self.mensaje='Error: el equipo se encuentra desconectado'


    def LCR_Configurar(self):
        from time import sleep
        
        #Velocidad
        self.escribir('MAIN:SPEE:SLOW')
        sleep(0.3)
        res=self.leer()
        if not ('MAIN:SPEE:SLOW' in res):
            return "Error en cambiar velocidad"
        
        #display
        self.escribir('MAIN:DISP:VALU')
        sleep(0.3)
        res=self.leer('RL')
        if not 'MAIN:DISP:VALU' in res:
            return 'Error al configurar display'

        #Modo de medicion
        res=self.LCR_modo('LR')
        if not 'OK' in res:
            return 'Error al configurar modo de medición'
        
        #Circuito
        self.escribir('MAIN:CIRC:SERI')
        sleep(0.3)
        res=self.leer('RL')
        if not 'MAIN:CIRC:SERI' in res:
            return 'Error al configurar circuito'

        #Frecuencia
        res=self.LCR_cambiarfreq(12)
        if not 'MAIN:FREQ' in res:
            return "Error en seteo de frecuencia"
        
        #Tensión
        #self.escribir('MAIN:VOLT 1.250')
        #sleep(0.3)
        #res=self.leer()
        #if not ('MAIN:VOLT 1.250' in res):
        #    return "Error en ajustar tensión"
        
        #Modo de disparo
        res=self.LCR_modo('M')
        if not 'OK' in res:
            return 'Error al configurar modo de disparo'
        
        #CV
        self.escribir('MAIN:C.V.:OFF.')
        sleep(0.3)
        res=self.leer()
        if not ('MAIN:C.V.:OFF.' in res):
            return "Error en ajustar tensión constante (off)"
      
        #BIAS interno
        self.escribir('MAIN:INTB:OFF.')
        sleep(0.3)
        res=self.leer()
        if not ('MAIN:INTB:OFF.' in res):
            return "Error en ajustar int BIAS (off)"
        
        #BIAS externo
        self.escribir('MAIN:EXTB:OFF.')
        sleep(0.3)
        res=self.leer()
        if not ('MAIN:EXTB:OFF.' in res):
            return "Error en ajustar ext BIAS (off)"
        
        #PROMEDIO de muestras
        self.escribir('STEP:AVER 1.00')
        sleep(0.3)
        res=self.leer()
        if not ('STEP:AVER 1' in res):
            return "Error en setear el numero de muestras"
        
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
class Lockin(equiposerie):
    """
    Herencia de 'equiposerie' adaptado a las funciones del Lockin
    Cuando se crea el objeto Lockin se cargan las configuraciones estandar,
    por lo que se deben modificar al inicializar
    """
    def __init__(self):
        equiposerie.__init__(self)
        #self.inicializado=False
    
    def LIA_inicializar(self,m='ON',**kwargs):
        """Si el parámetro m es 'OFF', desconecta el equipo y elimina la conexion.
        Si el parámetro m es 'ON, crea la conexión y ejecuta las funciones necesarias para inicializar:
            -Conectar
            -Enviar comando de iniciar comunicacion (COMU?)
            -Ver que responde correctamente(COMU:ON)
            -Enviar comando de finalizar inicializacion (COMU:OVER)
            -Ver que responde correctamente (COMU:OVER) 
            KWARGS:
                -port       ('PORT6')
                -baudrate   (38400)
                -bytesize   (8)
                -parity     ('N')
                -stopbits   (1)
                -timeout    (3)
            """
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
                self.inicializado=0
                self.desconectar()
                self.estado['conexion']='desconectado'
                self.estado['init']='sin inicializar'
            else:
                sts=self.conectar()
                sleep(0.3)
                if sts==1:
                    self.escribir('OF')
                    sleep(0.3)
                    resp=self.leer('RL')
                    if 'OF' in resp:
                        self.estado['init']='inicializado'
                        self.inicializado=1
                    else: self.estado['init']=f'respuesta incorrecta: {resp}'
                else: self.estado['init']=sts
        except Exception as e:
            self.inicializado=4
            self.estado['conexion']=str(e)
            self.estado['init']=f'error: {str(e)}'
        return self.estado['init']
    
    def LIA_cambiarfrecuencia(self, freq:float):
        """
        Función para cambiar la frecuencia del Lockin.
        No tiene tiempo de estabilizacion.
        La frecuencia se ingresa en Hertz, puede ser con décimaso centécimas
        """
        try: 
            from time import sleep
            freal=int(freq*1000)
            cmd=f"OF{freal}"
            self.escribir(cmd)
            sleep(0.3)
            ret=self.leer('RL')
            if 'OF' in ret:
                ret='OK'
            else: ret= 'ERROR'
            return ret
        except Exception as e:
            return str(e)
        
    def LIA_cambiartension(self, tension:float):
        """
        Función para cambiar la tension del Lockin.
        No tiene tiempo de estabilizacion.
        La tensión es un numero flotante, en voltios
        """
        try: 
            from time import sleep
            tensionmv=int(tension*1000)
            if tensionmv >3000: tensionmv=3000
            cmd=f"OA{tensionmv}"
            print(cmd)
            self.escribir(cmd)
            sleep(0.3)
            ret=self.leer('RL')
            if 'OA' in ret:
                ret='OK'
            else: ret= 'ERROR'
            return ret
        except Exception as e:
            return str(e)
    
    def LIA_configurar(self):
        return 'OK'
        

    def convertir(self,x):
        return float(x)

    def LIA_medir(self):
        """Mide los parámetros precargados del LockIn"""
        from time import sleep
        self.escribir('XY.')
        sleep(0.3)
        
        resp1=self.leer('RL')
        if 'XY.' in resp1:
            resp2=self.leer('RL')
            resp3=resp2.split(sep=',')
            prim, sec=map(self.convertir,resp3)
            uprim='mV'
            usec='mV'
        else:
            prim,uprim,sec,usec='error','error','error','error'
        return prim,uprim,sec,usec
    
    def LIA_leerfrecuencia(self):
        """Mide la frecuencia del LockIn"""
        from time import sleep
        self.escribir('FRQ.')
        sleep(0.3)
        
        resp1=self.leer('RL')
        if 'FRQ.' in resp1:
            resp2=self.leer('RL')
            frec=self.convertir(resp2)
        else:
            frec='error'
        return frec
    
    def LIA_Cambiarsensibilidad(self, consigna:str):
        """
        Cambia la sensibilidad del lockin
        18, 19, 20 ..... 1, 2 o 5mV
        21, 22, 23 ..... 10, 20 o 50mV
        24, 25, 26 ..... 100, 200 o 500mV
        27         ..... 1V
        """
        from time import sleep
        if consigna == '+':
            self.escribir('SEN')
            sleep(0.3)
            resp1=self.leer('RL')
            if 'SEN' in resp1:
                resp2=self.leer('RL')
                sen=int(resp2)+1
                self.escribir(f'SEN{sen}')
                sleep(0.3)
                resp1=self.leer('RL')
                if f'SEN{sen}' in resp1:
                    ret='OK'
                else: ret='error'
        elif consigna=='-':
            self.escribir('SEN')
            sleep(0.3)
            resp1=self.leer('RL')
            if 'SEN' in resp1:
                resp2=self.leer('RL')
                sen=int(resp2)-1
                self.escribir(f'SEN{sen}')
                sleep(0.3)
                resp1=self.leer('RL')
                if f'SEN{sen}' in resp1:
                    ret='OK'
                else: ret='error'
        else:
            ret='error'
        return ret
    
    def LIA_Leersensibilidad(self):
        from time import sleep
        self.escribir('SEN')
        sleep(0.3)
        resp1=self.leer('RL')
        if 'SEN' in resp1:
            resp2=self.leer('RL')
            sen=int(resp2)
            match sen:
                case 18: ret=1
                case 19: ret=2
                case 20: ret=5
                case 21: ret=10
                case 22: ret=20
                case 23: ret=50
                case 24: ret=100
                case 25: ret=200
                case 26: ret=500
                case 27: ret=1000
                case _: ret= 'error'
        else:
            ret='error'
        return ret


    def LIA_CambiarTau(self, tau:int):
        """
        Cambia la constante de tiempo del lockin
        10 -> 50mS
        11 -> 100mS
        12 -> 200mS
        13 -> 500mS
        14 -> 1000mS
        """
        if tau in [10,11,12,13,14]:
            #Solo incorporo estas constantes de tiempo ya que son las probables de usar
            from time import sleep
            self.escribir(f'TC{tau}')
            sleep(0.3)
            resp1=self.leer('RL')
            if f'TC{tau}' in resp1:
                ret='OK'
            else: ret='error'
        else:
            ret='error'
        return ret

# %% [markdown]
# def LIA_Cambiarsensibilidad(self, sen:int):
#         """
#         Cambia la sensibilidad del lockin
#         18, 19, 20 ..... 1, 2 o 5mV
#         21, 22, 23 ..... 10, 20 o 50mV
#         24, 25, 26 ..... 100, 200 o 500mV
#         27         ..... 1V
#         """
#         if sen in [18,19,20,21,22,23,24,25,26,27]:
#             #Solo incorporo estas sensibilidades ya que son las probables de usar
#             from time import sleep
#             self.escribir(f'SEN{sen}')
#             sleep(0.3)
#             resp1=self.leer('RL')
#             if f'SEN{sen}' in resp1:
#                 ret='OK'
#             else: ret='error'
#         else:
#             ret='error'
#         return ret


