import pygame

pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotated Screen")
clock = pygame.time.Clock()

# Create a separate surface to draw all game elements onto
# This is the "world" surface that will be rotated
original_surface = pygame.Surface((WIDTH, HEIGHT))
# Make the background transparent if you don't want a solid color border
# If using a solid background, use .fill() instead
# original_surface.set_colorkey((0, 0, 0)) 

# Example: Draw a simple object on the original surface
font = pygame.font.SysFont(None, 100)
text = font.render("Rotated World", True, (255, 255, 0))
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
# Draw to the original surface, not the screen directly
original_surface.blit(text, text_rect) 

angle = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Increment the angle on key press
                angle = (angle + 90) % 360

    # Clear the actual display screen
    screen.fill((0, 0, 0))

    # --- Draw all game logic to original_surface before rotation (not shown for brevity) ---

    # Rotate the original surface
    # It is best practice to always rotate the original surface to avoid quality loss
    rotated_surface = pygame.transform.rotate(original_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Blit the rotated surface to the main display screen
    screen.blit(rotated_surface, rotated_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
