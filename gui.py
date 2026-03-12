import pygame
import sys
import os
import threading

from board import initialize_board
from game_logic import move_piece, check_game_status, get_all_legal_moves, is_in_check
from algorithm import minimax
from utils import position_to_indices, indices_to_position
from pieces import Pawn, King

# --- Constants ---
SQUARE = 80
BOARD_PX = SQUARE * 8
SIDEBAR = 220
WIN_W = BOARD_PX + SIDEBAR
WIN_H = BOARD_PX
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SEL_LIGHT = (246, 246, 105)
SEL_DARK = (186, 202, 68)
LAST_LIGHT = (205, 210, 106)
LAST_DARK = (170, 162, 58)
CHECK_COL = (235, 97, 80)
BG = (48, 46, 43)
TEXT = (220, 220, 220)
MUTED = (150, 150, 150)
ACCENT = (129, 182, 76)
BTN = (70, 70, 70)
BTN_HOVER = (90, 90, 90)

WHITE_PIECE = (255, 255, 255)
BLACK_PIECE = (50, 50, 50)

PIECE_SVG = {
    'King': 'king.svg', 'Queen': 'queen.svg', 'Rook': 'rook.svg',
    'Bishop': 'bishop.svg', 'Knight': 'knight.svg', 'Pawn': 'pawn.svg',
}


