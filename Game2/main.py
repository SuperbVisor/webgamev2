import pygame
import sys
import math
from random import randint
from pygame import mixer

from pygame.constants import K_LEFT, KEYDOWN
pygame.init()

screen = pygame.display.set_mode((800,600))



font = pygame.font.Font("Game2/font/GameOfSquids.ttf" , 25)
fontX = 10
fontY = 10

bullet_state = None


def showHiScore():  
      fileo = open("Game2/highscore.txt" )
      hiscore_value = fileo.readline()
      hiscore = font.render("High-Score : " + str(hiscore_value) , True , (255,255,255))
      screen.blit(hiscore , (500,10))
 
def showScore(x,y,score_value):
     score = font.render("Score : " + str(score_value), True , (255,255,255))
     screen.blit(score , (x,y))
 
 
def isCollision(enemyX , enemyY , bulletX , bulletY):
     dist = math.sqrt(math.pow((enemyX - bulletX),2) + math.pow((bulletY - enemyY),2))
     if dist<35:
         return True
     else:
         return False
 
def player(x,y,playerImg):
     screen.blit(playerImg , (x, y))
 
def bullet():
      global bullet_state
      bullet_state = "fire"
     #  screen.blit(bulletImg , (x, y))
  
def enemy(x,y,enemyImg):
     screen.blit(enemyImg , (x, y))
 



pygame.display.set_caption("Space Shooter Game")
    
icon = pygame.image.load("Game2/images/logo.jpg")

pygame.display.set_icon(icon)


def main():
    global bullet_state
        
    mixer.music.load("Game2/music/background.wav")
    mixer.music.play(1000)  #-1 for infinte playing of the song
    
    
    over = False
    score_value = 0
    fileo = open("Game2/highscore.txt" )
    hiscore_value = fileo.readline()
    
    
    backgroundImg = pygame.image.load("Game2/images/background.png")
    backgroundX = 0
    backgroundY = 0
    
    
    playerImg = pygame.image.load("Game2/images/player.png")
    playerX = 370
    playerY = 500  
    playerX_change = 0
    
    
    ii=0
    j=0

    
    
    bulletImg = pygame.image.load("Game2/images/bullet.png") 
    bulletX = 0
    bulletY = 500
    bulletY_change = 10
    bullet_state = "ready"
    
    
    enemyImg = []
    enemyImg.append(pygame.image.load("Game2/enemy/1.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/1.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/3.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/4.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/2.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/3.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/2.png"))
    enemyImg.append(pygame.image.load("Game2/enemy/4.png"))
    
    enemyX = []
    enemyY = []
    enemyX_change = []
    enemyY_change = []
    number_of_enemies = 8
    for i in range(number_of_enemies):
            enemyX.append(randint(0,720))
            enemyY.append(randint(10,150))
            enemyX_change.append(2)
            enemyY_change.append(0)
    
    
    blastImg = pygame.image.load("Game2/images/blast.png")
    
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_LEFT:
                      playerX_change = -4
                if event.key == pygame.K_RIGHT:
                     playerX_change = 4
                if event.key == pygame.K_SPACE:
                    if bullet_state is "ready":
                      bullet_sound = mixer.Sound("Game2/music/laser.wav")
                      bullet_sound.play()
                      bulletX = playerX - 5
                      bullet()
            if event.type == pygame.MOUSEBUTTONDOWN:
                       pos = pygame.mouse.get_pos()
                    #    print(replayImg.get_rect().collidepoint(pos))
                       if (pos[0]>330 and pos[0]<422) and (pos[1]>340 and pos[1]<372):
                           return 
                    
            if event.type == pygame.KEYUP:
                    if event.key == K_LEFT or event.key == pygame.K_RIGHT:
                        playerX_change = 0
              
    
        screen.blit(backgroundImg , (0, 0))
        
        # print(playerX)
          
        if bullet_state is "fire":
            screen.blit(bulletImg , (bulletX , bulletY))
            bulletY -= bulletY_change
            if bulletY == 0:
                bullet_state = "ready"
                bulletY = 500
                i =0
    
            
    
        if playerX<0:
            playerX=0
        elif playerX>743:
            playerX = 743
        else:
            playerX += playerX_change
        player(playerX,playerY,playerImg)
        
        for i in range(number_of_enemies): 
            if enemyY[i]>450 : 
                for j in range(number_of_enemies):
                    enemyY[j] = 2000
                GAMF = pygame.font.Font("Game2/font/GameOfSquids.ttf", 64)
                gameover = GAMF.render("GAME OVER " , True , (255,255,255))
                screen.blit(gameover , (200,250))
                mixer.music.stop()
                if not over:
                   gameo = mixer.Sound("Game2/music/gameover.mp3")
                   gameo.play()
                   over = True
                gameo = font.render("RESTART" , True , (200,200,200))
                screen.blit(gameo , (330,340))
                break
                
            
        
                    
            if ii==0 and j==0:     
               enemyY_change[i] = .3
            if score_value > 50 and score_value<=150 and ii==0:
                enemyY_change = [z+.1 for z in enemyY_change]
                ii=1
                # print(enemyY_change)
            if score_value > 150  and j==0:
                enemyY_change = [z+.3 for z in enemyY_change]
                j=1
                # print(enemyY_change)
                      
            enemyY[i] += enemyY_change[i];
        
            # if enemyX[i]>730:
            #    enemyY_change[i] = -200
            #    enemyY[i] += 30
            # elif enemyX[i]<=0:
            #    enemyY_change[i] = 200
            #    enemyY[i] += 30 
            enemy(enemyX[i],enemyY[i],enemyImg[i])
        
            collision = isCollision(enemyX[i] , enemyY[i] ,  bulletX , bulletY)         
            if collision:
                collision_sound = mixer.Sound("Game2/music/explosion.wav")
                collision_sound.play()
                screen.blit(blastImg , (enemyX[i] , enemyY[i]))
                bullet_state = "ready"
                bulletY = 500
                score_value += 1
                if score_value > int(hiscore_value):
                    file = open("Game2/highscore.txt", "w")
                    file.write(str(score_value)) 
                    file.close() 
                enemyX[i] = randint(0,720)
                enemyY[i] = randint(10,150)
                
        showScore(fontX,fontY,score_value)
        showHiScore()
  
    

        pygame.display.update()

   
while True:
      main()
      