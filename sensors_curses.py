# PROG: Displays real-time information gathered from Falconia.
#       Updated to use the curses library rather than termcolor (a dependency)
#       Shouldn't display flashes when used remotely...
# AUTH: inv3rsion
# DATE: 1/28/2015

from __future__ import print_function;
import sys;
import time;
import random;
import serial;
import curses;
import threading;

TERM_LENGTH = 100;
TERM_HEIGHT = 29;
SCREEN = [[" " for j in range(0, TERM_LENGTH)] for i in range(0, TERM_HEIGHT)];
GRAPH_ULIMIT = 100;
GRAPH_LLIMIT = 0;
stdscr = curses.initscr();
stdscr.nodelay(1);
curses.start_color();
curses.use_default_colors();
curses.init_pair(1, curses.COLOR_RED, -1);
curses.init_pair(2, curses.COLOR_GREEN, -1);
curses.init_pair(3, curses.COLOR_CYAN, -1);
curses.init_pair(4, curses.COLOR_MAGENTA, -1);
curses.init_pair(5, curses.COLOR_YELLOW, -1);
curses.init_pair(6, curses.COLOR_BLUE, -1);

COLORS = {"red"    :  curses.color_pair(1),
          "green"  :  curses.color_pair(2),
          "cyan"   :  curses.color_pair(3),
          "magenta":  curses.color_pair(4),
          "yellow" :  curses.color_pair(5),
          "blue"   :  curses.color_pair(6),
          "bold"   :  curses.A_BOLD,
          "blink"  :  curses.A_BLINK,
          "underl" :  curses.A_UNDERLINE,
          "reverse":  curses.A_REVERSE,
          "stand"  :  curses.A_STANDOUT,
          "dim"    :  curses.A_DIM
         }

#TODO: ENABLE THIS
SENSORS = serial.Serial('/dev/tty.serial1', 38400);

def clear_screen():
    for i in range(0, TERM_HEIGHT):
        print();

def add_vertical_line(column):
    for i in range(0, TERM_HEIGHT):
        if SCREEN[i][column] == "-":
            SCREEN[i][column] = "+";
        else:
            SCREEN[i][column] = "|";

def add_str(string, row, col, color="white", startcolor_index=0):
    for i, l in enumerate(string):
        if i >= startcolor_index:
            SCREEN[row][col+i] = (l, color);
        else:
            SCREEN[row][col+i] = l;

def add_r_str(string, row, col, color="white"):
    if len(string) > col:
        return;

    for i, l in enumerate(string[::-1]):
        SCREEN[row][col-i] = (l, color);

def add_m_str(string, row, color="white"):
    if len(string) >= 100:
        return;

    start = TERM_LENGTH/2 - len(string)/2;
    for i, l in enumerate(string):
        SCREEN[row][start+i] = (l, color);

def add_horizontal_line(row):
    for i in range(0, TERM_LENGTH):
        if SCREEN[row][i] == "|":
            SCREEN[row][i] = "+";
        else:
            SCREEN[row][i] = "-";

def clear_row(row, start=0, end=TERM_LENGTH):
    # doesn't clear the end
    for i in range(start, end):
        SCREEN[row][i] = " ";

def clear_col(col, start=0, end=TERM_HEIGHT):
    for i in range(start, end):
        SCREEN[i][col] = " ";

def draw():
    for lnum, line in enumerate(SCREEN):
        for cnum, c in enumerate(line):
            if isinstance(c, tuple):
                if c[1] != "white":
#                    print(colored(c[0], c[1]), end="");
#                    stdscr.insstr(lnum, cnum, c[0], get_curses_color(c[1]));
                    stdscr.insstr(lnum, cnum, c[0], COLORS[c[1]]);
                else:
#                    print(c[0], end="");
                    stdscr.insstr(lnum, cnum, c[0]);
            else:
#                print(c, end="");
                stdscr.insstr(lnum, cnum, c);
#        print();
    stdscr.refresh();

def limit(val):
    if val < GRAPH_LLIMIT:
        return GRAPH_LLIMIT;
    return GRAPH_ULIMIT;

def in_range(val):
    return GRAPH_LLIMIT <= val <= GRAPH_ULIMIT;

def add_graph(data, x_axis):
    clear_row(22);
    # start at 7
    for i, t in enumerate(x_axis):
        if t % 5 == 0:
            t = str(t%100);
            add_str(t, 22, 7+i, "underl" if t == "0" else "white");
            add_str("+", 21, 7+i);
        else:
            add_str("-", 21, 7+i);

    for r in range(1, 21):
        clear_row(r, 7);

    for dvalues in data:
        if not dvalues[3]:
            continue;
        for i, dval in enumerate(dvalues[0][-90:]):
            if not in_range(dval):
                add_str("X", 21-int(round(limit(dval)/5)), 7+i, dvalues[2]);
            else:
                add_str(dvalues[1], 21-int(round(dval/5)), 7+i, dvalues[2]);

