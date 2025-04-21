import json
import numpy as np
import time
import hashlib
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
from Crypto.Util.Padding import  unpad

def decrypt_file(output_path, key, iv, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    with open(output_path, 'wb') as f:
        f.write(plaintext)

# Decryption Function
def time_lock_decrypt(decrypted_path, N, x, t, masked_key, iv, ciphertext, boids, width, height):
    start_time = time.time()
    # Ensure inputs are integers
    N = int(N)
    x = int(x)
    t = int(t)
    scrambled_positions = np.array([(x_pos, y_pos) for (x_pos, y_pos, _) in boids], dtype=float)
    colors = np.array([color for (_, _, color) in boids])
    original_positions = np.array([(j, i) for i in range(height) for j in range(width)], dtype=float)
    current_positions = scrambled_positions.copy()
    deltas = (original_positions - scrambled_positions) / t
    positions_over_time = [current_positions.copy()]
    x_final = x
    for step in range(t):
        if not isinstance(x_final, int) or not isinstance(N, int):
            raise TypeError(f"x_final ({type(x_final)}) or N ({type(N)}) is not an integer at step {step}")
        x_final = pow(x_final, 2, N) # Modular squaring
        current_positions += deltas
        positions_over_time.append(current_positions.copy())
    aes_key = bytes(a ^ b for a, b in zip(masked_key, hashlib.sha256(x_final.to_bytes(256, 'big')).digest()))
    decrypt_file(decrypted_path, aes_key, iv, ciphertext)
    end_time = time.time()
    print("Decryption complete: " + str(end_time-start_time))
    return positions_over_time, colors, width, height

def load_decryption_info(file_path):
    with open(file_path, 'r') as f:
        decryption_info = json.load(f)

    N = int(decryption_info["N"])
    x = int(decryption_info["x"])
    t = int(decryption_info["t"])
    masked_key = bytes.fromhex(decryption_info["masked_key"])
    iv = bytes.fromhex(decryption_info["iv"])
    ciphertext = bytes.fromhex(decryption_info["ciphertext"])
    boids = decryption_info["boids"]
    width = int(decryption_info["width"])
    height = int(decryption_info["height"])

    return N, x, t, masked_key, iv, ciphertext, boids, width, height

def main():
    # Example usage
    file_path = 'decrypt.txt'
    N, x, t, masked_key, iv, ciphertext, boids, width, height = load_decryption_info(file_path)


    positions_over_time, colors, width, height = time_lock_decrypt(
        "decrypted_image.png", N, x, t, masked_key, iv, ciphertext, boids, width, height
    )

if __name__ == "__main__":
    main()