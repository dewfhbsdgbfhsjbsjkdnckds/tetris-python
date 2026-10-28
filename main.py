import time
import os
import termios, sys
import random
import threading 
from threading import Event
from collections import deque

#def test():
#    print("hello")

class HasGrid:
    """Interface for classes which have a grid"""
    def get_rows_count(self):
        """Returns the amount of rows"""
        pass
    def get_cols_count(self):
        """Returns the amount of cols"""
        pass
    def get_at(self, i, j):
        """Gets the value at i, j"""
        pass

class HasMutableGrid(HasGrid):
    """Has mutable gird interface"""
    def set_at(self, i, j, val):
        """Sets the value at i, j to val"""
        pass


class Displayable:
    """Interface for displaying"""
    def display():
        """Prints self"""
        pass

    def display_on_blank_screen(self):
        """Prints self on blank screen

        Does not need to implemented manually
        """
        print("\x1b[1;1H")
        print("\x1b[2J")
        self.display();
        pass

class Clonable:
    """Clonable Interface"""
    def clone(self):
        """Returns a deep copy of self"""
        pass

class Piece(Clonable, HasGrid):
    """Falling Tetris Piece class

    While the grid does mutate, it doesnt need to implement HasMutableGrid.
    You probably shouldnt be mutating this class from another class, just rotating it
    """
    def clone(self):
        new_piece = Piece("Empty");
        grid = self._grid.clone();
        new_piece._grid = grid;
        return new_piece;

    def __str__(self):
        return str(self._grid)

    def __init__(self, kind):
        """Initialises based on string kind

        Kind is standard tetris piece naming convention
        """
        if kind == "Empty":
            self._grid = BlockGrid(0, 0);
        elif kind == "L":
            self._grid = BlockGrid(3, 2);
            # []
            # []
            # [] []
            self._grid.set_at(0, 0, True);
            self._grid.set_at(1, 0, True);
            self._grid.set_at(2, 0, True);
            self._grid.set_at(2, 1, True);
        elif kind == "Z":
            self._grid = BlockGrid(2, 3);
                # [] []
                #    [] []
            self._grid.set_at(0, 0, True);
            self._grid.set_at(0, 1, True);
            self._grid.set_at(1, 1, True);
            self._grid.set_at(1, 2, True);
        elif kind == "S":
            self._grid = BlockGrid(2, 3);
                #    [] []
                # [] []
            self._grid.set_at(0, 1, True);
            self._grid.set_at(0, 2, True);
            self._grid.set_at(1, 0, True);
            self._grid.set_at(1, 1, True);
        elif kind == "O":
            self._grid = BlockGrid(2, 2);
                # [] []
                # [] []
            self._grid.set_at(0, 0, True);
            self._grid.set_at(0, 1, True);
            self._grid.set_at(1, 0, True);
            self._grid.set_at(1, 1, True);
        elif kind == "I":
            self._grid = BlockGrid(4, 1);
                # []
                # []
                # []
                # []
            self._grid.set_at(0, 0, True);
            self._grid.set_at(1, 0, True);
            self._grid.set_at(2, 0, True);
            self._grid.set_at(3, 0, True);
        elif kind == "J":
            self._grid = BlockGrid(3, 2);
            #    []
            #    []
            # [] []
            self._grid.set_at(0, 1, True);
            self._grid.set_at(1, 1, True);
            self._grid.set_at(2, 0, True);
            self._grid.set_at(2, 1, True);
        elif kind == "T":
            self._grid = BlockGrid(2, 3);
                # [] [] []
                #    []
            self._grid.set_at(0, 0, True);
            self._grid.set_at(0, 1, True);
            self._grid.set_at(0, 2, True);
            self._grid.set_at(1, 1, True);
        else:
            raise ValueError("invalid kind passed")

    def get_rows_count(self):
        return self._grid.get_rows_count()

    def get_cols_count(self):
        return self._grid.get_cols_count()

    def get_at(self, i, j):
        return self._grid.get_at(i, j);

    def rotate_clockwise(self):
        # when i is 0, want to set_at(j, 1)
        # when i is 1, want to set_at(j, 0)
        # [] []   
        #    [] []
        # turns to
        #    []
        # [] []
        # []   
        old_grid = self._grid.clone(); # just to make sure deep copy happens
        old_rows_count = self.get_rows_count();
        old_cols_count = self.get_cols_count();
        self._grid = BlockGrid(old_cols_count, old_rows_count);
        for i in range(0, old_rows_count):
            for j in range(0, old_cols_count):
                old_val = old_grid.get_at(i, j);
                self._grid.set_at(j, (old_rows_count - 1) - i, old_val);

    def rotate_counter_clockwise(self):
        # [] []
        # []
        # []
        # turns to
        # []
        # [] [] []
        old_grid = self._grid.clone(); # just to make sure deep copy happens
        old_rows_count = old_grid.get_rows_count();
        old_cols_count = old_grid.get_cols_count();
        self._grid = BlockGrid(old_cols_count, old_rows_count);
        for i in range(0, old_rows_count):
            for j in range(0, old_cols_count):
                old_val = old_grid.get_at(i, j);
                self._grid.set_at((old_cols_count - 1) - j, i, old_val);

