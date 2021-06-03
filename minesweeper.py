import random
import sys
import os
import string

import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.signal import convolve2d
from scipy.misc import imsave, imread


def generate_minefield(rows, cols, num_mines, r, c):
    # generate mines
    mines = np.zeros((rows,cols), dtype=bool)
    count = 0
    while count < num_mines:
        x,y = random.randint(0,rows-1), random.randint(0,cols-1)
        if r!=x and c!=y:
            if not mines[x,y]:
                mines[x,y] = 1
                count += 1
    # count the number of mine neighbors.
    neighbors = convolve2d(mines, np.ones((3,3)), mode='same', boundary='fill')
    neighbors[mines] = 9 # Locations with mines are set to 9.
    return neighbors.astype(np.uint8)
        
def user_input_good(input_string, input_type='int', boxName=''):
    if len(input_string) == 0:
        messagebox.showwarning(
                "Input error",
                ''.join((boxName, ' value is missing.')))
        return False

    if input_type == 'int':
        bad = ''.join((string.ascii_letters, string.punctuation,
                       string.whitespace))
        if any((c in bad) for c in input_string):
            messagebox.showwarning(
                "Input error",
                ''.join((boxName, ' should be a positive integer value')))
            return False
        else:
            return True

class LabelAndEntry(tk.Frame):
    """
    A label and entry widget in a frame.
    Call .get() to get the input text
    Call .check() to make sure the input is convertable to the proper dtype.
    """
    def __init__(self, parent, label_text, label_width=12, entry_width=5,
                 entry_start=None, input_type='int', padx=2, pady=2):
        
        tk.Frame.__init__(self, parent)
        self.label_text = label_text
        self.label_width = label_width
        self.entry_width = entry_width
        self.input_type = input_type
        self.entry_start = entry_start
        self.padx = padx
        self.pady = pady

        self.input_string = tk.StringVar()

        # Create widgets
        self.label = tk.Label(self, text=self.label_text,
                              width=self.label_width, anchor='e')
        self.entry = tk.Entry(self, width=self.entry_width,
                              textvariable=self.input_string)

        # Place widgets
        self.label.grid(row=0, column=0, padx=0, pady=pady)
        self.entry.grid(row=0, column=1, padx=padx, pady=pady)

        # Put start value into input text
        if self.entry_start is not None:
            self.input_string.set(str(entry_start))

    def check(self):
        
        if self.input_type is not None:
            return user_input_good(self.input_string.get(),
                                            self.input_type,
                                            self.label_text)
            
        else:
            print('Input type was not specified.  Cannot check user input.')
            return True

    def get(self):
        return self.input_string.get()

