import time
from dragonfly import Function, Choice, MappingRule
from castervoice.lib import control, navigation
from castervoice.lib.actions import Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.additions import IntegerRefST
from castervoice.lib.merge.state.short import R
from castervoice.rules.ccr.standard import SymbolSpecs


# Command to kill the grid
def kill():
    control.nexus().comm.get_com("grids").kill()


# Perform an action based on the passed in action number
# action - optional mouse action after movement
def perform_mouse_action(action):
    if action == 1:
        Mouse("left").execute()
    if action == 2:
        Mouse("left:2").execute()
    elif action == 3:
        Mouse("right").execute()
        
def send_input(x, y, action):
    s = control.nexus().comm.get_com("grids")
    s.move_mouse(int(x), int(y))
    int_a = int(action)
    if int_a != 0:
        s.kill()
        navigation.wait_for_grid_exit()
    if int_a == 1:
        Mouse("left").execute()
    if int_a == 2:
        Mouse("left:2").execute()
    if int_a == 3:
        Mouse("left:3").execute()
    elif int_a == 4:
        Mouse("right").execute()


# Command to move the mouse
# n - square to move to
# s - optional inner square to move to
# action - optional mouse action after movement
def move_mouse(n, s, action):
    sudoku = control.nexus().comm.get_com("grids")
    sudoku.move_mouse(int(n), int(s))
    sudoku.kill()
    navigation.wait_for_grid_exit()
    time.sleep(0.1)
    perform_mouse_action(int(action))


# Command to drag the mouse from the current position
# n0 - optional square to drag from
# s0 - optional inner square to drag from
# n  - square to drag to
# s  - optional inner square to drag to
# action - optional mouse action after movement
def drag_mouse(n0, s0, n, s, action):
    sudoku = control.nexus().comm.get_com("grids")
    x, y = sudoku.get_mouse_pos(int(n), int(s))
    # If dragging from a different location, move there first
    if int(n0) > 0:
        sudoku.move_mouse(int(n0), int(s0))
    sudoku.kill()
    navigation.wait_for_grid_exit()
    time.sleep(0.1)
    # Hold down click, move to drag destination, and release click
    Mouse("left:down/10").execute()
    Mouse("[{}, {}]".format(x, y)).execute()
    time.sleep(0.1)
    Mouse("left:up/30").execute()
    perform_mouse_action(int(action))

def store_first_point():
    global x1, y1
    x1, y1 = get_cursor_position()

def select_text():
    global x1, y1, x2, y2
    x2, y2 = get_cursor_position()
    s = control.nexus().comm.get_com("grids")
    s.kill()
    navigation.wait_for_grid_exit()
    drag_from_to(x1, y1, x2, y2)

'''
Rules for sudoku grid. We can either move the mouse or drag it.
The number n is one of the numbered squares.
The grid portion is a number from 1-9 referencing an inner unnumbered square.
'''


class SudokuGridRule(MappingRule):
    pronunciation = "sudoku grid"

    mapping = {
        "<n> [grid <s>] [<action>]":
            R(Function(move_mouse)),
        "[<n0>] [grid <s0>] drag <n> [grid <s>] [<action>]":
            R(Function(drag_mouse)),
        "squat {weight=2}":
            R(Function(store_first_point)),
        "bench {weight=2}":
            R(Function(select_text)),
        SymbolSpecs.CANCEL:
            R(Function(kill)),
    }
    extras = [
        IntegerRefST("n", -1, 1500),
        IntegerRefST("n0", -1, 1500),
        IntegerRefST("s", 0, 10),
        IntegerRefST("s0", 0, 10),
        Choice("action", {
            "move": 0,
            "kick": 1,
            "kick (double | 2)": 2,
            "kick 3": 3,
            "psychic": 4,
        }),
    ]
    defaults = {
        "n": 0,
        "n0": 0,
        "s": 0,
        "s0": 0,
        "action": 0,
    }


def get_rule():
    Details = RuleDetails(name="Sudoku Grid", title="sudokugrid")
    return SudokuGridRule, Details
