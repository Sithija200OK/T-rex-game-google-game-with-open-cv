import cv2
import mediapipe as mp
import pygame
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (211, 211, 211)  # Light Gray Background
GROUND = HEIGHT - 60
JUMP_HEIGHT = 150

# Load Images
dino_img = pygame.image.load("dino.png")  # Dino standing image
dino_img = pygame.transform.scale(dino_img, (50, 50))  # Adjust size

cactus_img = pygame.image.load("cactus.png")
cactus_img = pygame.transform.scale(cactus_img, (40, 50))

cloud_img = pygame.image.load("cloud.png")
cloud_img = pygame.transform.scale(cloud_img, (100, 50))

background_img = pygame.image.load("ground.png")  # Load your background image
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))  # Scale it to screen size

# Dino Class
class Dino:
    def __init__(self):
        self.x = 50
        self.y = GROUND
        self.width = 50
        self.height = 50
        self.velocity = 0
        self.is_jumping = False
        self.is_crouching = False
    
    def jump(self):
        if not self.is_jumping:
            self.velocity = -15
            self.is_jumping = True
    
    def crouch(self):
        self.is_crouching = True
    
    def update(self):
        if self.is_jumping:
            self.y += self.velocity
            self.velocity += 1  # Gravity
            if self.y >= GROUND:
                self.y = GROUND
                self.is_jumping = False
        if self.is_crouching:
            self.height = 30
        else:
            self.height = 50
        self.is_crouching = False

    def draw(self, screen):
        screen.blit(dino_img, (self.x, self.y))  # Draw the dino

# Obstacle Class
class Obstacle:
    def __init__(self):
        self.x = WIDTH
        self.y = GROUND
        self.width = 40
        self.height = 50
        self.velocity = 5
    
    def update(self):
        self.x -= self.velocity
        if self.x < -self.width:
            self.x = WIDTH + random.randint(200, 400)
    
    def draw(self, screen):
        screen.blit(cactus_img, (self.x, self.y))

# Collision Detection
def check_collision(dino, obstacle):
    return (dino.x < obstacle.x + obstacle.width and
            dino.x + dino.width > obstacle.x and
            dino.y < obstacle.y + obstacle.height and
            dino.y + dino.height > obstacle.y)

# Initialize Game Objects
dino = Dino()
obstacles = [Obstacle(), Obstacle()]  # Two obstacles in the game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand-Controlled Dino Run")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
score = 0
game_over = False

# Capture Video
cap = cv2.VideoCapture(0)

running = True
while running:
    screen.blit(background_img, (0, 0))  # Set the background image for every frame
    
    if not game_over:
        # Read Video Frame
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_y = hand_landmarks.landmark[9].y  # Middle of the hand
                
                if hand_y < 0.4:
                    dino.jump()
                elif hand_y > 0.6:
                    dino.crouch()
                
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Update Game Objects
        dino.update()
        for obstacle in obstacles:
            obstacle.update()
        score += 1
        
        # Increase speed of obstacles as score increases
        if score % 500 == 0 and score > 0:
            for obstacle in obstacles:
                obstacle.velocity += 1
        
        # Collision Check
        for obstacle in obstacles:
            if check_collision(dino, obstacle):
                game_over = True
    
    # Draw Cloud in the Upper Right
    screen.blit(cloud_img, (WIDTH - 120, 20))  # Adjust as needed

    # Draw Game Objects
    dino.draw(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)
    
    # Draw Ground with Black Line and Dots (rough terrain)
    pygame.draw.line(screen, BLACK, (0, GROUND), (WIDTH, GROUND), 2)
    for i in range(0, WIDTH, 40):
        pygame.draw.circle(screen, BLACK, (i + random.randint(-10, 10), GROUND + random.randint(5, 15)), 2)

    # Display Score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    # Game Over Screen
    if game_over:
        game_over_text = font.render("Game Over! Press SPACE to Restart", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 4, HEIGHT // 2))
    
    pygame.display.update()
    
    # Show Webcam Feed
    cv2.imshow("Hand Tracking", frame)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                dino = Dino()
                obstacles = [Obstacle(), Obstacle()]
                score = 0
                game_over = False
    
    clock.tick(30)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
