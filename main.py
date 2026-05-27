"""
메인 엔트리포인트: 이벤트 루프 및 모듈 연결 (ESC 즉시 종료 반영)
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from audio import AudioManager
from entities import GameState, WordSpawner
from game_logic import process_shout, try_submit_word, update_words, spawn_word_if_ready
from renderer import Renderer

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("보스를 향해 소리쳐! - 가로형 디펜스 에디션")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    audio = AudioManager()
    audio.start()

    state = GameState()
    spawner = WordSpawner()
    last_spawn_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # [수정] 게임 중이든, 게임오버 상태이든 ESC를 누르면 즉시 전체 게임 완전히 종료
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                
                # 게임 진행 중일 때의 키 입력 분기
                if not state.game_over:
                    if event.key == pygame.K_BACKSPACE:
                        state.backspace_input()
                    elif event.key == pygame.K_RETURN:
                        try_submit_word(state, current_time)
                    elif event.key == pygame.K_SPACE:
                        state.append_input(" ")
                    else:
                        if event.unicode.isalpha():
                            state.append_input(event.unicode)

        if not state.game_over:
            # 소리치기 및 쿨타임 연산 처리 (current_time 추가 전달)
            process_shout(state, audio, current_time)

            # 단어 스폰
            last_spawn_time = spawn_word_if_ready(
                state, spawner, current_time, last_spawn_time
            )

            # 단어 이동 및 충돌
            update_words(state, current_time)

        # 렌더링 (게이지 및 쿨타임UI용 데시벨 전달)
        renderer.draw_frame(state, audio.get_volume(),
                            audio.is_shouting(), current_time)
        clock.tick(FPS)

    audio.stop()
    pygame.quit()

if __name__ == "__main__":
    main()