def get_user_input():
    c = stdscr.getch();
    if c == ord("h"):
        data[0][3] = not data[0][3];
    if c == ord("t"):
        data[1][3] = not data[1][3];
    if c == ord("r"):
        data[2][3] = not data[2][3];
    if c == ord("g"):
        data[3][3] = not data[3][3];
    if c == ord("b"):
        data[4][3] = not data[4][3];
    if c == ord("q"):
        clear_screen();
        quit();

def get_sensors():
    #TODO: CHANGE THIS TO ACTUALLY READ THE SENSORS
    r = -1;
    g = -1;
    b = -1;
    h = -1;
    t = -1;
    datain = SENSORS.readlines().strip();
    data = datain.split(",");
    r = data[0];
    g = data[1];
    b = data[2];
    return r, g, b, h, t;
#    return random.randint(50, 100), random.randint(100, 150), random.randint(150, 255), random.randint(20, 50), random.randint(50, 100); 

def is_humid(humid):
    return False;

def is_hot(temp):
    return False;

def is_yellow(red, green, blue):
    RU = 190;
    RL = 30;
    GU = 90;
    GL = 20;
    BU = 90;
    BL = 20;
    return (RL <= red <= RU) and \
           (GL <= green <= GU) and \
           (BL <= blue <= BU);

def is_hot_spring(humid, temp, red, green, blue):
    return is_humid(humid) and is_hot(temp) and is_yellow(red, green, blue);

clear_screen();
add_horizontal_line(21);
add_vertical_line(5);

clear_row(0);
add_m_str("Falconia Sensors (Zoya Bharmal, Katie Cho, Matthew Feng, June Xu)", 0);
for i in range(22, TERM_HEIGHT):
    clear_row(i);

for i in range(100, 0, -5):
    add_r_str(str(i), 21-i/5, 4);

T_START = 0;
x_axis = range(0, T_START); 
t = 0;
data = [[[], "h", "magenta", True], # humidity
        [[], "t", "yellow", True],  # temperature 
        [[], "r", "red", False],     # red
        [[], "g", "green", False],   # green
        [[], "b", "cyan", False]];   # blue

#TODO: ENABLE THIS
#output = open("/home/ubuntu/Desktop/mission_data.txt", "w");

while True:
    # get sensor data from /dev/ttyACM0, try to parse and read
    rdata, gdata, bdata, hdata, tdata = get_sensors();
    data[0][0].append(hdata);
    data[1][0].append(tdata);
    data[2][0].append(rdata * 100.0 / 255.0);
    data[3][0].append(gdata * 100.0 / 255.0);
    data[4][0].append(bdata * 100.0 / 255.0);

    x_axis.append(T_START + t);

    add_graph(data, x_axis[-90:]);
    add_r_str(str((t+T_START)/100), 22, 3);

    for i in range(23, TERM_HEIGHT):
        clear_row(i);

    add_str("Current Readings:", 23, 0);
    add_str("(R)ed:         " + str(rdata), 24, 5, "red", 13);
    add_str("(G)reen:       " + str(gdata), 25, 5, "green", 13);
    add_str("(B)lue:        " + str(bdata), 26, 5, "cyan", 13);
    add_str("(H)umidity:    " + str(hdata), 27, 5, "magenta", 13);
    add_str("(T)emperature: " + str(tdata), 28, 5, "yellow", 13);


    isye = is_yellow(rdata, gdata, bdata);
    isho = is_hot(tdata);
    ishu = is_humid(hdata);

    add_str("Yellow? " + str(isye), 25, 40, "green" if isye else "red", 7);
    add_str("Hot?    " + str(isho), 26, 40, "green" if isho else "red", 7);
    add_str("Humid?  " + str(ishu), 27, 40, "green" if ishu else "red", 7);

    add_r_str("Running Time: %ss" % str(t+T_START), 28, 98);

#    TODO: ENABLED THESE
#    write to output: time, r, g, b, isyellow (0/1), h, t
#    output.write("%d\t%s\t%s\t%s\t%s\t%s\t%d\n" % (str(T_START+t), str(rdata), str(gdata), str(bdata), (1 if isye else 0), str(hdata), str(tdata)));
#    output.flush();

    get_user_input();
    draw();
    time.sleep(1);
    t += 1;
