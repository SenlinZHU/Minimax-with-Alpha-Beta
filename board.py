import tkinter as tk
from tkinter import messagebox, filedialog
from random import choice
from time import time
from piece import *


class Board(object):
    """"The game itself, the main functionality of the program"""
    def __init__(self, size=600, AI=False):
        """Creates windows, backgrounds and figures. """
        self.ai_side = None
        """The 'AI' parameter determines whether it is played against the computer"""
        self.root = tk.Tk()
        self.root.title("CHECKER: enjoy this game with AI")
        self.root.resizable(0, 0)
        self.size = size
        self.rect_size = self.size / 8
        self.AI = AI
        self.c = Piece.c = tk.Canvas(width=size, height=size, bg="#bcbcbc")
        self.c.pack()
        self.menu_bar()
        self.DrawBoard()
        self.choose_side()

    def timer(self):
        """Keeps the number of seconds after the game starts"""
        if self.count_time:
            self.time = round(time() - self.start) + self.add
            self.c.after(1000, self.timer)

    def choose_side(self):
        """Creates a window for selecting a player's side, creates a game when selected"""
        def closed():
            self.root.destroy()

        self.choose_side = tk.Toplevel(background='#F5FFFA')  # Let players choose white or black pieces
        self.choose_side.title('Welcome to this AI WORLD')
        self.choose_side.attributes('-topmost', True)
        self.choose_side.resizable(0, 0)
        self.choose_side.geometry('300x300')
        self.choose_side.protocol('WM_DELETE_WINDOW', closed)

        label = tk.Label(self.choose_side, text='HI! *WHITE* or *BLACK* to *START*', font=('microsoft yahei', 14),
                         bd=2, background='#F5FFFA')
        label.pack()

        self.black_button = tk.Button(self.choose_side, text="Easy", font=('microsoft yahei', 13),
                                      bd=2, background='#F5FFFA',
                                      command=lambda: chose_side('white'))
        self.white_button = tk.Button(self.choose_side, text="Difficult", font=('microsoft yahei', 13),
                                      bd=2, background='#F5FFFA',
                                      command=lambda: chose_side('black'))
        self.random_button = tk.Button(self.choose_side, text="RANDOM", font=('microsoft yahei', 13),
                                       bd=2, background='#F5FFFA',
                                       command=lambda: chose_side('random'))

        self.black_button.pack()
        self.white_button.pack()
        self.random_button.pack()

        def chose_side(col):
            if col == 'random':
                self.side = choice(('black', 'white'))
            else:
                self.side = col
            self.choose_side.destroy()
            self.PutPieces()
            self.selected = None

        self.choose_side.mainloop()

    def DrawBoard(self):
        """"Draw An 8x8 game chessboard"""
        self.lg, self.dk = '#F0F8FF', '#808080'
        for y in range(8):
            for x in range(8):
                rec_c = self.dk if (x + y) % 2 else self.lg
                coords = [y * self.rect_size, x * self.rect_size, y * self.rect_size + self.rect_size,
                          x * self.rect_size + self.rect_size]
                try:
                    self.c.create_rectangle(*coords, fill=rec_c, outline="")
                except:
                    pass

    def PutPieces(self):
        """Creates figure objects and starts a timer"""
        self.board = [[None for i in range(8)] for j in range(8)]
        side = 'black'
        for y in (0, 1, 2, 5, 6, 7):
            if y == 5:
                side = 'white'
            for x in range(1 - y % 2, 8 - y % 2, 2):
                self.board[x][y] = (Piece(side, (x, y), self.rect_size))

        self.count_time = True
        self.start = time()
        self.timer()

        if self.AI and self.side != self.move_side:
            self.c.update()
            self.waiting_for_ai = True
            self.c.after(1000, self.AIMoves())
        self.c.bind_all("<ButtonPress-1>", self.Click)

    def threatened_num(self,piece):
        # Before jump, find out risk
        threats = self.threatened(piece)
        # figurines that AI endanger 'piece'
        if threats:
            op_can_take = 0
            for threat in threats:
                op_moves = self.valid_moves((threat[0], threat[1]))  # figurines the endanger 'piece'
                for op_move in op_moves.values():
                    if op_move and (len(op_move) > op_can_take):
                        op_can_take = len(op_move)
            return op_can_take  # how another people the opponent
        return 0

    def evaluate(self):
        """"evaluate the num between ai_piece_num and player_piece_num"""
        self.ai_piece_num = len([piece for line in self.board for piece in line if (piece and piece.side == self.ai_side)])
        self.player_piece_num = len([piece for line in self.board for piece in line if (piece and piece.side == self.side)])
        return self.ai_piece_num - self.player_piece_num

    def minimax(self, position, depth=5, alpha=0, beta=0, max_player=True):
        """"using minimax search with alpha-beta pruning"""
        global all_move
        if depth == 0 or self.check_win == False:
            return position.evaluate(), position

        if max_player:
            maxEval = float('-inf')
            best_move = None
            ai_pieces = [piece for line in self.board for piece in line if (piece and piece.side == self.ai_side)]
            for piece in ai_pieces:
                move = self.valid_moves((piece.x, piece.y), False)
                evaluation = self.minimax(move, depth - 1, alpha, beta, False)[0]
                maxEval = max(maxEval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
                if maxEval == evaluation:
                    best_move = move

            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            player_pieces = [piece for line in self.board for piece in line if (piece and piece.side == self.side)]
            for piece in player_pieces:
                move = self.valid_moves((piece.x, piece.y), False).append
                evaluation = self.minimax(move, depth - 1, alpha, beta, True)[0]
                minEval = min(minEval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
                if minEval == evaluation:
                    best_move = move

            return minEval, best_move

    def AIMoves(self):
        """It finds all possible computer moves, evaluates them and
           selects the best ones valid (selected, field)
           Determines if the movement from 'selected' to 'field' is valid
        """
        ai_side = 'white' if self.side == 'black' else 'black'
        if ai_side != self.move_side:
            return

        ai_pieces = [piece for line in self.board for piece in line if (piece and piece.side == ai_side)]
        moves = []

        for piece in ai_pieces:
            move = self.valid_moves((piece.x, piece.y), False)
            if move:
                for key, value in move.items():
                    goes_from = self.board[piece.x][piece.y]
                    score = 0 if not value else len(value)
                    score += self.threatened_num(piece) * 0.5

                    if key[1] == 7 and goes_from.side == 'black' and not goes_from.king:
                        score += 0.75
                    elif key[1] == 0 and goes_from.side == 'white' and not goes_from.king:
                        score += 0.75

                    self.board[key[0]][key[1]] = Piece(goes_from.side, (key[0], key[1]), self.rect_size, goes_from.king)
                    self.board[piece.x][piece.y] = None
                    if value:
                        for remove in value:
                            self.board[remove.x][remove.y] = None

                    # accurately adjusted distribution of figures (for steps forward)
                    score -= self.threatened_num(self.board[key[0]][key[1]]) * 0.75
                    self.board[key[0]][key[1]].delete()
                    self.board[piece.x][piece.y] = goes_from
                    self.board[key[0]][key[1]] = None
                    if value:
                        for remove in value:
                            self.board[remove.x][remove.y] = remove
                    # # location returned
                    moves.append(((piece.x, piece.y), key, score, value))

        for move in moves:
            takes = ''
            if move[3]:
                for i in move[3]:
                    takes += f'({i.x}, {i.y}) '
            else:
                takes = 'None'
            print(f'From: {move[0]} | To: {move[1]} | Score: {move[2]} | Takes: {takes}')
        print('-' * 50)

        if not moves:
            messagebox.showinfo('Game finished', f'{self.side.capitalize()} won in {self.time} seconds!')
            return

        best, scores, max = [], [], -10
        for move in moves:
            if move[2] > max:
                best = []
                scores.append(move[2])
                max = move[2]
                best.append((move[0], move[1], move[3]))
            elif move[2] == max:
                best.append((move[0], move[1], move[3]))
        go_make_king = True

        for i, score in enumerate(scores):
            if score != 0:
                go_make_king = False
                break

        best_choice = None
        # position = self.board[piece.x][piece.y]
        # best = self.minimax(self, position)
        if go_make_king:  # If it's not good, then go and make the king
            for move in best:
                pom = self.board[move[0][0]][move[0][1]]
                if not pom.king:
                    best_choice = ((move[0], move[1], move[2]))
                    break
        if not best_choice:
            best_choice = choice(best)
            pom = self.board[best_choice[0][0]][best_choice[0][1]]

        pom.move(*best_choice[1])
        self.board[best_choice[0][0]][best_choice[0][1]] = None
        self.board[best_choice[1][0]][best_choice[1][1]] = pom
        pom.check_king()

        if best_choice[2]:
            for rem in best_choice[2]:
                self.board[rem.x][rem.y] = None
                rem.delete()
                del rem

        self.move_side = 'black' if self.move_side == 'white' else 'white'
        for highlight in self.hl_vaild:
            self.c.delete(highlight)

    def Click(self, event):
        """"Takes care of marking, unmarking and making moves with the left mouse button"""
        field = self.field_index(event.x, event.y)

        if not field:
            return
        elif self.AI and (self.side != self.move_side):
            return

        for highlight in self.hl_vaild:
            self.c.delete(highlight)

        if type(field) == tuple:
            x, y = field
            field = None
        else:
            x, y = field.x, field.y

        if self.selected:
            if (x, y) in self.moves.keys():  # delete the select chess
                remove = self.moves[(x, y)]
                if remove:
                    for rem in remove:
                        self.board[rem.x][rem.y] = None
                        rem.delete()
                        del rem

                self.board[self.selected.x][self.selected.y] = None
                self.selected.move(x, y)
                self.selected.check_king()
                self.board[x][y] = self.selected
                self.move_side = 'black' if self.move_side == 'white' else 'white'

                if self.AI:
                    self.c.update()
                    self.c.after(500, self.AIMoves())

                if self.check_win():
                    self.root.unbind("<ButtonPress-1>")
                    messagebox.showinfo('Game finished', f'{self.check_win()} won in {self.time} seconds!')
                    self.count_time = False
                    return

            elif field:
                self.selected.unmark()
                self.selected = field
                field.mark()
            self.selected.unmark()
            self.selected = None
        elif field and field.side == self.move_side:
            field.mark()
            self.moves = self.valid_moves((x, y))
            self.selected = field

    def valid(self, selected, field):
        """Determines if the movement from 'selected' to 'field' is valid"""
        if field[0] < 0 or field[0] > 7 or field[1] < 0 or field[1] > 7:
            return False

        if self.board[field[0]][field[1]]:
            return False
        else:
            x, y = field
            if not (x + y) % 2:
                return False

        if selected.side == 'black':
            if selected.y == 7 and not selected.king:
                return False
            shift = (1,)
        else:
            if selected.y == 0 and not selected.king:
                return False
            shift = (-1,)
        if selected.king:
            shift = (-1, 1)

        for i in (-1, 1):
            for j in shift:
                if y - j == selected.y and x + i == selected.x:  # if click a empty
                    return (x, y)

        def bet_coor(axis):  # 中心2极
            a = selected.x if axis == 'x' else selected.y
            b = x if axis == 'x' else y
            return int(a + ((b - a) // 2))

        piece = self.board[bet_coor('x')][bet_coor('y')]
        threatened = self.threatened(piece)

        if not threatened:  # The part between empty and me is not threatened
            return False

        if (selected.x, selected.y) in threatened:  # If my chess pieces threaten
            return (x, y), piece

    def valid_moves(self, field, highlight=True):
        """Returns a dictionary of all possible piece moves"""
        field = self.board[field[0]][field[1]]
        moves = {}
        for i in (-1, 1):
            for j in (-1, 1):
                move = self.valid(field, (field.x + i, field.y + j))
                if move:
                    moves[move] = None

        def long_jump(field, prev=[]):  # Recursively find moved and discarded fragments
            # If player can enter the site in multiple ways, you don't have to choose the best (most popular) //bug
            for i in (-2, 2):
                for j in (-2, 2):
                    if not field:
                        pass
                    else:
                        move = self.valid(field, (field.x + i, field.y + j))
                        if move:
                            x, y = move[0][0], move[0][1]
                            moves[move[0]] = [move[1]] + prev
                            pom = self.board[x][y] = Piece(field.side, (x, y), self.rect_size, field.king)
                            long_jump(pom, prev + [
                                move[1]])  # If I can jump: add TAH, I can jump from this new
                            pom.delete()
                            del pom
                            self.board[x][y] = None

        long_jump(field)

        for move in moves.keys():
            x, y = move
            x *= self.rect_size
            y *= self.rect_size
            if highlight:
                self.hl_vaild.append(self.c.create_rectangle(
                    x, y, x + self.rect_size, y + self.rect_size,
                    fill='', outline='red', width=3))

        return moves

    def field_index(self, x, y):
        """ Returns the figure / indexes of the board field from the given coordinates on the surface threatened (piece)
        """
        x, y = int(x // self.rect_size), int(y // self.rect_size)
        if x == 8 or y == 8:
            return False
        if self.board[x][y]:
            return self.board[x][y]
        else:
            return (x, y)

    def threatened(self, piece):
        """Returns an array of figure coordinates that threaten 'piece' around + -1"""
        if not piece:
            return False
        x, y = piece.x, piece.y
        if x in (0, 7) or y in (0, 7):
            return False
        opponent = 'white' if piece.side == 'black' else 'black'
        out = []
        for i in (-1, 1):
            for j in (-1, 1):
                op = self.board[x + i][y + j]  # threatened chesses
                if op and op.side == opponent and not self.board[x - i][y - j]:  # another is empty
                    if not op.king:
                        if not (piece.side == 'white' and op.y > piece.y) and not (
                                piece.side == 'black' and op.y < piece.y):
                            out.append((x + i, y + j))
                    else:
                        out.append((x + i, y + j))  # threatened chess
        if out == []:
            return False
        return out

    def check_win(self):
        """Finds out if the game is over (there are no pieces in the page)"""
        b, w = 0, 0
        for i in self.board:
            for j in i:
                if j:
                    if j.side == 'white':
                        w += 1
                    else:
                        b += 1
        if not b:
            return 'White'
        elif not w:
            return 'Black'
        return False

    def menu_bar(self):
        """Creates a bar with saving, loading, display the rules the game and shutting down the program"""
        self.side, self.hl_vaild = None, []
        self.count_time, self.add, self.move_side = False, 0, 'black'

        def save():
            if not self.side:
                messagebox.showinfo('WARNING', 'PLEASE CHOOSE ONE SIDE FIRST')
                return

            save_file = filedialog.asksaveasfile(
                mode='w', initialdir='saves', title='Save game',
                filetypes=[('Text files', '*.txt')],
                defaultextension=[('Text files', '*.txt')])

            if not save_file:
                return

            op = 'ai' if self.AI else 'player'
            save_file.write(f'{self.side} {self.time} {op} {self.move_side} ')

            for i in self.board:
                for j in i:
                    if j:
                        k = 'k' if j.king else 'n'
                        save_file.write(f'{j.x}/{j.y}/{j.side}/{k} ')

        def load():
            if not self.side:
                messagebox.showinfo('WARNING', 'PLEASE CHOOSE ONE SIDE FIRST')
                return

            save_file = filedialog.askopenfilename(
                initialdir='saves', title='Load game',
                filetypes=[('Text files', '*.txt')])
            if not save_file:
                return

            with open(save_file, 'r') as file:
                line = file.readline().split()

            self.side, self.add = line[0], int(line[1])
            self.AI = True if line[2] == 'ai' else False
            self.move_side = line[3]
            self.c.delete('all')
            self.DrawBoard()
            self.board = [[None for i in range(8)] for j in range(8)]

            for i in line[4:]:
                x, y, side, king = i.split('/')
                k = True if king == 'k' else False
                self.board[int(x)][int(y)] = Piece(side, (int(x), int(y)), self.rect_size, k)
            if self.AI and self.side != self.move_side:
                self.c.update()
                self.c.after(1000, self.AIMoves())
        def rule():
            messagebox.showinfo("RULE" ,'Checkers is a game for two players. '
                                'Each player receives twelve, flat disk-like '
                                'pieces which are placed on the black squares '
                                'in the manner indicated in the diagram at the left.'
                                'Be sure that a light-coloured square appears in the '
                                'lower right-hand corner of the board. The darker-coloured '
                                'checkers are usually designated black, and the lighter colour '
                                'is designated white. Black always moves first. ')


        def exit():
            if tk.messagebox.askyesno('Exit', 'Do you want to quit the game?'):
                self.root.destroy()

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        subMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="ClickTHERE", menu=subMenu)
        subMenu.add_command(label="SAVE", command=save)
        subMenu.add_command(label="LOAD", command=load)
        subMenu.add_command(label="RULE", command=rule)
        subMenu.add_command(label="EXIT", command=exit)
