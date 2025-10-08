# player.py
import pygame



class Player:
    def __init__(self, x=100, y=100, w=80, h=80, speed=300.0, rot_speed=100.0):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0.0

        self.speed = speed
        self.slow_speed = 50
        self.normal_speed = speed
        self.boost_speed = self.normal_speed * 5
        self.rot_speed = rot_speed
        self.slow_rot_speed = rot_speed/2
        self.normal_rot_speed = rot_speed
        self.boost_rot_speed = self.normal_rot_speed * 2

        self.size = (w, h)
        self.fire = False
        self.live = 100
        self.score = 0
        self.guard = 0

        # ↓↓↓ HIER: Rechteck-Grafik durch Bild ersetzen ↓↓↓
        img = pygame.image.load("../textures/Player.png").convert_alpha()   # Pfad anpassen!
        # Falls die PNG größer/kleiner ist, auf self.size bringen:
        if img.get_size() != self.size:
            img = pygame.transform.scale(img, self.size)

        # Falls dein Sprite nach OBEN zeigt, einmalig -90°, damit 0° nach rechts ist:
        # (Weglassen, wenn dein Bild schon nach rechts zeigt.)
        img = pygame.transform.rotate(img, -90)

        # Basisbild, das später pro Frame rotiert wird
        self.base_image = img

        # Hitbox – kannst du an Bildgröße koppeln oder kompakt lassen
        self.hitbox_size = 24  # oder z.B. max(self.size)

    def handle_input(self, dt: float):
        keys = pygame.key.get_pressed()

        # Rotation
        if keys[pygame.K_LEFT]:
            self.angle -= self.rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.angle += self.rot_speed * dt

        # Forward / backward towards the view angle
        thrust = 0.0
        if keys[pygame.K_UP]:
            thrust += 1.0
        if keys[pygame.K_DOWN]:
            thrust -= 1.0

        if keys[pygame.K_b]:
            self.speed = self.boost_speed
            self.rot_speed = self.boost_rot_speed
        elif keys[pygame.K_v]:
            self.speed = self.slow_speed
            self.rot_speed = self.slow_rot_speed
        else:
            self.speed = self.normal_speed
            self.rot_speed = self.normal_rot_speed

        if keys[pygame.K_f]:
            self.fire = True
        else:
            self.fire = False

        heading = pygame.Vector2(1, 0).rotate(self.angle)  # 0° pointing in the right direction
        self.vel = heading * (thrust * self.speed)

    # in player.py (nur Update anpassen, Rest wie zuvor)
    def update(self, dt: float, tilemap, bounds_rect: pygame.Rect):
        new_pos = self.pos + self.vel * dt

        # Kollision: erst X, dann Y (Axis-Aligned)
        hitbox = pygame.Rect(0, 0, self.hitbox_size, self.hitbox_size) # kompaktere Hitbox als das Sprite
        # --- X
        hitbox.center = (new_pos.x, self.pos.y)
        for wall in tilemap.get_nearby_solid_rects(hitbox):
            if hitbox.colliderect(wall):
                if self.vel.x > 0:
                    hitbox.right = wall.left
                elif self.vel.x < 0:
                    hitbox.left = wall.right
                new_pos.x = hitbox.centerx
        # --- Y
        hitbox.center = (new_pos.x, new_pos.y)
        for wall in tilemap.get_nearby_solid_rects(hitbox):
            if hitbox.colliderect(wall):
                if self.vel.y > 0:
                    hitbox.bottom = wall.top
                elif self.vel.y < 0:
                    hitbox.top = wall.bottom
                new_pos.y = hitbox.centery

        self.pos = new_pos
        # optional: im Welt-Rechteck bleiben
        self.pos.x = max(0, min(tilemap.pixel_width, self.pos.x))
        self.pos.y = max(0, min(tilemap.pixel_height, self.pos.y))

    def draw(self, surface: pygame.Surface):
        image = pygame.transform.rotate(self.base_image, -self.angle)  # -angle passt zur heading-Logik
        rect = image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        surface.blit(image, rect)

    def draw_with_camera(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        import pygame
        image = pygame.transform.rotate(self.base_image, -self.angle)
        rect = image.get_rect(center=(round(self.pos.x - camera_offset.x), round(self.pos.y - camera_offset.y)))
        surface.blit(image, rect)