class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Smart Chess")
        self.clock = pygame.time.Clock()

        _fn = "ubuntu"
        self.label_font = pygame.font.SysFont(_fn, 16)
        self.title_font = pygame.font.SysFont(_fn, 24, bold=True)
        self.info_font = pygame.font.SysFont(_fn, 18)
        self.small_font = pygame.font.SysFont(_fn, 16)

        self._load_pieces()
        self.reset_game()

    def _load_pieces(self):
        """Load SVG assets and create white/black tinted versions at multiple sizes."""
        self.piece_img = {}
        self.piece_img_sm = {}
        self.piece_img_promo = {}

        board_size = SQUARE - 10
        small_size = 22
        promo_size = 52

        for ptype, filename in PIECE_SVG.items():
            path = os.path.join(ASSET_DIR, filename)
            base = pygame.image.load(path).convert_alpha()

            for color, tint in [('white', WHITE_PIECE), ('black', BLACK_PIECE)]:
                # Board piece
                scaled = pygame.transform.smoothscale(base, (board_size, board_size))
                tinted = scaled.copy()
                tinted.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                self.piece_img[(ptype, color)] = tinted

                # Small piece (sidebar captured)
                sm = pygame.transform.smoothscale(base, (small_size, small_size))
                sm_t = sm.copy()
                sm_t.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                self.piece_img_sm[(ptype, color)] = sm_t

                # Promotion dialog piece
                pr = pygame.transform.smoothscale(base, (promo_size, promo_size))
                pr_t = pr.copy()
                pr_t.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                self.piece_img_promo[(ptype, color)] = pr_t

    def reset_game(self):
        self.board = initialize_board()
        self.turn = 'white'
        self.human_color = 'white'
        self.ai_color = 'black'
        self.last_move = None
        self.selected = None
        self.legal_dests = []
        self.game_over = False
        self.result = None
        self.status = "Your turn"
        self.captured_by_white = []
        self.captured_by_black = []
        self.last_move_sqs = []
        self.ai_thinking = False
        self.ai_result = None
        self.check_sq = None
        self.promo_pending = False
        self.promo_move = None
        self.promo_rects = {}
        self.new_game_btn = None

    # --- Drawing ---

    def _sq_color(self, row, col, selected=False, last_move=False):
        light = (row + col) % 2 == 1
        if selected:
            return SEL_LIGHT if light else SEL_DARK
        if last_move:
            return LAST_LIGHT if light else LAST_DARK
        return LIGHT if light else DARK

    def draw_board(self):
        last_set = set(tuple(s) for s in self.last_move_sqs)
        sel_set = {self.selected} if self.selected else set()

        for row in range(8):
            for col in range(8):
                is_sel = (row, col) in sel_set
                is_last = (row, col) in last_set and (row, col) not in sel_set
                color = self._sq_color(row, col, is_sel, is_last)
                rect = pygame.Rect(col * SQUARE, (7 - row) * SQUARE, SQUARE, SQUARE)
                pygame.draw.rect(self.screen, color, rect)

        # Check highlight
        if self.check_sq:
            r, c = self.check_sq
            surf = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
            surf.fill((*CHECK_COL, 160))
            self.screen.blit(surf, (c * SQUARE, (7 - r) * SQUARE))

        # Legal move indicators
        for pos_str in self.legal_dests:
            r, c = position_to_indices(pos_str)
            target = self.board[r][c]
            surf = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
            if target and target.color != self.human_color:
                pygame.draw.circle(surf, (0, 0, 0, 50),
                                   (SQUARE // 2, SQUARE // 2), SQUARE // 2 - 2, 5)
            else:
                pygame.draw.circle(surf, (0, 0, 0, 50),
                                   (SQUARE // 2, SQUARE // 2), 12)
            self.screen.blit(surf, (c * SQUARE, (7 - r) * SQUARE))

        # File labels (a-h) along bottom
        for col in range(8):
            is_light = col % 2 == 1
            fc = DARK if is_light else LIGHT
            lbl = self.label_font.render(chr(ord('a') + col), True, fc)
            self.screen.blit(lbl, (col * SQUARE + SQUARE - 12, BOARD_PX - 14))

        # Rank labels (1-8) along left
        for row in range(8):
            is_light = row % 2 == 1
            rc = DARK if is_light else LIGHT
            lbl = self.label_font.render(str(row + 1), True, rc)
            self.screen.blit(lbl, (2, (7 - row) * SQUARE + 2))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    ptype = type(piece).__name__
                    img = self.piece_img.get((ptype, piece.color))
                    if img:
                        rect = img.get_rect(center=(
                            col * SQUARE + SQUARE // 2,
                            (7 - row) * SQUARE + SQUARE // 2
                        ))
                        self.screen.blit(img, rect)

    def draw_sidebar(self):
        pygame.draw.rect(self.screen, BG, (BOARD_PX, 0, SIDEBAR, WIN_H))
        x = BOARD_PX + 18
        y = 20

        # Title
        t = self.title_font.render("Smart Chess", True, ACCENT)
        self.screen.blit(t, (x, y))
        y += 32

        pygame.draw.line(self.screen, (80, 80, 80), (x, y), (WIN_W - 18, y))
        y += 14

        # Turn indicator
        dot_color = (255, 255, 255) if self.turn == 'white' else (40, 40, 40)
        pygame.draw.circle(self.screen, dot_color, (x + 6, y + 7), 6)
        pygame.draw.circle(self.screen, MUTED, (x + 6, y + 7), 6, 1)
        turn_txt = self.info_font.render(f"{self.turn.capitalize()}'s turn", True, TEXT)
        self.screen.blit(turn_txt, (x + 18, y))
        y += 26

        # Status
        sc = ACCENT if not self.game_over else CHECK_COL
        st = self.info_font.render(self.status, True, sc)
        self.screen.blit(st, (x, y))
        y += 30

        pygame.draw.line(self.screen, (80, 80, 80), (x, y), (WIN_W - 18, y))
        y += 12

        # Captured pieces
        cl = self.small_font.render("Captured", True, MUTED)
        self.screen.blit(cl, (x, y))
        y += 22

        self._draw_captured_row(x, y, self.captured_by_white)
        y += 28
        self._draw_captured_row(x, y, self.captured_by_black)
        y += 36

        pygame.draw.line(self.screen, (80, 80, 80), (x, y), (WIN_W - 18, y))
        y += 12

        ctrl = self.small_font.render("N = new game  ESC = quit", True, MUTED)
        self.screen.blit(ctrl, (x, y))

        # New Game button
        self.new_game_btn = pygame.Rect(x, WIN_H - 56, SIDEBAR - 36, 38)
        mx, my = pygame.mouse.get_pos()
        bc = BTN_HOVER if self.new_game_btn.collidepoint(mx, my) else BTN
        pygame.draw.rect(self.screen, bc, self.new_game_btn, border_radius=6)
        bt = self.info_font.render("New Game", True, TEXT)
        br = bt.get_rect(center=self.new_game_btn.center)
        self.screen.blit(bt, br)

    def _draw_captured_row(self, x, y, captured_list):
        cx = x
        for ptype, color in captured_list:
            img = self.piece_img_sm.get((ptype, color))
            if img:
                self.screen.blit(img, (cx, y))
                cx += 24
            if cx > WIN_W - 30:
                break

    def draw_promotion_dialog(self):
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        dw, dh = 340, 110
        dx = (BOARD_PX - dw) // 2
        dy = (WIN_H - dh) // 2
        pygame.draw.rect(self.screen, BG, (dx, dy, dw, dh), border_radius=10)
        pygame.draw.rect(self.screen, ACCENT, (dx, dy, dw, dh), 2, border_radius=10)

        label = self.small_font.render("Promote pawn to:", True, MUTED)
        self.screen.blit(label, (dx + (dw - label.get_width()) // 2, dy + 8))

        pieces = ['Queen', 'Rook', 'Bishop', 'Knight']
        self.promo_rects = {}
        mx, my = pygame.mouse.get_pos()

        for i, pname in enumerate(pieces):
            rx = dx + 10 + i * 82
            ry = dy + 28
            rect = pygame.Rect(rx, ry, 74, 72)
            if rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, BTN_HOVER, rect, border_radius=6)

            img = self.piece_img_promo.get((pname, self.human_color))
            if img:
                ir = img.get_rect(center=rect.center)
                self.screen.blit(img, ir)
            self.promo_rects[pname] = rect

    # --- Game Logic Helpers ---

    def update_check(self):
        self.check_sq = None
        if is_in_check(self.board, self.turn, self.last_move):
            for row in range(8):
                for col in range(8):
                    p = self.board[row][col]
                    if p and isinstance(p, King) and p.color == self.turn:
                        self.check_sq = (row, col)
                        return

    def _track_capture(self, start_pos, end_pos):
        sr, sc = position_to_indices(start_pos)
        er, ec = position_to_indices(end_pos)
        piece = self.board[sr][sc]
        target = self.board[er][ec]

        # En passant
        if isinstance(piece, Pawn) and abs(ec - sc) == 1 and target is None:
            cap = self.board[sr][ec]
            if cap and isinstance(cap, Pawn):
                entry = ('Pawn', cap.color)
                if cap.color == 'white':
                    self.captured_by_black.append(entry)
                else:
                    self.captured_by_white.append(entry)
        elif target and target.color != piece.color:
            entry = (type(target).__name__, target.color)
            if target.color == 'white':
                self.captured_by_black.append(entry)
            else:
                self.captured_by_white.append(entry)

    def _result_msg(self, result):
        if result == 'white_win':
            return "Checkmate! You win!"
        elif result == 'black_win':
            return "Checkmate! AI wins!"
        return "Stalemate! Draw."

    def _execute_move(self, start_pos, end_pos, promo='Q'):
        self._track_capture(start_pos, end_pos)
        sr, sc = position_to_indices(start_pos)
        er, ec = position_to_indices(end_pos)

        move_piece(self.board, start_pos, end_pos, self.last_move, promotion_choice=promo)
        self.last_move = (start_pos, end_pos)
        self.last_move_sqs = [(sr, sc), (er, ec)]
        self.selected = None
        self.legal_dests = []

        # Switch turn
        self.turn = self.ai_color
        over, result = check_game_status(self.board, self.turn, self.last_move)
        if over:
            self.game_over = True
            self.result = result
            self.status = self._result_msg(result)
        else:
            self.status = "AI thinking..."
            self.update_check()
            self._start_ai()

    def _select(self, row, col):
        self.selected = (row, col)
        pos = indices_to_position(col, row)
        all_legal = get_all_legal_moves(self.board, self.human_color, self.last_move)
        self.legal_dests = [end for start, end in all_legal if start == pos]

    # --- AI ---

    def _start_ai(self):
        self.ai_thinking = True
        self.ai_result = None
        t = threading.Thread(target=self._ai_compute, daemon=True)
        t.start()

    def _ai_compute(self):
        ev, move = minimax(
            self.board, depth=3,
            alpha=float('-inf'), beta=float('inf'),
            maximizing_player=True,
            current_color=self.ai_color,
            last_move=self.last_move
        )
        self.ai_result = (ev, move)

    def _process_ai(self):
        if not self.ai_thinking or self.ai_result is None:
            return

        ev, ai_move = self.ai_result
        self.ai_thinking = False

        if ai_move:
            sp, ep = ai_move
            self._track_capture(sp, ep)
            sr, sc = position_to_indices(sp)
            er, ec = position_to_indices(ep)

            move_piece(self.board, sp, ep, self.last_move, promotion_choice='Q')
            self.last_move = (sp, ep)
            self.last_move_sqs = [(sr, sc), (er, ec)]

            self.turn = self.human_color
            over, result = check_game_status(self.board, self.turn, self.last_move)
            if over:
                self.game_over = True
                self.result = result
                self.status = self._result_msg(result)
            else:
                self.status = "Your turn"
                self.update_check()
        else:
            self.game_over = True
            self.status = "AI has no moves!"

    # --- Input ---

    def handle_click(self, mx, my):
        if self.promo_pending:
            self._handle_promo_click(mx, my)
            return

        if self.new_game_btn and self.new_game_btn.collidepoint(mx, my):
            self.reset_game()
            return

        if self.game_over or self.ai_thinking or self.turn != self.human_color:
            return

        pos = self._pixel_to_board(mx, my)
        if not pos:
            return

        row, col = pos
        clicked = indices_to_position(col, row)

        if self.selected:
            if clicked in self.legal_dests:
                start_pos = indices_to_position(self.selected[1], self.selected[0])
                piece = self.board[self.selected[0]][self.selected[1]]
                er, ec = position_to_indices(clicked)
                promo_row = 7 if piece.color == 'white' else 0
                if isinstance(piece, Pawn) and er == promo_row:
                    self.promo_pending = True
                    self.promo_move = (start_pos, clicked)
                    return
                self._execute_move(start_pos, clicked)
            else:
                p = self.board[row][col]
                if p and p.color == self.human_color:
                    self._select(row, col)
                else:
                    self.selected = None
                    self.legal_dests = []
        else:
            p = self.board[row][col]
            if p and p.color == self.human_color:
                self._select(row, col)

    def _handle_promo_click(self, mx, my):
        choice_map = {'Queen': 'Q', 'Rook': 'R', 'Bishop': 'B', 'Knight': 'N'}
        for pname, rect in self.promo_rects.items():
            if rect.collidepoint(mx, my):
                start, end = self.promo_move
                self.promo_pending = False
                self.promo_move = None
                self._execute_move(start, end, promo=choice_map[pname])
                return

    def _pixel_to_board(self, mx, my):
        if 0 <= mx < BOARD_PX and 0 <= my < BOARD_PX:
            return 7 - (my // SQUARE), mx // SQUARE
        return None

    # --- Main Loop ---

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.handle_click(*ev.pos)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_n:
                        self.reset_game()
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self._process_ai()

            self.draw_board()
            self.draw_pieces()
            self.draw_sidebar()
            if self.promo_pending:
                self.draw_promotion_dialog()

            pygame.display.flip()
            self.clock.tick(60)


def main():
    gui = ChessGUI()
    gui.run()


if __name__ == "__main__":
    main()
