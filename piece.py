class Piece(object):
    """"Class of figure, content information about position, side and graphics"""
    c = None

    def __init__(self, Side, Position, Size, King=False):
        """"initialize the parameters"""
        self.side = Side
        self.king = King
        self.pos = Position
        self.x, self.y = Position
        self.size = Size

        self.marked = False
        self.outline = None
        self.colour = '#FFFFFF' if Side == 'white' else '#000000'  # pieces colours
        self.circle = self.draw('', self.colour)
        self.check_king()

    def coord(self):
        """Returns the coordinates needed to draw graphic objects"""
        size_r = self.size * 0.8
        shift = int((self.size - size_r) // 2)
        x, y = self.x * self.size + shift, self.y * self.size + shift
        return (x, y, size_r)

    def check_king(self):
        """Checks if the piece has not become king. If so, it will create a crown"""
        if not self.king:
            if self.side == 'white' and self.y == 0:
                self.king = True
            elif self.side == 'black' and self.y == 7:
                self.king = True
        if self.king:
            c = 'white' if self.side == 'black' else 'black'
            x, y, size_r = self.coord()
            fsize = f'helvetica {int(self.size * 0.5)}'
            self.coin = self.c.create_text(x + size_r / 2, y + size_r // 2, text='♔', font=fsize, fill=c)

    def draw(self, outline, fill=''):
        """Creates a circle with the given properties in its position"""
        x, y, size_r = self.coord()
        return self.c.create_oval(x, y, x + size_r, y + size_r, fill=fill, outline=outline, width=int(size_r * 0.05))

    def mark(self):
        """Graphically marks the selected figure"""
        self.outline = self.draw('red')
        self.marked = True

    def unmark(self):
        """"Deselects the selected figure (the graphic object is deleted)"""
        self.c.delete(self.outline)
        self.marked = False

    def delete(self):
        """Removes all graphics"""
        self.c.delete(self.circle)
        if self.king:
            self.c.delete(self.coin)

    def move(self, x, y):
        """Moves the piece to the given position"""
        self.unmark()
        self.c.delete(self.circle)
        if self.king:
            self.c.delete(self.coin)
        self.x, self.y = x, y
        self.circle = self.draw('', self.colour)
