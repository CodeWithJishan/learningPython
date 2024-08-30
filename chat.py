

import subprocess
import threading
import random
import string
import getpass

# Generate a random key for encryption
key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
port = 1234
compromise_password = "cookie10"  # Set your compromise password here

def verify_password():
    """Prompt the user to enter the compromise password and verify it."""
    for _ in range(3):  # Allow up to 3 attempts
        entered_password = getpass.getpass("Enter your compromise password: ")
        if entered_password == compromise_password:
            print("Password verified. Chat unlocked.")
            return True
        else:
            print("Incorrect password. Try again.")
    print("Too many incorrect attempts. Exiting...")
    return False

def start_listener():
    """Start the Cryptcat listener process to receive messages."""
    listener_command = f"cryptcat -k {key} -l -p {port}"
    try:
        print(f"Listening on port {port} with encryption key: {key}")
        # Run the listener in a subprocess
        subprocess.run(listener_command, shell=True)
    except Exception as e:
        print(f"Error starting listener: {e}")

def send_message(target_ip):
    """Send messages to the target IP."""
    while True:
        try:
            # Input message to send
            message = input("You: ")
            if message.lower() == "exit":
                print("Exiting chat...")
                break
            # Send the message using Cryptcat
            subprocess.run(f"echo {message} | cryptcat -k {key} {target_ip} {port}", shell=True)
        except Exception as e:
            print(f"Error sending message: {e}")
            break

def main():
    # Verify the user's password before starting chat
    if not verify_password():
        return  # Exit if the password verification fails
    
    # Get the target IP address to connect to
    target_ip = input("Enter the IP address to connect to: ")
    
    # Start listener in a separate thread to handle incoming messages
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()
    
    # Start sending messages
    send_message(target_ip)

if __name__ == "__main__":
    main()

