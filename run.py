import os
import json
import time
from Crypto.Util.number import getPrime

from encrypt_img import time_lock_encrypt, save_decryption_info
from decrypt_img import load_decryption_info, time_lock_decrypt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time

import pygame
import numpy as np

def estimate_steps(minutes):
    # Convert minutes to seconds
    total_seconds = minutes * 60

    # Measure the time for a single squaring operation

    prime_bits = 1024  # Use 1024-bit primes for security
    p = getPrime(prime_bits)
    q = getPrime(prime_bits)
    N = p * q  # RSA modulus (publicly shared)

    phi = (p - 1) * (q - 1)
    t = 1000
    x = int.from_bytes(os.urandom(32), 'big')  # Random base for exponentiation
    e = pow(2,t,phi) # Efficient modular exponentiation to get exponent
    x_final = x

    start_time = time.time()
    for _ in range(t):
        x_final = pow(x_final, e, N)
    end_time = time.time()

    single_squaring_time = (end_time - start_time) / t

    # Estimate the number of steps
    t = total_seconds / single_squaring_time
    return int(t)



def main():
    image_path = input("Enter the path to the image: ")
    t = int(input("Enter the time period (number of steps): "))
    #
    # minutes = t
    # t = estimate_steps(minutes)
    # print(f"Estimated steps for {minutes} minutes: {t}")


    # Encrypt the image
    N, x, t, masked_key, iv, ciphertext, boids, width, height = time_lock_encrypt(image_path, t)
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"{image_path} has been deleted.")
    else:
        print(f"{image_path} does not exist.")
    save_decryption_info("decrypt.txt", N, x, t, masked_key, iv, ciphertext, boids, width, height)
    print("Image encrypted and original deleted. Starting decryption...")

    # Decrypt and show progress
    N, x, t, masked_key, iv, ciphertext, boids, width, height = load_decryption_info("decrypt.txt")
    start_time = time.time()
    positions_over_time, colors, width, height = time_lock_decrypt(
        "decrypted_image.png", N, x, t, masked_key, iv, ciphertext, boids, width, height
    )
    end_time = time.time()

    print("Time taken is: "+str(end_time-start_time))


    # Animation
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')
    scatter = ax.scatter(positions_over_time[0][:, 0], positions_over_time[0][:, 1], c=colors, marker='s', s=1)

    def update(frame):
        scatter.set_offsets(frame)
        if frame is positions_over_time[-1]:
            ani.event_source.stop()
            print("Decryption complete.")
        return scatter,

    ani = FuncAnimation(fig, update, frames=positions_over_time, interval=10, blit=True)
    plt.show()


if __name__ == "__main__":
    main()