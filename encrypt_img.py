from Crypto.Util.number import getPrime
from PIL import Image
import numpy as np
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

# AES Encryption/Decryption Helpers
def generate_aes_key():
    return os.urandom(32)

def encrypt_file(file_path, key):
    cipher = AES.new(key, AES.MODE_CBC)
    with open(file_path, 'rb') as f:
        data = f.read()
    padded_data = pad(data, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return cipher.iv, ciphertext

# Encryption Function
def time_lock_encrypt(image_path, t):
    image = Image.open(image_path)
    image_array = np.array(image)
    height, width = image.size[1], image.size[0]
    prime_bits = 1024  # Use 1024-bit primes for security
    p = getPrime(prime_bits)
    q = getPrime(prime_bits)
    N = p * q  # RSA modulus (publicly shared)

    phi = (p - 1) * (q - 1)

    x = int.from_bytes(os.urandom(32), 'big')  # Random base for exponentiation
    e = pow(2, t, phi)  # Efficient modular exponentiation to get exponent
    x_final = pow(x, e, N)
    # for i in range(t):
    #     x_final = pow(x_final, 2, N)
    boids = []
    for i in range(height):
        for j in range(width):
            seed = hashlib.sha256(str(x_final).encode() + str(i).encode() + str(j).encode()).digest()
            x_pos = int.from_bytes(seed[:4], 'big') / float(1 << 32) * width
            y_pos = int.from_bytes(seed[4:8], 'big') / float(1 << 32) * height
            color = tuple(image_array[i, j].astype(float) / 255.0)
            boids.append((x_pos, y_pos, color))
    aes_key = generate_aes_key()
    iv, ciphertext = encrypt_file(image_path, aes_key)
    masked_key = bytes(a ^ b for a, b in zip(aes_key, hashlib.sha256(x_final.to_bytes(256, 'big')).digest()))
    return N, x, t, masked_key, iv, ciphertext, boids, width, height

def save_decryption_info(file_path, N, x, t, masked_key, iv, ciphertext, boids, width, height):
    decryption_info = {
        "N": N,
        "x": x,
        "t": t,
        "masked_key": masked_key.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex(),
        "boids": boids,
        "width": width,
        "height": height
    }
    with open(file_path, 'w') as f:
        json.dump(decryption_info, f)


def main():
    # Main Execution
    image_path = "Luca.png"  # Your image file (e.g., 100x100 pixels)
    t = 100  # Number of steps
    N, x, t, masked_key, iv, ciphertext, boids, width, height = time_lock_encrypt(image_path, t)
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")
    save_decryption_info("decrypt.txt", N, x, t, masked_key, iv, ciphertext, boids, width, height)

if __name__ == "__main__":
    main()

