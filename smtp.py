import smtplib
import poplib
import email
import tkinter as tk
from tkinter import messagebox

# Configuración de correo electrónico
SMTP_SERVER = 'sandbox.smtp.mailtrap.io'
SMTP_PORT = 587
POP3_SERVER = 'pop3.mailtrap.io'
POP3_PORT = 1100
EMAIL_ADDRESS = '395e2d8a30ce3c'
EMAIL_PASSWORD = '2f0591ed5f6f8e'

# Función para enviar un correo electrónico
def enviar_correo():
    destinatario = entry_destinatario.get()
    asunto = entry_asunto.get()
    cuerpo = text_cuerpo.get('1.0', tk.END)

    mensaje = f"Subject: {asunto}\n\n{cuerpo}"

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, destinatario, mensaje)
        messagebox.showinfo('Envío de correo', 'Correo enviado con éxito.')
    except Exception as e:
        messagebox.showerror('Error', f'Error al enviar el correo: {str(e)}')

def recibir_correos():
    try:
        mailbox = poplib.POP3(POP3_SERVER, POP3_PORT)
        mailbox.user(EMAIL_ADDRESS)
        mailbox.pass_(EMAIL_PASSWORD)

        num_correos = len(mailbox.list()[1])

        lista_correos.delete(0, tk.END)

        for i in range(num_correos):
            _, correo_data, _ = mailbox.retr(i+1)
            raw_email = b'\r\n'.join(correo_data).decode()
            mensaje = email.message_from_string(raw_email)

            remitente = mensaje['From']
            if remitente is None:
                remitente = "Remitente desconocido"

            asunto = mensaje['Subject']

            lista_correos.insert(tk.END, f"De: {remitente} - Asunto: {asunto}")

        mailbox.quit()
    except Exception as e:
        messagebox.showerror('Error', f'Error al recibir los correos: {str(e)}')

    # Programar la próxima actualización en 10 segundos
    recibir_window.after(10000, recibir_correos)

def mostrar_cuerpo(event):
    seleccionado = lista_correos.curselection()
    if seleccionado:
        index = seleccionado[0]

        try:
            mailbox = poplib.POP3(POP3_SERVER, POP3_PORT)
            mailbox.user(EMAIL_ADDRESS)
            mailbox.pass_(EMAIL_PASSWORD)

            _, correo_data, _ = mailbox.retr(index+1)
            raw_email = b'\r\n'.join(correo_data).decode()
            mensaje = email.message_from_string(raw_email)

            cuerpo = ''
            if mensaje.is_multipart():
                for part in mensaje.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain' or content_type == 'text/html':
                        cuerpo = part.get_payload(decode=True).decode()
                        break
            else:
                cuerpo = mensaje.get_payload(decode=True).decode()

            text_cuerpo_recibido.delete('1.0', tk.END)
            text_cuerpo_recibido.insert(tk.END, cuerpo)

            mailbox.quit()
        except Exception as e:
            messagebox.showerror('Error', f'Error al mostrar el cuerpo del correo: {str(e)}')


# Crear la interfaz de usuario para enviar correos
enviar_window = tk.Tk()
enviar_window.title('Enviar correo')

label_destinatario = tk.Label(enviar_window, text='Destinatario:')
entry_destinatario = tk.Entry(enviar_window)
label_asunto = tk.Label(enviar_window, text='Asunto:')
entry_asunto = tk.Entry(enviar_window)
label_cuerpo = tk.Label(enviar_window, text='Cuerpo:')
text_cuerpo = tk.Text(enviar_window)

button_enviar = tk.Button(enviar_window, text='Enviar', command=enviar_correo)

label_destinatario.pack()
entry_destinatario.pack()
label_asunto.pack()
entry_asunto.pack()
label_cuerpo.pack()
text_cuerpo.pack()
button_enviar.pack()

# Crear la interfaz de usuario para recibir correos
recibir_window = tk.Toplevel(enviar_window)
recibir_window.title('Recibir y mostrar correos')

lista_correos = tk.Listbox(recibir_window, width=100)
scroll_lista = tk.Scrollbar(recibir_window, command=lista_correos.yview)
lista_correos.config(yscrollcommand=scroll_lista.set)
lista_correos.bind('<<ListboxSelect>>', mostrar_cuerpo)

text_cuerpo_recibido = tk.Text(recibir_window)

lista_correos.pack(side=tk.LEFT, fill=tk.BOTH)
scroll_lista.pack(side=tk.RIGHT, fill=tk.Y)
text_cuerpo_recibido.pack(fill=tk.BOTH)

recibir_correos()

enviar_window.mainloop()
