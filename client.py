import socket
import threading
import tkinter as tk

# Server configuration
SERVER_HOST = '127.0.0.1'  # Server IP address
SERVER_PORT = 5001  # Server port number

class Client:
    def __init__(self):
        self.server_socket = None
        self.gui_thread = None
        self.clients = []  # Store connected clients

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((SERVER_HOST, SERVER_PORT))

        self.gui_thread = threading.Thread(target=self.create_gui)
        self.gui_thread.start()

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                data = self.server_socket.recv(1024).decode('utf-8')
                if data:
                    self.update_chat_window(data)
            except ConnectionResetError:
                print('Disconnected from the server.')
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.update_chat_window(f'You: {message}')
            self.server_socket.send(message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def create_gui(self):
        root = tk.Tk()
        root.title('Client')

        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True)

        chat_frame = tk.Frame(frame, bg='white')
        chat_frame.pack(side='left', fill='both', expand=True)

        chat_label = tk.Label(chat_frame, text='Chat')
        chat_label.pack()

        self.chat_text = tk.Text(chat_frame, state='disabled')
        self.chat_text.pack(fill='both', expand=True)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side='bottom', fill='x')

        self.message_entry = tk.Entry(bottom_frame)
        self.message_entry.pack(side='left', fill='x', expand=True)
        self.message_entry.bind('<Return>', self.send_message)

        send_button = tk.Button(bottom_frame, text='Send', command=self.send_message)
        send_button.pack(side='right')

        root.mainloop()

    def update_chat_window(self, message):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(tk.END, f'{message}\n')
        self.chat_text.configure(state='disabled')

if __name__ == '__main__':
    client = Client()
    client.start()
