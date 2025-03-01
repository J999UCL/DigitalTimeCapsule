import os
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime, inverse


# Generate a random AES key (256-bit)
def generate_aes_key():
    return os.urandom(32)


# Encrypt file using AES key
def encrypt_file(file_path, key):
    with open(file_path, "rb") as f:
        plaintext = f.read()
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return cipher.iv, ciphertext


# Decrypt file using AES key
def decrypt_file(file_path, key, iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    with open(file_path, "wb") as f:
        f.write(plaintext)
    return plaintext


# Generate an RSA-based time-lock puzzle
def create_rsa_puzzle(aes_key, t):
    prime_bits = 1024  # Use 1024-bit primes for security
    p = getPrime(prime_bits)
    q = getPrime(prime_bits)
    N = p * q  # RSA modulus (publicly shared)
    phi = (p - 1) * (q - 1)

    x = int.from_bytes(os.urandom(32), 'big')  # Random base for exponentiation
    e = pow(2, t, phi)  # Efficient modular exponentiation to get exponent
    x_final = pow(x, e, N)  # Compute x^(2^t) mod N (slow for decryption)

    masked_key = bytes(a ^ b for a, b in zip(aes_key, hashlib.sha256(x_final.to_bytes(256, 'big')).digest()))

    return N, x, t, masked_key, x_final


# Solve the RSA-based time-lock puzzle (decryption is slow)
def solve_rsa_puzzle(N, x, t):
    x_final = x
    for _ in range(t):  # Perform sequential squaring
        x_final = pow(x_final, 2, N)
    return x_final


# Main function to encrypt with time-lock
def time_lock_encrypt(file_path, t):
    aes_key = generate_aes_key()
    iv, ciphertext = encrypt_file(file_path, aes_key)
    N, x, t, masked_key, x_final = create_rsa_puzzle(aes_key, t)
    return N, x, t, masked_key, iv, ciphertext


# Main function to decrypt with time-lock
def time_lock_decrypt(file_path, N, x, t, masked_key, iv, ciphertext):
    x_final = solve_rsa_puzzle(N, x, t)  # Slow decryption process
    aes_key = bytes(a ^ b for a, b in zip(masked_key, hashlib.sha256(x_final.to_bytes(256, 'big')).digest()))
    decrypt_file(file_path, aes_key, iv, ciphertext)
    print("File successfully decrypted!")


# Example Usage
if __name__ == "__main__":
    FILE_TO_ENCRYPT = "secret.txt"
    DELAY_TIME = 1000000  # Number of sequential squarings

    print("Encrypting and creating time-lock...")
    N, x, t, masked_key, iv, ciphertext = time_lock_encrypt(FILE_TO_ENCRYPT, DELAY_TIME)
    if os.path.exists(file_path):
        os.remove(file_path)  # Removes the original file
    print(N)
    print(x)
    print(t)
    print(masked_key)
    print(iv)
    print(ciphertext)