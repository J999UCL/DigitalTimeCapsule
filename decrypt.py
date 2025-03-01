import os
import hashlib
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime, inverse

# Decrypt file using AES key
def decrypt_file(file_path, key, iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    with open(file_path, "wb") as f:
        f.write(plaintext)
    return plaintext

# Solve the RSA-based time-lock puzzle (decryption is slow)
def solve_rsa_puzzle(N, x, t):
    x_final = x
    for _ in range(t):  # Perform sequential squaring
        x_final = pow(x_final, 2, N)
    return x_final


# Main function to decrypt with time-lock
def time_lock_decrypt(file_path, N, x, t, masked_key, iv, ciphertext):
    x_final = solve_rsa_puzzle(N, x, t)  # Slow decryption process
    aes_key = bytes(a ^ b for a, b in zip(masked_key, hashlib.sha256(x_final.to_bytes(256, 'big')).digest()))
    decrypt_file(file_path, aes_key, iv, ciphertext)
    print("File successfully decrypted!")

N= input()
x= input()
t = input()
masked_key = input()
iv = input()
ciphertext = input()
print("Solving RSA time-lock puzzle and decrypting...")
time_lock_decrypt("decrypted_secret.txt", N, x, t, masked_key, iv, ciphertext)