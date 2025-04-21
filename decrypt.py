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

N= 13366966701982412265977528757330774727059276660217379363670147263189506631344494364104643771845675446036089446421933704675018015540842050225498075825951242600473328558277057971218271254406987135509282765538489396877309524993032462350050116161306835013147377710895532932146449044187432471149357220738129035124530284466882889087363573163486521852961926824004721824921168093624764273678954096917540847478255772757548093787404338716639877292096972538571421294947390098309520517600284508854808322017953516814101578823896667208136027862723565956572950501613981304956467075754107274975605025960803411004720334794489647237379
x= 94874706489403701002911608915800387975291797465920176947270639514842581371193
t = 1000000
masked_key = b'\xaf`\xddf\xc2\x9b\xc7\\\xd0{B\xb7N\xc1\x86r\xd3w\xba\x0f\xfd\x92r\xf0ok\xfas\xe5\x08\xfa\xbe'
iv = b'+v\xfe)!NE\xea%\xc2f6m\nV2'
ciphertext = b'\xa4/\x9c\xb9\xce\x8bT\xbd \x8eFK\t\xb9`\xbb&o\xac\xef\x8b\r\x9d\x9a`O\x8fi\xe8J\x02\xac \xe7j\xfd\x99z\x9e\xae`\x19u\xc6\xc3\xaf\xb3['
print("Solving RSA time-lock puzzle and decrypting...")
time_lock_decrypt("decrypted_secret.txt", N, x, t, masked_key, iv, ciphertext)