import pygame
import sys
import json
import os
from typing import List, Tuple, Optional, Dict

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 450, 550
BOARD_SIZE = 3
CELL_SIZE = 125
BOARD_OFFSET_X, BOARD_OFFSET_Y = 40, 50
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GREEN': (46, 204, 113),
    'RED': (231, 76, 60),
    'GRAY': (120, 120, 120),
    'LIGHT_GRAY': (240, 240, 240),
    'DARK_GRAY': (50, 50, 50),
    'BLUE': (52, 152, 219),
    'PURPLE': (155, 89, 182),
    'YELLOW': (241, 196, 15),
    'PANEL_BG': (30, 30, 40)
}
FONT_NAME = 'Arial'

class TicTacToe:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            print("Error al inicializar el mezclador de sonido.")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TIC TAC TOE")

        try:
            icon = pygame.image.load('static/icono.ico')
            pygame.display.set_icon(icon)
        except:
            print("No se pudo cargar el icono")

        self.clock = pygame.time.Clock()

        self.load_resources()
        self.load_sounds()
        self.reset_game()

        self.scores = {'X': 0, 'O': 0, 'Ties': 0}
        self.load_scores()

        self.font = pygame.font.SysFont(FONT_NAME, 18)
        self.big_font = pygame.font.SysFont(FONT_NAME, 28, bold=True)
        self.score_font = pygame.font.SysFont(FONT_NAME, 16, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 12, bold=True)

        self.cell_coords = [
            [(BOARD_OFFSET_X + j * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE) 
             for j in range(BOARD_SIZE)] 
            for i in range(BOARD_SIZE)
        ]

    def load_resources(self):
        try:
            self.background = pygame.image.load('static/tictactoe_background.png')
            self.background = pygame.transform.scale(self.background, (450, 450))

            self.circle_img = pygame.image.load('static/circle.png')
            self.circle_img = pygame.transform.scale(self.circle_img, (125, 125))

            self.x_img = pygame.image.load('static/x.png')
            self.x_img = pygame.transform.scale(self.x_img, (125, 125))
        except pygame.error as e:
            print(f"Error al cargar imágenes: {e}")
            sys.exit(1)

    def load_sounds(self):
        try:
            self.click_sound = pygame.mixer.Sound('static/click.wav') if os.path.exists('static/click.wav') else None
            self.win_sound = pygame.mixer.Sound('static/win.wav') if os.path.exists('static/win.wav') else None
            self.draw_sound = pygame.mixer.Sound('static/draw.wav') if os.path.exists('static/draw.wav') else None
        except:
            self.click_sound = None
            self.win_sound = None
            self.draw_sound = None

    def reset_game(self):
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.winning_cells = []
        self.animation_alpha = 0
        self.animation_direction = 1

    def load_scores(self):
        try:
            if os.path.exists('scores.json'):
                with open('scores.json', 'r') as f:
                    self.scores = json.load(f)
        except:
            self.scores = {'X': 0, 'O': 0, 'Ties': 0}

    def save_scores(self):
        try:
            with open('scores.json', 'w') as f:
                json.dump(self.scores, f)
        except:
            print("No se pudo guardar la puntuación.")

    def draw_board(self):
        self.screen.blit(self.background, (0, 0))

        if self.winning_cells:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 200, 0, int(self.animation_alpha)))
            self.screen.blit(s, (0, 0))

            for row, col in self.winning_cells:
                img = self.x_img.copy() if self.board[row][col] == 'X' else self.circle_img.copy()
                img.fill((255, 255, 255, 255), None, pygame.BLEND_RGBA_MULT)
                self.screen.blit(img, self.cell_coords[row][col])

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row, col) not in self.winning_cells:
                    if self.board[row][col] == 'X':
                        self.screen.blit(self.x_img, self.cell_coords[row][col])
                    elif self.board[row][col] == 'O':
                        self.screen.blit(self.circle_img, self.cell_coords[row][col])

    def check_winner(self) -> Optional[str]:
        for i in range(BOARD_SIZE):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '':
                self.winning_cells = [(i, 0), (i, 1), (i, 2)]
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != '':
                self.winning_cells = [(0, i), (1, i), (2, i)]
                return self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            self.winning_cells = [(0, 0), (1, 1), (2, 2)]
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            self.winning_cells = [(0, 2), (1, 1), (2, 0)]
            return self.board[0][2]

        return None

    def is_board_full(self) -> bool:
        return all(self.board[row][col] != '' for row in range(BOARD_SIZE) for col in range(BOARD_SIZE))

    def draw_score_box(self, x, y, width, height, title, value, color):
        pygame.draw.rect(self.screen, COLORS['PANEL_BG'], (x, y, width, height))
        pygame.draw.rect(self.screen, color, (x, y, width, height), 2)

        title_text = self.title_font.render(title, True, COLORS['LIGHT_GRAY'])
        self.screen.blit(title_text, (x + width//2 - title_text.get_width()//2, y + 5))

        value_text = self.score_font.render(str(value), True, color)
        self.screen.blit(value_text, (x + width//2 - value_text.get_width()//2, y + height//2))

    def draw_ui(self):
        pygame.draw.rect(self.screen, COLORS['PANEL_BG'], (0, 450, SCREEN_WIDTH, 100))
        pygame.draw.line(self.screen, COLORS['BLUE'], (0, 450), (SCREEN_WIDTH, 450), 3)

        self.draw_score_box(10, 455, 120, 40, "JUGADOR X :", self.scores['X'], COLORS['RED'])
        self.draw_score_box(10, 500, 120, 40, "JUGADOR O :", self.scores['O'], COLORS['GREEN'])

        turn_rect = pygame.Rect(SCREEN_WIDTH//2 - 75, 460, 150, 80)
        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], turn_rect, border_radius=20)
        pygame.draw.rect(self.screen, COLORS['BLUE'], turn_rect, 2, border_radius=20)

        turn_text = self.big_font.render(f"{self.current_player}", True,
                                         COLORS['GREEN'] if self.current_player == 'O' else COLORS['RED'])
        label_text = self.font.render("Turno", True, COLORS['LIGHT_GRAY'])
        self.screen.blit(label_text, (SCREEN_WIDTH//2 - label_text.get_width()//2, 470))
        self.screen.blit(turn_text, (SCREEN_WIDTH//2 - turn_text.get_width()//2, 500))

        self.draw_score_box(320, 455, 120, 40, "EMPATES :", self.scores['Ties'], COLORS['YELLOW'])

        self.restart_button_rect = pygame.Rect(320, 505, 120, 35)
        pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], self.restart_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['YELLOW'], self.restart_button_rect, 2, border_radius=10)
        restart_text = self.font.render("Reiniciar", True, COLORS['LIGHT_GRAY'])
        self.screen.blit(restart_text, (self.restart_button_rect.centerx - restart_text.get_width()//2,
                                        self.restart_button_rect.centery - restart_text.get_height()//2))

        if self.game_over:
            result_rect = pygame.Rect(50, 460, SCREEN_WIDTH-100, 80)
            pygame.draw.rect(self.screen, COLORS['DARK_GRAY'], result_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['BLUE'], result_rect, 2, border_radius=10)

            if self.winner:
                result_text = self.big_font.render(f"¡{self.winner} GANA!", True,
                                                   COLORS['GREEN'] if self.winner == 'O' else COLORS['RED'])
            else:
                result_text = self.big_font.render("¡EMPATE!", True, COLORS['YELLOW'])

            restart_text = self.font.render("Haz clic para jugar otra vez", True, COLORS['LIGHT_GRAY'])
            self.screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 475))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 515))

    def handle_click(self, pos: Tuple[int, int]):
        try:
            x, y = pos

            if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(x, y):
                self.scores = {'X': 0, 'O': 0, 'Ties': 0}
                self.save_scores()
                return

            if self.game_over:
                self.reset_game()
                self.save_scores()
                return

            if (BOARD_OFFSET_X <= x < BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE and 
                BOARD_OFFSET_Y <= y < BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE):

                row = (y - BOARD_OFFSET_Y) // CELL_SIZE
                col = (x - BOARD_OFFSET_X) // CELL_SIZE

                if self.board[row][col] == '':
                    self.board[row][col] = self.current_player
                    if self.click_sound:
                        try:
                            self.click_sound.play()
                        except:
                            pass

                    self.winner = self.check_winner()
                    if self.winner:
                        self.game_over = True
                        self.scores[self.winner] += 1
                        if self.win_sound:
                            try:
                                self.win_sound.play()
                            except:
                                pass
                    elif self.is_board_full():
                        self.game_over = True
                        self.scores['Ties'] += 1
                        if self.draw_sound:
                            try:
                                self.draw_sound.play()
                            except:
                                pass
                    else:
                        self.current_player = 'O' if self.current_player == 'X' else 'X'
        except Exception as e:
            print(f"Error en handle_click: {e}")

    def update_animation(self):
        if self.winning_cells:
            self.animation_alpha += 5 * self.animation_direction
            if self.animation_alpha >= 100:
                self.animation_alpha = 100
                self.animation_direction = -1
            elif self.animation_alpha <= 0:
                self.animation_alpha = 0
                self.animation_direction = 1

    def run(self):
        while True:
            try:
                self.clock.tick(60)
                self.screen.fill(COLORS['WHITE'])
                self.draw_board()
                self.draw_ui()
                self.update_animation()
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.save_scores()
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_click(event.pos)
            except Exception as e:
                print(f"Error durante el ciclo principal: {e}")

if __name__ == "__main__":
    game = TicTacToe()
    game.run()
