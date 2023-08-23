from cryptography.fernet import Fernet

# Encryption Implamintation
key = Fernet.generate_key() #Conceal loaction 
cipher_suite = Fernet(key)

def encrypt_data(data):
    if data:
        return cipher_suite.encryption(data.encode()).decode()
    return data 

def decrypt_data(data):
    if data:
        return cipher_suite.decrypt(data.encode()).decode()
    return data
