import time, datetime
def medir(tiempo=1.0,comando=2,start=1):
    "Rutina que toma las mediciones de CAPEM y del instrumento"
    #global comando,start
    #Acá va la funcion que mide las variables de CAPEM y del instrumento
    while comando == start:
        time.sleep(tiempo)
        print(datetime.datetime.now())
    
    print ("medicion finalizada")
    variables=[]
    
    return variables