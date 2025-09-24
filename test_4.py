import cv2
import pygame
import math
import time

# ------------------------
# CONFIGURATION
# ------------------------
VIDEO_PATH = "lathe_video.mp4"  # Replace with your video file name
SPINDLE_SPEED = 500  # RPM
DOC = 1.0            # Depth of cut per second (mm/s)
FPS = 60

# ------------------------
# VIDEO CAPTURE
# ------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise IOError("Error: Could not open video file.")

# ------------------------
# PYGAME SETUP
# ------------------------
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lathe Digital Twin - Feed, Speed, Radius")
clock = pygame.time.Clock()

# ------------------------
# WORKPIECE & TOOL STATE
# ------------------------
workpiece_radius = 80
workpiece_length = 300
tool_x = WIDTH // 2 + workpiece_length // 2 - 20
tool_y = HEIGHT // 2 - workpiece_radius - 20
rotation_angle = 0

# ------------------------
# TIMING & CONTROL
# ------------------------
RAD_PER_FRAME = (SPINDLE_SPEED / 60.0) * (2 * math.pi) / FPS
paused = False
font = pygame.font.SysFont("Arial", 20)

last_tool_x = tool_x
feed_speed = 0.0
last_time = time.time()

# ------------------------
# MAIN LOOP
# ------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # toggle pause

    # --- Read and process video frame ---
    if not paused:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = (0, 100, 100)
        upper_red = (10, 255, 255)
        mask = cv2.inRange(hsv, lower_red, upper_red)
        moments = cv2.moments(mask)

        if moments["m00"] > 0:
            cx = int(moments["m10"] / moments["m00"])
            video_width = frame.shape[1]

            # Compute feed speed
            current_tool_x = (cx / video_width) * (WIDTH - workpiece_length) + (WIDTH // 2 - workpiece_length // 2)
            now = time.time()
            feed_speed = abs(current_tool_x - last_tool_x) / (now - last_time + 1e-6)  # px/s
            last_tool_x = current_tool_x
            last_time = now

            tool_x = current_tool_x

        # Show the video + mask for debugging
        cv2.imshow("Video Feed", frame)
        cv2.imshow("Red Mask", mask)

    # --- Workpiece rotation ---
    if not paused:
        rotation_angle += RAD_PER_FRAME
        rotation_angle %= 2 * math.pi

    # --- Cutting Logic: reduce radius when tool touches workpiece ---
    tool_rect = pygame.Rect(tool_x, tool_y, 20, 20)
    workpiece_rect = pygame.Rect(WIDTH // 2 - workpiece_length // 2,
                                 HEIGHT // 2 - workpiece_radius,
                                 workpiece_length,
                                 workpiece_radius * 2)
    if tool_rect.colliderect(workpiece_rect) and not paused:
        workpiece_radius -= DOC * dt
        if workpiece_radius < 20:
            workpiece_radius = 20  # stop at min diameter

    # --- Draw workpiece ---
    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (WIDTH // 2 - workpiece_length // 2, HEIGHT // 2 - workpiece_radius,
         workpiece_length, workpiece_radius * 2),
        border_radius=10
    )

    # --- Draw rotating red line ---
    face_center = (WIDTH // 2 - workpiece_length // 2, HEIGHT // 2)
    line_length = workpiece_radius * 0.5
    line_end = (
        face_center[0] + line_length * math.cos(rotation_angle),
        face_center[1] + line_length * math.sin(rotation_angle)
    )
    pygame.draw.line(screen, (255, 100, 100), face_center, line_end, 3)

    # --- Draw tool ---
    pygame.draw.rect(screen, (100, 255, 100), (tool_x, tool_y, 20, 20))

    # --- Display Info ---
    info_text = font.render(
        f"Spindle: {SPINDLE_SPEED} RPM | Feed: {feed_speed:.2f} px/s | Radius: {workpiece_radius:.1f} mm",
        True,
        (255, 255, 255)
    )
    screen.blit(info_text, (20, 20))

    if paused:
        pause_text = font.render("PAUSED", True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH - 120, 20))

    pygame.display.flip()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False

cap.release()
cv2.destroyAllWindows()
pygame.quit()