class BlockGrid(Clonable, HasMutableGrid):
    """Class which represents a grid of blocks"""
    def __init__(self, rows, cols):
        if type(rows) is not int:
            raise ValueError("rows should be an integer type")
        if type(cols) is not int:
            raise ValueError("cols should be an integer type")
        self._grid = []
        # needed to stop shallow copying
        for i in range(0, rows):
            rowlist = []
            for j in range(0, cols):
                rowlist.append(False)
            self._grid.append(rowlist)
        #if self.get_rows_count() != rows:
        #    raise Exception
        #if self.get_cols_count() != cols:
        #    raise Exception


    def clone(self):
        out = BlockGrid(self.get_rows_count(), self.get_cols_count());
        for i in range(0, self.get_rows_count()):
            for j in range(0, self.get_cols_count()):
                out.set_at(i, j, self.get_at(i, j));
        return out;

    def __str__(self):
        out = ""
        for i in range(0, self.get_rows_count()):
            for j in range(0, self.get_cols_count()):
                if self._grid[i][j] == True:
                    out = out + "[]"
                else:
                    out = out + "--"
            out = out + "\n"
        return out

    def set_at(self, i, j, item):
        if type(item) is not bool:
            raise ValueError("item should be a bool type")
        if type(i) is not int:
            raise ValueError("i should be an integer type")
        if type(j) is not int:
            raise ValueError("j should be an integer type")
        self._grid[i][j] = item

    def get_at(self, i, j):
        if type(i) is not int:
            raise ValueError("i should be an integer type")
        if type(j) is not int:
            raise ValueError("j should be an integer type")
        if i >= self.get_rows_count():
            return None;
        if j >= self.get_cols_count():
            return None;
        return self._grid[i][j]

    def get_rows_count(self):
        return len(self._grid)

    def get_cols_count(self):
        return len(self._grid[0])

    # i should probably return an error type
    # one that has an error kind,
    # but idk if python has that
    #def add_piece_in_top_middle(self, piece):
    #    # TODO
    #    output = self.clone();
    #    if type(piece) is not Piece:
    #        #raise ValueError("item should be a bool type")
    #        return None;
    #    #piece_grid = BlockGrid(self.get_rows_count(), self.get_cols_count());
    #    if (piece.get_rows_count() > self.get_rows_count() or 
    #        piece.get_cols_count() > self.get_cols_count()):
    #        return None;
    #        #raise ValueError("piece cannot be larger than the grid")
    #    starting_col = (self.get_cols_count() - 1) // 2;
    #    for i in range(0, piece.get_rows_count()):
    #        for j in range(0, piece.get_cols_count()):
    #            # check if adding piece conflicts
    #            if (output.get_at(i, j + starting_col) == True and
    #                piece.get_at(i, j) == True):
    #                    return None;
    #            output.set_at(i, j + starting_col, piece.get_at(i, j))
    #    return output

