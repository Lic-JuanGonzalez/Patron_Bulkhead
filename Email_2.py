import tkinter as tk
import pika

MAX_MESSAGES_PER_CYCLE = 5

def start_email_2():
    def send_message():
        try:
            message = message_entry.get()
            channel.basic_publish(exchange='', routing_key='email_queue_1', body=message)
            message_entry.delete(0, tk.END)
        except Exception as e:
            print("Error al enviar el mensaje:", str(e))

    def update_queue(channel):
        try:
            method_frame, properties, body = channel.basic_get(queue='email_queue_2')
            messages_processed = 0
            while method_frame and messages_processed < MAX_MESSAGES_PER_CYCLE:
                message = body.decode()
                queue_listbox.insert(tk.END, message)
                channel.basic_ack(method_frame.delivery_tag)

                messages_processed += 1
                method_frame, properties, body = channel.basic_get(queue='email_queue_2')

            root.after(1000, update_queue, channel)
        except Exception as e:
            print("Error al actualizar la cola:", str(e))

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='email_queue_1', durable=True)
        channel.queue_declare(queue='email_queue_2', durable=True)  # Declarar la cola 'email_queue_2'

        root = tk.Tk()
        root.title("Email 2")

        message_label = tk.Label(root, text="Enter message:")
        message_label.pack()

        message_entry = tk.Entry(root, width=30)
        message_entry.pack()

        send_button = tk.Button(root, text="Send", command=send_message)
        send_button.pack()

        queue_label = tk.Label(root, text="Message Queue:")
        queue_label.pack()

        queue_listbox = tk.Listbox(root, width=50)
        queue_listbox.pack()

        update_queue(channel)

        root.mainloop()
    except Exception as e:
        print("Error general:", str(e))

if __name__ == "__main__":
    start_email_2()