class Minesweeper(tk.Frame):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Minesweeper')
        tk.Frame.__init__(self, self.root)
        self.pack()

        self.level = 0
        self.manage_high_scores()

        # Minefield metrics
        self.rows = 9
        self.cols = 9
        self.num_mines = 10

        # Images
        self.im = {'1' : tk.PhotoImage(file='assets/1.gif'),
                   '2' : tk.PhotoImage(file='assets/2.gif'),
                   '3' : tk.PhotoImage(file='assets/3.gif'),
                   '4' : tk.PhotoImage(file='assets/4.gif'),
                   '5' : tk.PhotoImage(file='assets/5.gif'),
                   '6' : tk.PhotoImage(file='assets/6.gif'),
                   '7' : tk.PhotoImage(file='assets/7.gif'),
                   '8' : tk.PhotoImage(file='assets/8.gif'),
                   '9' : tk.PhotoImage(file='assets/rbomb.gif'),
                   '0' : tk.PhotoImage(file='assets/0.gif'),
                   'c1' : tk.PhotoImage(file='assets/c1.gif'),
                   'c2' : tk.PhotoImage(file='assets/c2.gif'),
                   'c3' : tk.PhotoImage(file='assets/c3.gif'),
                   'c4' : tk.PhotoImage(file='assets/c4.gif'),
                   'c5' : tk.PhotoImage(file='assets/c5.gif'),
                   'c6' : tk.PhotoImage(file='assets/c6.gif'),
                   'c7' : tk.PhotoImage(file='assets/c7.gif'),
                   'c8' : tk.PhotoImage(file='assets/c8.gif'),
                   'c9' : tk.PhotoImage(file='assets/c9.gif'),
                   'c0' : tk.PhotoImage(file='assets/c0.gif'),
                   'flag' : tk.PhotoImage(file='assets/flag.gif'),
                   'bomb' : tk.PhotoImage(file='assets/bomb.gif'),
                   'xbomb' : tk.PhotoImage(file='assets/xbomb.gif'),
                   'blank' : tk.PhotoImage(file='assets/blank.gif'),
                   'smile' : tk.PhotoImage(file='assets/smile_smile.gif'),
                   'o' : tk.PhotoImage(file='assets/smile_o.gif'),
                   'cool' : tk.PhotoImage(file='assets/smile_cool.gif'),
                   'dead' : tk.PhotoImage(file='assets/smile_dead.gif')
                    }

        # Top frame
        self.top_frame = tk.Frame(self, relief = tk.SUNKEN, bd=3)
        self.top_frame.pack(fill=tk.X, expand=1, padx=3, pady=3)

        # Smile button
        self.but_smile = tk.Button(self.top_frame, image=self.im['smile'],
                                   command=self.restart, bd=3)

        #digital
        self.counter_frame = tk.Frame(self.top_frame, bd=0)
        self.clock_frame = tk.Frame(self.top_frame, bd=0)

        # pack top frame
        self.counter_frame.pack(side='left', anchor='w', expand=1, padx=3, pady=3)
        self.but_smile.pack(side='left', anchor='c', expand=1, padx=3, pady=3)
        self.clock_frame.pack(side='left', anchor='e',expand=1,padx=3, pady=3)

        self.lab_clock = []
        self.lab_count = []
        for i in range(3):
            self.lab_clock.append(tk.Label(self.clock_frame, bd=0,
                                           image=self.im['c0']))
            self.lab_count.append(tk.Label(self.counter_frame, bd=0,
                                           image=self.im['c0']))
            self.lab_clock[-1].grid(row=0, column=i, padx=0, pady=0)
            self.lab_count[-1].grid(row=0, column=i, padx=0, pady=0)
            
                                      
        
        # keep track of mouse clicks
        self.was_both_click = False
        self.was_left_click = False
        self.was_right_click = False
        self.both_click_timer = 0
        
        # Frame that holds mine buttons.
        self.minefield_frame = tk.Frame(self, relief=tk.SUNKEN, bd=3)
        self.minefield_frame.pack(fill=tk.X, expand=1, padx=5, pady=5)

        self.restart()

        # Create menu
        self.menubar = tk.Menu(self)
        
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Game", menu=menu)
        menu.add_command(label="New Game           F2", command=self.restart)
        menu.add_command(label="High Scores         F4", command=self.view_high_scores)
        menu.add_command(label="Options                F5", command=self.options)
        menu.add_command(label="Exit")

        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=menu)
        menu.add_command(label="Instructions")
        menu.add_command(label="About")

        self.root.config(menu=self.menubar)
        
        # Keep track of clicking
        self.left_click = False
        self.right_click = False
        self.root.bind('<Button-1>', self.lefttclick)
        self.root.bind('<Button-3>', self.rightclick)
        self.root.bind('<ButtonRelease-1>', self.nolefttclick)
        self.root.bind('<ButtonRelease-3>', self.norightclick)
        self.root.bind('<F5>', self.f5_options)
        self.root.bind('<F4>', self.f4_hs)

        self.root.after(50, self.check_clicked)

        self.root.after(1000, self.update_clock)
        self.root.mainloop()

    def restart(self):
        self.time = -1
        self.first = True
        self.dead = False
        self.gameover = False
        self.but_smile.config(image=self.im['smile'])
        self.lab_clock[2].config(image=self.im['c0'])
        self.lab_clock[1].config(image=self.im['c0'])
        self.lab_clock[0].config(image=self.im['c0'])
        self.update_counter(self.num_mines)
        
        # keep track of what buttons have been clicked and where the mouse is
        self.clicked = np.zeros((self.rows, self.cols), dtype=bool)
        self.rclicked = np.zeros((self.rows, self.cols), dtype=bool)
        self.entered = np.zeros((self.rows, self.cols), dtype=bool)
        # Make buttons.
        self.btn =  [[0 for c in range(self.cols)] for r in range(self.rows)] 
        for r in range(self.rows):
            for c in range(self.cols):
                self.btn[r][c] = tk.Label(
                    self.minefield_frame, bd=0, image=self.im['blank'],
                    padx=0, pady=0, relief=tk.FLAT)
                self.btn[r][c].grid(row=r, column=c)
                self.btn[r][c].bind('<Enter>', lambda event, x=r, y=c: self.enter(x,y))
                self.btn[r][c].bind('<Leave>', lambda event, x=r, y=c: self.leave(x,y))
                
    def enter(self, r, c):
        self.entered[r, c] = 1

    def leave(self, r, c):
        self.entered[r,c] = 0
        
    def check_clicked(self):
        if not self.right_click and not self.left_click: # no click
            self.both_click_timer = 0
            if np.count_nonzero(self.entered) > 1:
                print("Program thinks the mouse is on more than one thing.")
            elif np.count_nonzero(self.entered) == 0:
                pass # No worries, the mouse is outside the minefield.
            else:
                mouse_loc = np.argwhere(self.entered) 
                r = mouse_loc[0,0]
                c = mouse_loc[0,1]
                if self.was_left_click:
                    self.click(r,c)
                if self.was_right_click:
                    self.rclick(r,c)
                if self.was_both_click:
                    self.bclick(r,c)
            self.was_both_click = False
            self.was_left_click = False
            self.was_right_click = False
        elif self.left_click and self.right_click: # both click
            self.was_both_click = True
            self.was_left_click = False
            self.was_right_click = False
        elif  self.right_click: # right click
            if self.was_both_click and self.both_click_timer < 5:
                self.both_click_timer += 1
            else:
                self.both_click_timer = 0
                self.was_both_click = False
                self.was_left_click = False
                self.was_right_click = True
        elif  self.left_click: # left click
            if self.was_both_click and self.both_click_timer < 5:
                self.both_click_timer += 1
            else:
                self.both_click_timer = 0
                self.was_both_click = False
                self.was_left_click = True
                self.was_right_click = False

        self.root.after(30, self.check_clicked)
        
        
    def rightclick(self, event):
        self.right_click = True

    def lefttclick(self, event):
        if not self.dead:
            self.but_smile.config(image=self.im['o'])
        self.left_click = True

    def norightclick(self, event):
        
        self.right_click = False

    def nolefttclick(self, event):
        if not self.dead:
            self.but_smile.config(image=self.im['smile'])
        self.left_click = False

    def bclick(self, r, c):
        if self.clicked[r,c] and not self.gameover:
            neighboring_flags = convolve2d(
                self.rclicked, np.ones((3,3)), mode='same', boundary='fill')
            if neighboring_flags[r,c] == self.minefield[r,c]:
                for x in range(r-1, r+2):
                    for y in range(c-1, c+2):
                        if x>=0 and x < self.rows and y>=0 and y < self.cols:
                            if not self.clicked[x,y]:
                                self.click(x,y)
        
            
    def rclick(self,r,c):
        if not self.clicked[r,c] and not self.first and not self.gameover:
            if self.rclicked[r,c]:
                self.rclicked[r,c] = False
                self.btn[r][c].config(image=self.im['blank'])
            else:
                self.rclicked[r,c] = True
                self.btn[r][c].config(image=self.im['flag'])
        
        self.update_counter(self.num_mines - np.count_nonzero(self.rclicked))
        
    def click(self,r, c):
        if self.first and not self.gameover:
            # Generate minefield.
            self.minefield = generate_minefield(self.rows, self.cols,
                                                self.num_mines,
                                                r, c)
            self.first = False
        if not self.clicked[r,c] and not self.rclicked[r,c] and not self.gameover:
            #if self.minefield[r,c]:
            self.btn[r][c].config(image=self.im[str(self.minefield[r,c])])
            self.clicked[r,c] = True
            if self.minefield[r,c] == 9:
                self.lose(r,c)
            elif self.minefield[r,c] == 0: # Click all the other butons
                for x in range(r-1, r+2):
                    for y in range(c-1, c+2):
                        if x>=0 and x < self.rows and y>=0 and y < self.cols:
                            if not self.clicked[x,y]:
                                self.click(x,y)

            if np.count_nonzero(self.clicked) >= self.rows* self.cols - self.num_mines:
                    self.win()

                
    def exit_program(self):
        self.root.destroy()
        sys.exit(0)

    def lose(self, x, y):
        self.gameover=True
        self.but_smile.config(image=self.im['dead'])
        bombs = self.minefield == 9
        bombs = np.argwhere(bombs)
        for r, c in bombs:
            if not self.rclicked[r,c]:
                self.btn[r][c].config(image=self.im['bomb'])
        flags = np.argwhere(self.rclicked)
        for r, c in flags:
            if self.minefield[r,c] != 9:                
                self.btn[r][c].config(image=self.im['xbomb'])
                
        self.btn[x][y].config(image=self.im['9'])
        if tk.messagebox.askyesno("Good game", "You lost.  Play again?"):
            self.restart()
        else:
            self.exit_program()

    def win(self):
        self.gameover = True
        self.but_smile.config(image=self.im['cool'])
        if self.level == 0:
            hs = int(self.highscores['Beginner'].split()[1])
        elif self.level == 1:
            hs = int(self.highscores['Intermediate'].split()[1])
        elif self.level == 2:
            hs = int(self.highscores['Expert'].split()[1])
        else:
            hs = -1

        if self.time < hs:
            self.new_highscore()
        else:
            
            if tk.messagebox.askyesno("Good game", "You won!  Play again?"):
                self.restart()
            else:
                self.root.destroy()
                sys.exit(0)

    def f5_options(self, _):
        self.options()
        
    def options(self):
        self.optionsTL = tk.Toplevel(self)
        self.optionsTL.title('Options')
        self.pack()

        self.var_options = tk.IntVar()

        self.options_beginner = tk.Radiobutton(
            self.optionsTL, text= 'Begginer\n10 mines\n9 x 9 tile grid',
                                               variable = self.var_options,
                                               value=0, justify=tk.LEFT)
        self.options_intermediate = tk.Radiobutton(
            self.optionsTL, text= 'Intermediate\n40 mines\n16 x 16 tile grid',
                                               variable = self.var_options,
                                               value=1, justify=tk.LEFT)
        self.options_expert = tk.Radiobutton(
            self.optionsTL, text= 'Expert\n99 mines\n16 x 30 tile grid',
                                               variable = self.var_options,
                                               value=2, justify=tk.LEFT)
        self.options_custom = tk.Radiobutton(
            self.optionsTL, text= 'Custom',
                                               variable = self.var_options,
                                               value=3, justify=tk.LEFT)

        self.but_options_ok = tk.Button(self.optionsTL,
                                        text = 'Ok', width = 12,
                                    command = self.options_ok)
        self.but_options_cancel = tk.Button(self.optionsTL,
                                            text = 'Cancel', width = 12,
                                        command = self.options_cancel)



        self.options_beginner.grid(row=0, column=0, sticky='w', padx=10, pady=3)
        self.options_intermediate.grid(row=1, column=0, sticky='w', padx=10, pady=3)
        self.options_expert.grid(row=2, column=0, sticky='w', padx=10, pady=3)
        self.options_custom.grid(row=0, column=1, sticky='e', padx=10, pady=3)
        self.but_options_ok.grid(row=3, column=0, stick='e', padx=20, pady=10)
        self.but_options_cancel.grid(row=3, column=1, stick='w', padx=20, pady=10)

        self.var_op_rows = tk.StringVar()
        self.var_op_cols = tk.StringVar()
        self.var_op_mines = tk.StringVar()
        self.custom_frame = tk.Frame(self.optionsTL)
        self.custom_frame.grid(row=1, column=1)
        self.op_rows = LabelAndEntry(self.custom_frame, 'Rows:')
        self.op_cols = LabelAndEntry(self.custom_frame, 'Columns:')
        self.op_mines = LabelAndEntry(self.custom_frame, 'Mines:')
        self.op_rows.grid(row=0, column=0, sticky='e')
        self.op_cols.grid(row=1, column=0, sticky='e')
        self.op_mines.grid(row=2, column=0, sticky='e')

    def options_ok(self):
        good = False
        if self.var_options.get() == 0:
            self.rows = 9
            self.cols = 9
            self.num_mines = 10
            self.level = 0
            good = True
        elif self.var_options.get() == 1:
            self.rows = 16
            self.cols = 16
            self.num_mines = 40
            self.level=1
            good = True
        elif self.var_options.get() == 2:
            self.rows = 16
            self.cols = 30
            self.num_mines = 99
            self.level=2
            good = True
        elif self.var_options.get() == 3:
            if self.op_rows.check():
                if self.op_mines.check():
                    if self.op_cols.check():
                        self.rows = int(self.op_rows.get())
                        self.cols = int(self.op_cols.get())
                        self.num_mines = int(self.op_mines.get())
                        self.level=3
                        good = True
        if good:
            self.restart()
            self.optionsTL.destroy()

    def options_cancel(self):
        self.optionsTL.destroy()

    def options_change(self):
        if self.var_options.get() == 3:
            pass
            # ungray options
        else:
            # gray custom things
            pass

    def update_counter(self, val):
        v = str(int(val))
        if val < 10:
            v = ''.join(('00', v))
        elif val < 100:
            v = ''.join(('0', v))
        if val < 0:
            v = '000'
        elif val > 999:
            v = '999'
        self.lab_count[0].config(image=self.im[''.join(('c',v[0]))])
        self.lab_count[1].config(image=self.im[''.join(('c',v[1]))])
        self.lab_count[2].config(image=self.im[''.join(('c',v[2]))])

    def update_clock(self):
        if not self.first and self.time < 999 and not self.gameover:
            self.time += 1
            time = str(int(self.time))
            if self.time < 10:
                time = ''.join(('00', time))
            elif self.time < 100:
                time = ''.join(('0', time))
            self.lab_clock[0].config(image=self.im[''.join(('c',time[0]))])
            self.lab_clock[1].config(image=self.im[''.join(('c',time[1]))])
            self.lab_clock[2].config(image=self.im[''.join(('c',time[2]))])

        self.root.after(1000, self.update_clock)

    def manage_high_scores(self):
        self.fhsfile = 'assets/high_scores.txt'
        self.rhsfile = 'bitio'
        self.highscores = {}
        self.levels = ['Beginner', 'Intermediate', 'Expert']

        if not os.path.exists(self.fhsfile):
            with open(self.fhsfile, 'w') as f:
                string = 'Anonymous 999\nAnonymous 999\nAnonymous 999'
                f.write(string)

        if not os.path.exists(self.rhsfile):
            with open(self.rhsfile, 'w') as f:
                string = ''.join((toHex('Anonymous 999'), '\n',
                                  toHex('Anonymous 999'), '\n',
                                  toHex('Anonymous 999')))
                f.write(string)

        with open(self.rhsfile, 'r') as f:
            for i, line in enumerate(f):
                self.highscores[self.levels[i]] = toStr(line.strip())


    def reset_highscores(self):
        with open(self.rhsfile, 'w') as f:
            string = ''.join((toHex('Anonymous 999'), '\n',
                              toHex('Anonymous 999'), '\n',
                              toHex('Anonymous 999')))
            f.write(string)
        self.highscores['Beginner'] = 'Anonymous 999'
        self.highscores['Intermediate'] = 'Anonymous 999'
        self.highscores['Expert'] = 'Anonymous 999'
        self.hslab_time.config(text='999 seconds\n999 seconds\n999 seconds')
        self.hslab_name.config(text='Anonymous\nAnonymous\nAnonymous')

    def f4_hs(self, _):
        self.view_high_scores()
        
    def view_high_scores(self):
        self.highscoresTL = tk.Toplevel(self)
        self.highscoresTL.title('Fastest Mine Sweepers')
        self.pack()
        self.hslab_level = tk.Label(self.highscoresTL, justify='left',
                                    text='Begginer:\nIntermediate:\nExpert:')
        self.hslab_time = tk.Label(self.highscoresTL, justify='left',
            text = ''.join((self.highscores['Beginner'].split()[1], ' seconds\n',
                            self.highscores['Intermediate'].split()[1], ' seconds\n',
                            self.highscores['Expert'].split()[1], ' seconds'
                            )))
        self.hslab_name = tk.Label(self.highscoresTL, justify='left',
            text = ''.join((self.highscores['Beginner'].split()[0], '\n',
                            self.highscores['Intermediate'].split()[0], '\n',
                            self.highscores['Expert'].split()[0]
                            )))

        self.hsbut_ok = tk.Button(self.highscoresTL, width = 5,
                                  text='Ok', command=self.highscoresTL.destroy)
        self.hsbut_reset = tk.Button(self.highscoresTL,
                                     text='Reset highscores',
                                     command=self.reset_highscores)

        self.hslab_level.grid(row=0, column=0, padx=5, pady=10)
        self.hslab_time.grid(row=0, column=1, padx=5, pady=10)
        self.hslab_name.grid(row=0, column=2, padx=5, pady=10)
        self.hsbut_ok.grid(row=1, column=2, padx=5, pady=10, sticky='w')
        self.hsbut_reset.grid(row=1, column=0, padx=5, pady=10, columnspan=2)

        
    def new_highscore(self):
        self.newhs = tk.Toplevel(self)
        self.newhs.title('New High Score!')
        self.pack()

        self.newhs_level = self.level #Prevents exploit
        text = ''.join(("Wow!  You just beat the fastest time on ",
                        self.levels[self.newhs_level],
                        "\nWhat is your name?"))
        
        self.newhs_name = tk.StringVar()
        self.newhs_label = tk.Label(self.newhs, text=text)
        self.newhs_entry = tk.Entry(self.newhs, width = 15,
                                    textvariable = self.newhs_name)
        self.newhs_ok = tk.Button(self.newhs, text='Ok', width=5,
                                  command=self.ok_newhs)

        self.newhs_label.grid(row=0, column=0, padx=5, pady=5)
        self.newhs_entry.grid(row=1, column=0, padx=5, pady=5)
        self.newhs_ok.grid(row=2, column=0, padx=5, pady=5)
        

    def ok_newhs(self):
        self.highscores[self.levels[self.newhs_level]] = ''.join((
            self.newhs_name.get(), ' ', str(self.time)))
        with open(self.rhsfile, 'w') as f:
            string = ''.join((toHex(self.highscores['Beginner']), '\n',
                              toHex(self.highscores['Intermediate']), '\n',
                              toHex(self.highscores['Expert'])))
            f.write(string)
        self.newhs.destroy()

        if tk.messagebox.askyesno("Good game", "Play again?"):
            self.restart()
        else:
            self.root.destroy()
            sys.exit(0)
        
    
                
                            

#convert string to hex
def toHex(s):
    from functools import reduce
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)

#convert hex repr to string
def toStr(s):
    import binascii
    return str(binascii.unhexlify(s), 'utf-8')


if __name__ == '__main__':
    myapp = Minesweeper()
    myapp.master.title('Minesweeper')
    myapp.mainloop() 