class BoardIndex(Clonable):
    """Represents an index into a board"""
    def __init__(self, i, j):
        self._i = i;
        self._j = j;

    def clone(self):
        return BoardIndex(self.i(), self.j());

    def __str__(self):
        return f"i: {self._i}, j: {self._j}"

    def i(self):
        """Returns the i part of the index"""
        return self._i;

    def j(self):
        """Returns the j part of the index"""
        return self._j;
    
    def set_i(self, i):
        """Sets the i part of the index"""
        self._i = i;

    def set_j(self, j):
        """Sets the j part of the index"""
        self._j = j;

class Board(Displayable):
    """Represents a Tetris board

    Contains a Grid which has all of the solid pieces
    Contains a Piece which is the falling piece
    """
    def __init__(self, rows, cols):
        if type(rows) is not int:
            raise ValueError("rows should be an integer type")
        if type(cols) is not int:
            raise ValueError("cols should be an integer type")
        self._rows = rows
        self._cols = cols
        # initialise empty blocks
        self._placed_blocks = BlockGrid(rows, cols);
        self._falling_piece = None;
        self._falling_piece_pos = None;

    def is_falling_piece_oob(self):
        """Returns whether the falling piece is out of bounds"""
        if self._falling_piece_pos.j() < 0 == True:
            return True;
        if (self._falling_piece_pos.j() + self._falling_piece.get_cols_count() >= self.get_cols_count()) == True:
            return True;
        if (self._falling_piece_pos.i() + self._falling_piece.get_rows_count() >= self.get_rows_count()) == True:
            return True;
        return False

    def is_falling_piece_oob_or_colliding(self):
        """Returns whether the falling piece is out of bounds or colliding"""
        return (self.is_falling_piece_oob() == True or self.is_piece_colliding() == True);

    def rotate_falling_piece_counter_clockwise(self):
        """Rotates the falling piece counter clockwise"""
        if self.has_falling_piece():
            if self.is_piece_colliding():
                return;
            # clone necessary here
            old_piece = self._falling_piece.clone();
            old_piece_pos = self._falling_piece_pos.clone();
            self._falling_piece.rotate_counter_clockwise();
            if self.is_falling_piece_oob_or_colliding():
                self._falling_piece = old_piece;
                self._falling_piece_pos = old_piece_pos;

    def rotate_falling_piece_clockwise(self):
        """Rotates the falling piece clockwise"""
        if self.has_falling_piece():
            if self.is_piece_colliding():
                return;
            # clone necessary here
            old_piece = self._falling_piece.clone();
            old_piece_pos = self._falling_piece_pos.clone();
            self._falling_piece.rotate_clockwise();
            if self.is_falling_piece_oob_or_colliding():
                self._falling_piece = old_piece;
                self._falling_piece_pos = old_piece_pos;

    # should probably be private...?
    def falling_piece_value_at(self, i, j):
        if (self._falling_piece is None
            or self._falling_piece_pos is None):
            return False;
        index_i = i - self._falling_piece_pos.i();
        index_j = j - self._falling_piece_pos.j();
        if index_i < 0:
            return False;
        if index_j < 0:
            return False;
        return self._falling_piece.get_at(index_i, index_j);

    def get_at(self, i, j):
        if i >= self.get_rows_count():
            return None;
        if j >= self.get_cols_count():
            return None;
        if (self._placed_blocks.get_at(i, j) == True
            or self.falling_piece_value_at(i, j) == True):
            return True;
        return False;

    def set_at(self, i, j, value):
        self._placed_blocks.set_at(i, j, value);

    def __str__(self):
        out = ""
        for i in range(0, self.get_rows_count()):
            for j in range(0, self.get_cols_count()):
                if self.get_at(i, j) == True:
                    out = out + "[]";
                else:
                    out = out + "--";
            out = out + "\n";
        #out = out + "falling block pos: " + str(self._falling_piece_pos);
        return out;

    def get_rows_count(self):
        return self._rows

    def get_cols_count(self):
        return self._cols

    def has_falling_piece(self):
        # Returns whether the board currently has a falling piece"""
        return (self._falling_piece is not None and self._falling_piece_pos is not None);

    # python doesnt have move semantics so just
    # pretend like this consumes self
    # itll probably be in an invalid state
    # after this anyways

    # TODO make it rotate piece to try fit
    def add_piece_in_top_middle(self, piece):
        """Adds a piece in the top middle of the board

        Moves self,
        this means you should not continue using self after 
        this method is called.

        Returns:
            self
        """
        if type(piece) is not Piece:
            return None;
        if (piece.get_rows_count() > self.get_rows_count() or 
            piece.get_cols_count() > self.get_cols_count()):
            return None;
        piece_middle_pos = (self.get_cols_count() - 1) // 2;
        piece_width = piece.get_cols_count();
        amount_to_shift = (piece_width - 1) // 2;
        piece_pos = piece_middle_pos - amount_to_shift;

        self._falling_piece = piece;
        self._falling_piece_pos = BoardIndex(0, piece_pos);

        # check if piece collides
        if self.is_piece_colliding() == True:
            return None;
        return self;

    def is_piece_colliding(self):
        """Returns whether the falling piece is colliding with any solid blocks"""
        for i in range(0, self._falling_piece.get_rows_count()):
            for j in range(0, self._falling_piece.get_cols_count()):
                val_of_piece = self._falling_piece.get_at(i, j);
                val_of_board = self._placed_blocks.get_at(i + self._falling_piece_pos.i(), j + self._falling_piece_pos.j());
                if (val_of_piece == True) and (val_of_board == True):
                    return True;
        return False;

    def line_clear(self):
        """Clears any fully occupied rows"""
        rows_to_clear = [];
        for i in range(0, self.get_rows_count()):
            all_occupied = True;
            for j in range(0, self.get_cols_count()):
                if self.get_at(i, j) == False:
                    all_occupied = False;
            if all_occupied:
                rows_to_clear.append(i);
        for i, row in enumerate(rows_to_clear):
            #row_num = i + row;
            for j in range(row - 1, 0, -1):
                for k in range(0, self.get_cols_count()):
                    val = self.get_at(j, k);
                    self.set_at(j + 1, k, val);

    # this should probably be private as you need to check for oob and collision first
    def solidify_falling_piece(self):
        """Solidifies the falling piece"""
        for i in range(0, self._falling_piece.get_rows_count()):
            for j in range(0, self._falling_piece.get_cols_count()):
                piece_val = self._falling_piece.get_at(i, j);
                if piece_val is None:
                    return None;
                if piece_val == True:
                    self.set_at(i + self._falling_piece_pos.i(), j + self._falling_piece_pos.j(), True);
        # TODO add line clear logic
        self._falling_piece = None;
        self._falling_piece_pos = None;
        self.line_clear();

    def try_move_falling_piece_left(self):
        """Tries to move the falling piece left"""
        if self._falling_piece_pos is None or self._falling_piece is None:
            return False;
        if self._falling_piece_pos.j() == 0:
            return False;
        old_pos = self._falling_piece_pos.j();
        self._falling_piece_pos.set_j(old_pos - 1);
        if self.is_piece_colliding():
            self._falling_piece_pos.set_j(old_pos);
            return False;
        return True;

    def try_move_falling_piece_right(self):
        """Tries to move the falling piece right"""
        if self._falling_piece_pos is None or self._falling_piece is None:
            return False;
        if self._falling_piece_pos.j() + self._falling_piece.get_cols_count() == self.get_cols_count():
            return False;
        old_pos = self._falling_piece_pos.j();
        self._falling_piece_pos.set_j(old_pos + 1);
        if self.is_piece_colliding():
            self._falling_piece_pos.set_j(old_pos);
            return False;
        return True;

    def display(self):
        print(self);

    def try_advance_falling_piece(self):
        """Tries to move the falling piece down, or solidify it"""
        if self.has_falling_piece() == False:
            return None;
        # check if on bottom of board
        if (self._falling_piece_pos.i() + self._falling_piece.get_rows_count() == self.get_rows_count()):
            self.solidify_falling_piece();
            return self;
        if self.is_piece_colliding() == False:
            old_pos = self._falling_piece_pos.i();
            self._falling_piece_pos.set_i(self._falling_piece_pos.i() + 1);
            if self.is_piece_colliding() == True:
                self._falling_piece_pos.set_i(old_pos);
                self.solidify_falling_piece();
            return self;
        else:
            return None;

