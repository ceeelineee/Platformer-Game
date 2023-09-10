import pygame
import random
import time
from pygame.locals import *
from setup import *

pygame.init()
vec = pygame.math.Vector2

framesPerSec = pygame.time.Clock()
displaySurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumper")


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.shape = pygame.Surface((random.randint(50,100), 12))
        self.shape.fill(platform_color)
        self.rect = self.shape.get_rect(center = (random.randint(0,WIDTH-10),
                                                 random.randint(0, HEIGHT-30)))
        self.gotTouched = False
        self.velocity = random.randint(-1 , 1)
        self.inMotion = True
    
    def move(self):
        if self.inMotion == True:  
            self.rect.move_ip(self.velocity,0)
            if self.velocity > 0 and self.rect.left > WIDTH:
                self.rect.right = 0
            if self.velocity < 0 and self.rect.right < 0:
                self.rect.left = WIDTH
        if self.gotTouched:
            self.velocity = 0
                
        
        
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.shape = pygame.Surface((player_size, player_size))
        self.shape.fill(player_color)
        self.rect = self.shape.get_rect()
        self.pos = vec(30, 385)
        self.velocity = vec(0,0)
        self.acceleration = vec(0,0)
        self.in_air = False
        self.score = 0
        
    def move(self):
        self.acceleration = vec(0, 0.5)
        pressed_keys = pygame.key.get_pressed()
               
        if pressed_keys[K_LEFT]:
            self.acceleration.x = -ACCELERATION
        if pressed_keys[K_RIGHT]:
            self.acceleration.x = ACCELERATION 
            
        self.acceleration.x += self.velocity.x * FRICTION
        self.velocity += self.acceleration
        self.pos += self.velocity + 0.5 * self.acceleration
        
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
            
        self.rect.midbottom = self.pos
        
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.in_air:
            self.in_air = True
            self.velocity.y = -15
    
    def back_down(self):
        if self.in_air:
            if self.velocity.y < -3:
                self.velocity.y = -3
        
    def update(self):
        # self.move()
        hits = pygame.sprite.spritecollide(player , platforms, False)
        if player.velocity.y > 0: 
            if hits:
                if self.pos.y < hits[0].rect.bottom: 
                    if not hits[0].gotTouched:   
                        hits[0].gotTouched = True
                        self.score += 1           
                    self.pos.y = hits[0].rect.top +1
                    self.velocity.y = 0
                    self.in_air = False
        

# main game's entities
player = Player()
bottomPlatform = Platform()
bottomPlatform.shape = pygame.Surface((WIDTH, 20))
bottomPlatform.shape.fill((0,0,0))
bottomPlatform.rect = bottomPlatform.shape.get_rect(center = (WIDTH/2, HEIGHT - 10))
bottomPlatform.gotTouched = True
bottomPlatform.inMotion = False

all_sprites = pygame.sprite.Group()
all_sprites.add(bottomPlatform)
all_sprites.add(player)

platforms = pygame.sprite.Group()
platforms.add(bottomPlatform)

    

# level genration    
def check_platforms(platform, grouped):
    if pygame.sprite.spritecollideany(platform,grouped):
        return True
    else:
        for entity in grouped:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 50) and (abs(platform.rect.bottom - entity.rect.top) < 50):
                return True
        C = False
        
def platform_generator():
    while len(platforms) < HARD :
        width = random.randrange(50,100)
        p  = Platform()      
        C = True
        while C:           
             p = Platform()
             p.rect.center = (random.randrange(0, WIDTH - width),
                             random.randrange(-50, 0))
             C = check_platforms(p, platforms)
        platforms.add(p)
        all_sprites.add(p)

# initial platforms
for x in range(random.randint(4,5)):
    C = True
    pl = Platform()
    while C:
        pl = Platform()
        C = check_platforms(pl, platforms)
    platforms.add(pl)
    all_sprites.add(pl)


# main loop
while True:
    f = pygame.font.SysFont("Verdana", 20) 
    
    player.update()
    if player.rect.top <= HEIGHT / 3:
        player.pos.y += abs(player.velocity.y)
        for platform in platforms:
            platform.rect.y += abs(player.velocity.y)
            if platform.rect.top >= HEIGHT:
                platform.kill()
    if player.rect.top > HEIGHT:
        for entity in all_sprites:
            entity.kill()
            time.sleep(1)
            displaySurface.fill((255,0,0))
            game_over  = f.render("GAME OVER!", True, (0,0,0))  
            displaySurface.blit(game_over, (WIDTH/2 - 60, HEIGHT/2))
            pygame.display.update()
            time.sleep(2)
            pygame.quit()
            
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.KEYUP:    
            if event.key == pygame.K_SPACE:
                player.back_down()
    
    platform_generator()
    displaySurface.fill((255,255,255))   
    g  = f.render(str(player.score), True, (255,0,0))  
    displaySurface.blit(g, (WIDTH/2, 10))
    
    for entity in all_sprites:
        displaySurface.blit(entity.shape, entity.rect)
        entity.move()

    pygame.display.update()
    framesPerSec.tick(FPS)