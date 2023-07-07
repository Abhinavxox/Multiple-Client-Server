import socket
import threading
import tkinter as tk
from datetime import datetime
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
import random
from datetime import datetime
# Server configuration
SERVER_HOST = '127.0.0.1'  # Server IP address
SERVER_PORT = 5001  # Server port number

class Client:
    def __init__(self):
        self.server_socket = None
        self.gui_thread = None
        self.clients = []  # Store connected clients

    def decrypt(self, enc):
        password = enc.split("---")[1]
        private_key = hashlib.sha256(password.encode("utf-8")).digest()
        enc = base64.b64decode(enc)
        iv = enc[:16]
        ciphertext = enc[16:]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext).decode("utf-8")
        try:
            unpadded = self.unpad(decrypted)  # Remove padding from decrypted message
            return unpadded
        except ValueError:
            # Correct underpadding error by adding appropriate padding
            corrected = self.add_padding(decrypted)
            return corrected

    def unpad(self, padded_message):
        padding_size = ord(padded_message[-1])
        if padding_size > 0 and padding_size <= AES.block_size:
            unpadded = padded_message[:-padding_size]
            return unpadded
        else:
            raise ValueError("Invalid padding on message.")

    def add_padding(self, message):
        padding_size = AES.block_size - (len(message) % AES.block_size)
        padding = chr(padding_size) * padding_size
        padded = message + padding
        return padded

    def encrypt_message(self, message, passkey):
        private_key = hashlib.sha256(passkey.encode("utf-8")).digest()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        padded_message = self.add_padding(message)  # Add padding to the message
        encrypted = cipher.encrypt(padded_message.encode("utf-8"))
        return base64.b64encode(iv + encrypted).decode()

    def get_send_time(self):
        return datetime.now().strftime("%H:%M")
    
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
                    address = data.split(":")[0]
                    message = data.split(":")[1]
                    data = address+f": {self.decrypt(message)}"
                    self.update_chat_window(data)
                    del data
            except ConnectionResetError:
                print('Disconnected from the server.')
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            key = str(random.randint(1000,9999))
            message_encr = self.encrypt_message(f'{message} ({self.get_send_time()})',key)+f"---{key}"
            self.update_chat_window(f'You: {message} ({self.get_send_time()})')
            self.server_socket.send(message_encr.encode('utf-8'))
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