def main():
    stdin_fd = sys.stdin.fileno()
    new = termios.tcgetattr(stdin_fd)
    new[3] = new[3] & ~termios.ECHO 
    new[3] = new[3] & ~termios.ICANON
    try:
        termios.tcsetattr(stdin_fd, termios.TCSANOW, new)
    except Exception:
        sys.stderr.write("Error turning off ICANON and ECHO mode\n")
        return

    queue = deque([]);
    board = Board(20, 10);
    locked = Event();
    should_stop = Event();
    thread = threading.Thread(target=read_stdin_thread_to_queue, args = (queue, board, locked, should_stop));
    thread.start()

    falling_pieces_list = ["O", "I", "S", "Z", "L", "J", "T"];
    while True:
        locked.set();
        # do inputs that were blocked by critical section
        while True:
            try:
                game_input = queue.popleft();
                print("queue was nonempty");
                if game_input.is_left():
                    board.try_move_falling_piece_left();
                elif game_input.is_right():
                    board.try_move_falling_piece_right();
            except Exception:
                break;

        if board.has_falling_piece() == False:
            board.add_piece_in_top_middle(Piece(random.choice(falling_pieces_list)));
            if board.is_piece_colliding():
                print("you lost");
                should_stop.set();
                thread.join()
                return
        else:
            new_board = board.try_advance_falling_piece();
            if new_board is None:
                print("new board is none")
                should_stop.set();
                return
            board = new_board
        #print(board)
        board.display_on_blank_screen();
        locked.clear();
        time.sleep(0.5)

    # needed because input() will wait for \n
    # this is more suitable for reading 
    #read_bytes = os.read(stdin_fd, 100);
    #print(read_bytes)

