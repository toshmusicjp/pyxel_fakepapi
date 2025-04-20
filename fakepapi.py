import pyxel
import random

WIDTH, HEIGHT = 128, 128
PAPI_WIDTH, PAPI_HEIGHT = 15, 15
JUMP_HEIGHT = 4

class Sprite:
    def __init__(self, type, w, h, sx, sy, x, y, gy, col, friction_x=0.05):
        self.type = type
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.speed_x = sx
        self.speed_y = sy
        self.gravity_y = gy
        self.gravity_x = 0
        self.friction_x = friction_x
        self.age = 0
        self.active = True
        self.col = col
        self.id = id(self)  # 一意の識別子

    def update(self):
        self.speed_x = (self.speed_x + self.gravity_x) * (1 - self.friction_x)
        self.speed_y += self.gravity_y
        self.x = (self.x + self.speed_x) % WIDTH
        self.y += self.speed_y
        self.age += 1

        if self.type == "papi":
            if self.y + self.h > HEIGHT:
                self.y = HEIGHT - self.h
                self.speed_y = 0
        elif self.type == "jump":
            if self.y > HEIGHT:
                self.active = False

    def draw(self):
        if self.type == "papi":
            # スプライト番号0, U=0, V=0, サイズ15x15, ページ1, フリップなし
            pyxel.blt(self.x, self.y, 1, 0, 0, 16, 16, 0)
        else:
            pyxel.rect(self.x, self.y, self.w, self.h, self.col)

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Papi Jump")
        pyxel.load("papijump_res.pyxres")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.sprites = []
        self.jumps = []
        self.is_game_over = False
        self.last_jump_id = None  # 最後に踏んだジャンプ台のID
        self.papi = Sprite("papi", PAPI_WIDTH, PAPI_HEIGHT, 0, 0, WIDTH // 2, HEIGHT - 40, 0.2, 8)
        self.sprites.append(self.papi)
        self.spawn_jump(HEIGHT - 20, centered=True)
        for y in range(HEIGHT - 40, 0, -20):
            self.spawn_jump(y)
        # ↓↓↓ ジャンプの高さ（初速）をここで調整（負の値が大きいほど高く飛ぶ）↓↓↓
        self.papi.speed_y = -6  # 例：-6で高めジャンプに

    def spawn_jump(self, y, centered=False):
        w = random.randint(16, 24)
        x = (WIDTH - w) // 2 if centered else random.randint(0, WIDTH - w)
        jump = Sprite("jump", w, JUMP_HEIGHT, 0, 0, x, y, 0, 11)
        self.jumps.append(jump)
        self.sprites.append(jump)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.is_game_over:
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                self.papi.speed_x = -2
            elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                self.papi.speed_x = 2
            else:
                self.papi.speed_x = 0

            for sprite in self.sprites:
                sprite.update()

            for jump in self.jumps:
                if (
                    self.papi.speed_y > 0
                    and self.papi.y + self.papi.h <= jump.y + 5
                    and self.papi.x + self.papi.w > jump.x
                    and self.papi.x < jump.x + jump.w
                    and self.papi.y + self.papi.h >= jump.y
                ):
                    self.papi.y = jump.y - self.papi.h
                    self.papi.speed_y = -6  # ← ジャンプの高さ（調整可）

                    # 同じ床でスコアを加算しない
                    if self.last_jump_id != jump.id:
                        self.score += 1
                        self.last_jump_id = jump.id
                    break  # 複数ジャンプへの連続判定を防ぐ

            # ↓↓↓ カメラスクロール速度（上方向に移動時の世界の移動速度）↓↓↓
            if self.papi.y < HEIGHT // 6:
                scroll = 3  # ← スクロール速度（調整可）
                self.papi.y += scroll
                for jump in self.jumps:
                    jump.y += scroll

            if len(self.jumps) < 6:
                self.spawn_jump(0)

            self.jumps = [j for j in self.jumps if j.active]
            self.sprites = [s for s in self.sprites if s.active]

            if self.papi.y + self.papi.h >= HEIGHT:
                self.is_game_over = True

        else:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.reset_game()

    def draw(self):
        pyxel.cls(5) # 背景色を青
        for sprite in self.sprites:
            sprite.draw()
        pyxel.text(5, 5, f"Score: {self.score}", 0)
        if self.is_game_over:
            pyxel.text(WIDTH // 2 - 20, HEIGHT // 2 - 10, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(WIDTH // 2 - 40, HEIGHT // 2 + 10, "Press SPACE to restart", 0)

Game()
