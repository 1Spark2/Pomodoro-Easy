import random
import threading
import tkinter as tk
from datetime import datetime
import csv
import os
from tkinter import messagebox
import pygame

pygame.mixer.init()

carpeta_sonidos = './shitpostsounds/'


# Función para cargar la cantidad de ciclos ya completados en el día actual desde un archivo CSV.
def cargar_ciclos():
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    ciclos = 0
    try:
        with open("registro_pomodoro.csv", mode='r', newline='') as archivo:
            lector = csv.reader(archivo)
            for fila in lector:
                if fila[0] == fecha_actual:
                    ciclos = int(fila[1])
    except FileNotFoundError:
        pass  # El archivo se creará cuando se guarden los ciclos.
    return ciclos

# Función para guardar la cantidad total de ciclos completados en el día actual en un archivo CSV.
def guardar_ciclos(ciclos):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    temp_file = "registro_pomodoro_temp.csv"
    archivo_existe = os.path.isfile("registro_pomodoro.csv")
    with open(temp_file, mode='w', newline='') as archivo_temp:
        escritor = csv.writer(archivo_temp)
        if archivo_existe:
            with open("registro_pomodoro.csv", mode='r', newline='') as archivo:
                lector = csv.reader(archivo)
                entrada_existente = False
                for fila in lector:
                    if fila[0] == fecha_actual:
                        escritor.writerow([fecha_actual, ciclos])
                        entrada_existente = True
                    else:
                        escritor.writerow(fila)
                if not entrada_existente:
                    escritor.writerow([fecha_actual, ciclos])
        else:
            escritor.writerow([fecha_actual, ciclos])
    os.replace(temp_file, "registro_pomodoro.csv")


def reproducir_sonido_aleatorio():
    archivos_sonido = [archivo for archivo in os.listdir(carpeta_sonidos) if archivo.endswith(('.mp3', '.wav'))]
    sonido_aleatorio = random.choice(archivos_sonido)
    pygame.mixer.music.load(os.path.join(carpeta_sonidos, sonido_aleatorio))
    pygame.mixer.music.play()


def mostrar_mensaje_inicio_fase(titulo, mensaje):
    messagebox.showinfo(titulo, mensaje)

def actualizar_temporizador():
    global tiempo_restante, fase_actual, contador_ciclos

    if tiempo_restante > 0 and not en_pausa:
        tiempo_restante -= 1
        mostrar_tiempo(tiempo_restante)
        ventana.after(1000, actualizar_temporizador)
    elif tiempo_restante == 0:
        if fase_actual == 0:  # Fin de la fase de trabajo
            reproducir_sonido_aleatorio()
            messagebox.showinfo("Fin del Trabajo", "Listos tus 25 minutos, ¿empiezas los 5 minutos de pensamiento crítico?")
            tiempo_restante = duracion_pensamiento_critico
        elif fase_actual == 1:  # Fin de la fase de pensamiento crítico
            reproducir_sonido_aleatorio()
            messagebox.showinfo("Pensamiento Crítico", "Grande crack, ¿puedes pasar a los 5 min de descanso?")
            tiempo_restante = duracion_descanso
        elif fase_actual == 2:  # Fin de la fase de descanso
            reproducir_sonido_aleatorio()
            contador_ciclos += 1
            guardar_ciclos(contador_ciclos)
            etiqueta_contador.config(text=f"Ciclos completados hoy: {contador_ciclos}")
            messagebox.showinfo("Descanso Completado", "¿Listo para comenzar otro Pomodoro?")
            tiempo_restante = duracion_trabajo
        fase_actual = (fase_actual + 1) % 3
        mostrar_tiempo(tiempo_restante)


# Función para cerrar la aplicación y guardar los ciclos.
def cerrar_aplicacion():
    guardar_ciclos(contador_ciclos)
    ventana.destroy()


# Función para mostrar el tiempo restante en la etiqueta.
def mostrar_tiempo(segundos):
    minutos = segundos // 60
    segundos = segundos % 60
    etiqueta_temporizador.config(text=f"{minutos:02d}:{segundos:02d}")

# Función para iniciar o reanudar el Pomodoro.
def iniciar():
    global en_pausa
    en_pausa = False
    actualizar_temporizador()

# Función para pausar el Pomodoro.
def pausar():
    global en_pausa
    en_pausa = True

# Función para reiniciar el Pomodoro.
def reiniciar():
    global tiempo_restante, fase_actual, contador_ciclos
    tiempo_restante = duracion_trabajo
    fase_actual = 0
    contador_ciclos = cargar_ciclos()
    etiqueta_contador.config(text=f"Ciclos completados hoy: {contador_ciclos}")
    mostrar_tiempo(tiempo_restante)

# Configuración inicial
duracion_trabajo = 25 * 60
duracion_pensamiento_critico = 5 * 60
duracion_descanso = 5 * 60
tiempo_restante = duracion_trabajo
fase_actual = 0
en_pausa = False
contador_ciclos = cargar_ciclos()

# Configuración de la ventana de Tkinter
ventana = tk.Tk()
ventana.title("Reloj Pomodoro Personalizado")
ventana.geometry("300x200")

etiqueta_temporizador = tk.Label(ventana, text="25:00", font=("Arial", 48))
etiqueta_temporizador.pack()

etiqueta_contador = tk.Label(ventana, text=f"Ciclos completados hoy: {contador_ciclos}", font=("Arial", 14))
etiqueta_contador.pack()

boton_iniciar = tk.Button(ventana, text="Iniciar", command=iniciar)
boton_iniciar.pack()

boton_pausar = tk.Button(ventana, text="Pausar", command=pausar)
boton_pausar.pack()

boton_reiniciar = tk.Button(ventana, text="Reiniciar", command=reiniciar)
boton_reiniciar.pack()

ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

ventana.mainloop()