class GameInput:
    """Represents a possible input in the game"""
    def is_left(self):
        return self._input_type == "L";
    def is_right(self):
        return self._input_type == "R";

    def __init__(self, input_type):
        if (input_type != "L" and input_type != "R"
            and input_type != "RotateClockwise"
            and input_type != "RotateAntiClockwise"):
            raise ValueError("incorrect input value")
        else:
            self._input_type = input_type;

def read_stdin_thread_to_queue(queue, board, locked, should_stop):
    """Reads input from stdin, tries to execute inputs"""
    while True:
        if should_stop.is_set():
            break;
        stdin_fd = sys.stdin.fileno();
        read_bytes = os.read(stdin_fd, 100);
        if read_bytes == b'\x1b[D':
            if locked.is_set():
                queue.append(GameInput("L"))
            else:
                board.try_move_falling_piece_left();
                board.display_on_blank_screen()
        elif read_bytes == b'\x1b[C':
            if locked.is_set():
                queue.append(GameInput("R"))
            else:
                board.try_move_falling_piece_right();
                board.display_on_blank_screen()
        elif read_bytes == b'a':
            if locked.is_set():
                queue.append(GameInput("L"))
            else:
                board.try_move_falling_piece_left();
                board.display_on_blank_screen()
        elif read_bytes == b'd':
            if locked.is_set():
                queue.append(GameInput("R"))
            else:
                board.try_move_falling_piece_right();
                board.display_on_blank_screen();
        elif read_bytes == b'k':
            if locked.is_set():
                queue.append(GameInput("RotateClockwise"))
            else:
                board.rotate_falling_piece_clockwise();
                board.display_on_blank_screen();
        elif read_bytes == b'j':
            if locked.is_set():
                queue.append(GameInput("RotateCounterClockwise"));
            else:
                board.rotate_falling_piece_counter_clockwise();
                board.display_on_blank_screen();

if __name__ == "__main__":
    stdin_fd = sys.stdin.fileno()
    old = termios.tcgetattr(stdin_fd)
    try:
        main()
    except Exception as e:
        raise e
    # set attributes back to old attributes
    finally:
        try:
            termios.tcsetattr(stdin_fd, termios.TCSANOW, old)
        except Exception:
            sys.stderr.write("Error setting terminal attributes back to normal\n")
