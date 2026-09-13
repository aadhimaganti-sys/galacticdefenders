import socket
import pygame
from settings import *
import state

NETWORK_PORT = 5555
CLOUD_SERVER_IP = "127.0.0.1"  
GLOBAL_LOBBY_CODE = "SECRET_BASE_1"

udp_sock = None
network_target = None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception: 
        return "127.0.0.1"

def draw_text_local(text, font, color, x, y, surface):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, text_surface.get_rect(center=(x, y)))

def host_infinite_lan(screen, clock, mode_choice):
    global udp_sock
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", NETWORK_PORT))
    udp_sock.setblocking(False)
    local_ip = get_local_ip()

    while True:
        screen.fill(BLACK)
        draw_text_local("HOSTING INFINITE LAN LOBBY", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, screen)
        draw_text_local(f"Host IP Address: {local_ip}", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, screen)
        draw_text_local("Press ENTER to start game. ESC to cancel.", FONT_SMALL, LIGHT_GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return "HOME"
                elif event.key == pygame.K_RETURN: 
                    return "LAN_HOST_" + mode_choice
                    
        # Apply speedhack state tick modifications
        clock.tick(int(FPS * state.GAME_SPEED))

def join_infinite_lan(screen, clock):
    global udp_sock, network_target
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(False)
    input_ip = ""

    while True:
        screen.fill(BLACK)
        draw_text_local("JOIN LAN LOBBY", FONT_LARGE, CYAN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, screen)
        draw_text_local("Enter Host IP:", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, screen)
        draw_text_local(input_ip + "_", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return "HOME"
                elif event.key == pygame.K_RETURN:
                    network_target = (input_ip, NETWORK_PORT)
                    return "LAN_JOIN"
                elif event.key == pygame.K_BACKSPACE: 
                    input_ip = input_ip[:-1]
                else:
                    if event.unicode.isnumeric() or event.unicode == ".": 
                        input_ip += event.unicode
                        
        clock.tick(int(FPS * state.GAME_SPEED))

def join_global_cloud(screen, clock):
    global udp_sock, network_target
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setblocking(False)
    input_address = ""

    while True:
        screen.fill(BLACK)
        draw_text_local("JOIN GLOBAL CLOUD LOBBY", FONT_LARGE, MAGENTA, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, screen)
        draw_text_local("Enter Server IP or Ngrok Link:", FONT_MEDIUM, YELLOW, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, screen)
        draw_text_local(input_address + "_", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT_PROGRAM"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return "HOME"
                elif event.key == pygame.K_RETURN:
                    target_ip = input_address
                    target_port = NETWORK_PORT
                    
                    if "tcp://" in target_ip: 
                        target_ip = target_ip.replace("tcp://", "")
                    if ":" in target_ip:
                        parts = target_ip.split(":")
                        target_ip = parts[0]
                        try: 
                            target_port = int(parts[1])
                        except ValueError: 
                            pass
                            
                    network_target = (target_ip, target_port)
                    return "JOIN_CLOUD"
                    
                elif event.key == pygame.K_BACKSPACE: 
                    input_address = input_address[:-1]
                elif event.unicode.isprintable(): 
                    input_address += event.unicode
                    
        clock.tick(int(FPS * state.GAME_SPEED))