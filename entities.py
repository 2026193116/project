"""
게임 엔티티 (단어, 플레이어 상태, 보스) 모듈
"""

import random
import math
from config import (
    WORD_POOL, Y_LANES, MAX_RECENT_LANES, BOSS_X,
    HEAVY_CHANCE_BASE, HEAVY_CHANCE_PER_LEVEL, HEAVY_CHANCE_MAX,
    WORD_SPEED_MIN, WORD_SPEED_MAX, WORD_SPEED_LEVEL_BONUS,
    WORD_AMP_MIN, WORD_AMP_MAX, WORD_FREQ_MIN, WORD_FREQ_MAX,
    INITIAL_LIVES, INITIAL_LEVEL, INITIAL_NEXT_LEVEL_TARGET,
    PLAYER_X, SHOUT_PUSH_BASE,
    SPAWN_DELAY_BASE, SPAWN_DELAY_MIN, SPAWN_DELAY_LEVEL_REDUCTION
)

class Word:
    """화면을 가로질러 이동하는 단어 객체"""

    def __init__(self, text: str, x: float, base_y: int,
                 amp: int, freq: float, speed: float, is_heavy: bool):
        self.text = text
        self.x = x
        self.y = float(base_y)
        self.base_y = base_y
        self.amp = amp
        self.freq = freq
        self.speed = speed
        self.is_heavy = is_heavy

    def update(self, current_time: int):
        """매 프레임 호출: 왼쪽으로 이동 + 사인파 Y 좌표 계산"""
        self.x -= self.speed
        self.y = self.base_y + math.sin(current_time / self.freq * self.amp)

    def push_back(self, amount: float):
        """소리치기로 오른쪽으로 밀어냄 (heavy가 아닐 때만 외부에서 호출)"""
        self.x += amount

    def has_reached(self, threshold_x: float) -> bool:
        """방어선에 도달했는지 확인"""
        return self.x < threshold_x

    def matches(self, input_text: str) -> bool:
        """입력 텍스트와 단어가 일치하는지 확인"""
        return self.text == input_text.upper().strip()

    def starts_with(self, input_text: str) -> bool:
        """입력 텍스트가 단어의 접두사인지 확인"""
        stripped = input_text.strip()
        if not stripped:
            return False
        return self.text.startswith(stripped.upper())

class WordSpawner:
    """레인 시스템 기반 단어 생성기"""

    def __init__(self, word_pool: list = None, y_lanes: list = None):
        self.word_pool = word_pool or WORD_POOL
        self.y_lanes = y_lanes or Y_LANES
        self.recent_lanes = []

    def get_spawn_delay(self, level: int) -> int:
        """현재 레벨에 따른 스폰 딜레이(ms) 계산"""
        delay = SPAWN_DELAY_BASE - (level * SPAWN_DELAY_LEVEL_REDUCTION)
        return max(SPAWN_DELAY_MIN, delay)

    def get_heavy_chance(self, level: int) -> float:
        """현재 레벨에 따른 무거운 단어 등장 확률 계산"""
        return min(HEAVY_CHANCE_MAX, HEAVY_CHANCE_BASE + (level * HEAVY_CHANCE_PER_LEVEL))

    def choose_lane(self) -> int:
        """겹침 방지 레인 선택"""
        available = [l for l in self.y_lanes if l not in self.recent_lanes]
        if not available:
            available = self.y_lanes
        chosen = random.choice(available)
        self.recent_lanes.append(chosen)
        if len(self.recent_lanes) > MAX_RECENT_LANES:
            self.recent_lanes.pop(0)
        return chosen

    def spawn(self, level: int) -> Word:
        """새 단어 객체 생성"""
        lane = self.choose_lane()
        is_heavy = random.random() < self.get_heavy_chance(level)

        return Word(
            text=random.choice(self.word_pool),
            x=BOSS_X - 20,
            base_y=lane,
            amp=random.randint(WORD_AMP_MIN, WORD_AMP_MAX),
            freq=random.uniform(WORD_FREQ_MIN, WORD_FREQ_MAX),
            speed=random.uniform(WORD_SPEED_MIN, WORD_SPEED_MAX) + (level * WORD_SPEED_LEVEL_BONUS),
            is_heavy=is_heavy
        )

class GameState:
    """게임 전체 상태를 관리하는 클래스"""

    def __init__(self):
        self.lives = INITIAL_LIVES
        self.score = 0
        self.level = INITIAL_LEVEL
        self.words_cleared = 0
        self.next_level_target = INITIAL_NEXT_LEVEL_TARGET
        self.level_up_time = 0
        self.game_over = False
        self.current_input = ""
        self.active_words: list[Word] = []

    def lose_life(self):
        """목숨 감소, 0 이하면 게임 오버"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True

    def add_score(self, base_score: int = 100):
        """점수 추가 (레벨 비례)"""
        self.score += base_score * self.level
        self.words_cleared += 1

    def check_level_up(self, current_time: int) -> bool:
        """레벨업 조건 확인 및 처리. 레벨업 시 True 반환."""
        if self.words_cleared >= self.next_level_target:
            self.level += 1
            self.next_level_target += 10 + (self.level * 5)
            self.level_up_time = current_time
            return True
        return False

    def append_input(self, char: str):
        """입력 문자 추가"""
        self.current_input += char

    def backspace_input(self):
        """마지막 입력 문자 제거"""
        self.current_input = self.current_input[:-1]

    def clear_input(self):
        """입력 초기화"""
        self.current_input = ""
