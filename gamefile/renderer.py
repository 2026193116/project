"""
화면 렌더링 모듈 (pygame 의존 - 85dB 게이지 반영 및 쿨타임 UI 추가)
"""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOSS_X, BOSS_Y, PLAYER_X,
    WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN,
    DB_THRESHOLD, LEVEL_UP_DISPLAY_DURATION  # 수정 완료
)
from entities import GameState

class Renderer:
    """모든 화면 그리기 담당"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_word = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 24)
        self.font_boss = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_level = pygame.font.SysFont("Arial", 60, bold=True)

        # 시작 배경화면 이미지 로드 예외 처리 추가
        try:
            raw_bg = pygame.image.load("assets/background.png").convert()
            self.background_img = pygame.transform.scale(raw_bg, (1000, 600))
        except pygame.error:
            self.background_img = None

    def draw_frame(self, state: GameState, mic_volume: float,
                   is_shouting: bool, current_time: int):
        """게임 플레이 화면 전체를 그림"""
        if self.background_img:
            self.screen.blit(self.background_img, (0, 0))
        else:
            self.screen.fill(BLACK)

        if state.game_over:
            self._draw_game_over(state)
        else:
            self._draw_defense_line()
            self._draw_boss()
            self._draw_words(state)
            self._draw_level_up(state, current_time)
            self._draw_ui(state)
            self._draw_mic_gauge(mic_volume, is_shouting, state)

        pygame.display.flip()

    def _draw_defense_line(self):
        pygame.draw.line(self.screen, RED, (PLAYER_X, 0), (PLAYER_X, SCREEN_HEIGHT), 3)

    def _draw_boss(self):
        pygame.draw.circle(self.screen, PURPLE, (BOSS_X, BOSS_Y), 40)
        text_surface = self.font_boss.render("BOSS", True, WHITE)
        text_rect = text_surface.get_rect(center=(BOSS_X, BOSS_Y))
        self.screen.blit(text_surface, text_rect)

    def _draw_words(self, state: GameState):
        for w in state.active_words:
            color = YELLOW if w.is_heavy else WHITE
            if state.current_input and w.starts_with(state.current_input):
                color = GREEN
            
            surface = self.font_word.render(w.text, True, color)
            self.screen.blit(surface, (w.x, w.y))

    def _draw_level_up(self, state: GameState, current_time: int):
        if state.level_up_time > 0 and (current_time - state.level_up_time < LEVEL_UP_DISPLAY_DURATION):
            lvl_text = f"LEVEL UP! -> {state.level}"
            surface = self.font_level.render(lvl_text, True, YELLOW)
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(surface, rect)

    def _draw_ui(self, state: GameState):
        texts = [\
            (f"LEVEL: {state.level}", CYAN, (PLAYER_X + 20, 20)),
            (f"LIVES: {state.lives} / 3", RED, (PLAYER_X + 20, 50)),
            (f"SCORE: {state.score}", WHITE, (PLAYER_X + 20, 80)),
            (f"INPUT: {state.current_input}", GREEN, (PLAYER_X + 20, SCREEN_HEIGHT - 40)),
        ]
        for text, color, pos in texts:
            surface = self.font_ui.render(text, True, color)
            self.screen.blit(surface, pos)

    def _draw_mic_gauge(self, mic_volume: float, is_shouting: bool, state: GameState):
        gauge_x = SCREEN_WIDTH // 2 - 100
        gauge_y = 20
        gauge_width = 200
        gauge_height = 20

        pygame.draw.rect(self.screen, BLUE, (gauge_x, gauge_y, gauge_width, gauge_height), 2)
        bar_width = min(int((mic_volume / 100.0) * gauge_width), gauge_width)
        
        if state.is_cooling_down:
            bar_color = (120, 120, 120)
            status_text = "COOL DOWN (3s)"
        else:
            bar_color = RED if is_shouting else GREEN
            status_text = f"SHOUT GAUGE ({int(mic_volume)} dB)"

        if bar_width > 0:
            pygame.draw.rect(self.screen, bar_color, (gauge_x, gauge_y, bar_width, gauge_height))
        
        text_mic = self.font_ui.render(status_text, True, WHITE)
        self.screen.blit(text_mic, (gauge_x, gauge_y + 25))

    def _draw_game_over(self, state: GameState):
        surface = self.font_level.render("GAME OVER", True, RED)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(surface, rect)

        score_text = f"Final Score: {state.score}"
        surface_score = self.font_ui.render(score_text, True, WHITE)
        rect_score = surface_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(surface_score, rect_score)

        esc_text = "Press ESC to Quit Game"
        surface_esc = self.font_ui.render(esc_text, True, CYAN)
        rect_esc = surface_esc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(surface_esc, rect_esc)