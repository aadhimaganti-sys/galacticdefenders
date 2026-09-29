import pygame
import main
import state

pygame.init()
SCREEN = pygame.display.set_mode((800, 600))
state.SHIP_VIEW_MODE = True

try:
    cw, ch = SCREEN.get_width(), SCREEN.get_height()
    ccolor = (30, 30, 35)
    pygame.draw.polygon(SCREEN, ccolor, [(0, 0), (cw * 0.15, 0), (cw * 0.05, ch), (0, ch)])
    pygame.draw.polygon(SCREEN, ccolor, [(cw, 0), (cw * 0.85, 0), (cw * 0.95, ch), (cw, ch)])
    pygame.draw.polygon(SCREEN, ccolor, [(0, ch), (cw, ch), (cw, ch * 0.85), (0, ch * 0.85)])
    pygame.draw.polygon(SCREEN, ccolor, [(0, 0), (cw, 0), (cw * 0.85, ch * 0.08), (cw * 0.15, ch * 0.08)])
    cx, cy = cw // 2, ch // 2
    pygame.draw.circle(SCREEN, (0, 255, 0), (cx, cy), 15, 1)
    pygame.draw.line(SCREEN, (0, 255, 0), (cx - 25, cy), (cx - 10, cy), 1)
    pygame.draw.line(SCREEN, (0, 255, 0), (cx + 10, cy), (cx + 25, cy), 1)
    pygame.draw.line(SCREEN, (0, 255, 0), (cx, cy - 25), (cx, cy - 10), 1)
    pygame.draw.line(SCREEN, (0, 255, 0), (cx, cy + 10), (cx, cy + 25), 1)
    pygame.draw.line(SCREEN, (0, 200, 255), (cw * 0.3, ch * 0.9), (cw * 0.7, ch * 0.9), 2)
    print("Draw successful!")
except Exception as e:
    print("Error:", e)

