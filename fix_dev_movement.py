import re

with open('interior.py', 'r') as f:
    content = f.read()

# Replace the movement logic
movement_pattern = r'if keys\[pygame\.K_LEFT\].*?state\.astronaut_y \+= speed'
new_movement = '''dev_access = keys[pygame.K_d] and keys[pygame.K_e] and keys[pygame.K_v]
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: state.astronaut_x -= speed
    if keys[pygame.K_RIGHT] or (keys[pygame.K_d] and not dev_access): state.astronaut_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]: state.astronaut_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: state.astronaut_y += speed'''
content = re.sub(movement_pattern, new_movement, content, flags=re.DOTALL)

# Since dev_access is now defined earlier, we can remove the duplicate dev_access = ...
duplicate_dev = r'dev_access = keys\[pygame\.K_d\] and keys\[pygame\.K_e\] and keys\[pygame\.K_v\]\s*if room_x < -1'
content = re.sub(duplicate_dev, 'if room_x < -1', content, flags=re.DOTALL)

with open('interior.py', 'w') as f:
    f.write(content)
