"""
---------------------Tetris For Maya----------------------------------


Author: Mathieu BOUZARD
Date : 02-2018
Version : 1.5


---------------------------------------------------------------------
"""

import maya.cmds as cmds
from random import shuffle
from time import sleep
import math

# --------------CLEAN--------------


def clean_game():
    global score_tetris
    global level_tetris
    global total_lines
    global action
    # global hotkeyMapping
    global hold_tetrimino

    if cmds.ls('grilleTetrisGrp'):
        cmds.delete('grilleTetrisGrp')
    if cmds.ls('*TetriminoEnv'):
        cmds.delete('*TetriminoEnv')
    if cmds.ls('*Txgrp'):
        cmds.delete('*Txgrp')
    if cmds.ls('tetrisCam'):
        cmds.delete('tetrisCam')
    if cmds.ls('tetrimino*grp'):
        cmds.delete('tetrimino*grp')
    # if cmds.hotkeySet('tetrisMaya', q=1, exists=1):
    #     cmds.hotkeySet('tetrisMaya', edit=1, delete=1)

    score_tetris = 0.0
    level_tetris = 1
    total_lines = 0
    action = 0
    hotkeyMapping = ""
    hold_tetrimino = ""

# -----------------------------------------WORK-----------------------------------------

# global variable


score_tetris = 0.0
level_tetris = 1
total_lines = 0
action = 0
# hotkeyMapping = ""
lsHUD = []
lsHUDactivate = []
hold_tetrimino = ""

# --------------UI Process----------


# process Hud score
def score_tetris_p():
    global score_tetris
    return float(score_tetris)


# process Hud level
def level_tetris_p():
    global level_tetris
    return int(level_tetris)


# process Hud lines
def lines_tetris_p():
    global total_lines
    return int(total_lines)


def viewport_ui():
    # game environnement
    global lsHUD
    global lsHUDactivate

    cmds.group(name="grilleTetrisGrp", empty=1)
    for x in range(10):
        for y in range(20):
            name_cube = "GrilleTetris{0}{1}Env".format(x, y)
            cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, cuv=0, ch=0, n=name_cube)
            cmds.polyBevel3('{0}.e[0:11]'.format(name_cube), segments=1, ch=0, o=0.05, oaf=0, ws=1, at=30)
            cmds.move(x-4, y, -1, name_cube, absolute=1)
            cmds.parent(name_cube, 'grilleTetrisGrp')

    cmds.polyTorus(r=3.2, sr=0.3, tw=0, sx=4, sy=3, cuv=0, ch=0, n="futureTetriminoEnv")
    cmds.move(8.5, 15, -1, "futureTetriminoEnv", absolute=1)
    cmds.rotate('90deg', 0, '-45deg', "futureTetriminoEnv", a=1)

    cmds.polyTorus(r=3.2, sr=0.3, tw=0, sx=4, sy=3, cuv=0, ch=0, n="holdTetriminoEnv")
    cmds.move(-7.5, 15, -1, "holdTetriminoEnv", absolute=1)
    cmds.rotate('90deg', 0, '-45deg', "holdTetriminoEnv", a=1)

    # texte environnement
    ls_text = ["Next", "Hold"]
    for text in ls_text:
        grp_name = cmds.group(name = "{0}Txgrp".format(text), empty=1)
        # crv_tx = cmds.textCurves(f="Arial|wt:75|sz:32.2|sl:n|st:100", t=text)
        crv_tx = cmds.textCurves(t=text)
        for letter in text:
            letter_srf = cmds.planarSrf('Char_{0}_1'.format(letter), name="Char_{0}_1_tetris".format(letter),
                                        ch=0, tol=0.01, o=1, po=0)[0]
            cmds.parent(letter_srf, grp_name)
        cmds.delete(crv_tx)

    cmds.move(7.2, 18, 0, "NextTxgrp", absolute=1)
    cmds.move(-8.7, 18, 0, "HoldTxgrp", absolute=1)

    cmds.modelEditor('modelPanel4', e=1, hud=1, gr=0, ha=0, sdw=0)  # hud on - grid off - handles off
    # cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)  # ambiant occlusion
    # cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)  # anti-aliasing

    # camera
    tetris_cam = cmds.camera(position=[1.231, 9.496, 404], fl=300, ncp=10)
    cmds.rename(tetris_cam[0], "tetris_cam")
    cmds.lookThru("tetris_cam")
    ls_attr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    for attr in ls_attr:
        cmds.setAttr('tetris_cam.{0}'.format(attr), lock=True)

    # desactivation hud
    lsHUD = cmds.headsUpDisplay(q=1, listHeadsUpDisplays=1)
    lsHUDactivate = []
    for hud in lsHUD:
        if cmds.headsUpDisplay(hud, q=1, vis=1) is True:
            cmds.headsUpDisplay(hud, e=1, vis=0)
            lsHUDactivate.append(1)
        else:
            lsHUDactivate.append(0)

    # hud score
    cmds.headsUpDisplay('tetrisScoreHUD', section=0, block=11, blockSize="small", label="Score :",
                        labelFontSize="large", command="score_tetris_p",
                        dataFontSize="large", attachToRefresh=1)

    # hud level
    cmds.headsUpDisplay('tetrisLevelHUD', section=0, block=12, blockSize="small", label="Level :",
                        labelFontSize="large", command="level_tetris_p",
                        dataFontSize="large", attachToRefresh=1)

    # hud lines
    cmds.headsUpDisplay('tetrisLinesHUD', section=0, block=13, blockSize="small", label="Lines :",
                        labelFontSize="large", command="lines_tetris_p",
                        dataFontSize="large", attachToRefresh=1)


def restore_ui():
    # restore hotkey
    # global hotkeyMapping
    global lsHUD
    global lsHUDactivate

    # cmds.hotkeySet(hotkeyMapping, edit=1, current=1)
    # cmds.hotkeySet('tetrisMaya', edit=1, delete=1)

    # restore viewport
    cmds.modelEditor('modelPanel4', e=1, hud=1, gr=1, ha=1, sdw=0)
    # cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
    # cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)

    cmds.headsUpDisplay('tetrisScoreHUD', rem=1)
    cmds.headsUpDisplay('tetrisLevelHUD', rem=1)
    cmds.headsUpDisplay('tetrisLinesHUD', rem=1)

    # restore hud

    i = 0
    while i < len(lsHUD):
        if lsHUDactivate[i] == 1:
            cmds.headsUpDisplay(lsHUD[i], e=1, vis=1)
        i += 1


# --------------Game Process----------


# process tetrimino Maker
def tetrimino_maker(id_t, part_pos):
    part_ls = []
    i = 0
    while i < 4:
        pos = part_pos[i]
        name_part = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=[0, 1, 0], ch=0, cuv=0,
                                  n="tetrimino{1}{0}part1".format(id_t, part_pos[4]))
        cmds.polyBevel3('{0}.e[0:11]'.format(name_part[0]), segments=1, ch=0, o=0.1, oaf=0, ws=1,  at=30)
        cmds.polyColorPerVertex(rgb=(part_pos[5][0], part_pos[5][1], part_pos[5][2]), cdo=1, nun=1)
        cmds.move(pos[0], pos[1], 0, name_part, absolute=1)
        part_ls.append(name_part[0])
        i += 1
    grp_name = cmds.group(part_ls, name="tetrimino{1}{0}grp".format(id_t, part_pos[4]))
    cmds.xform(grp_name, piv=[0, 0, 0], ws=1)
    cmds.select(clear=1)
    return grp_name


# process move
def move_tetris(move_x_y, active_tetrimino, active_part, condition, channel):
    global action
    global matrix_pos
    limit = 0
    for part in active_part:
        pos_part = cmds.xform(part, ws=1, q=1, t=1)
        # teste si la place dans la direction du deplacement est occupe
        if (pos_part[channel] == condition[0] or
                matrix_pos[int(pos_part[1]) + condition[1]][int(pos_part[0] + condition[2])] == 1):
            limit = 1
            break
    if limit == 0:
        cmds.move(move_x_y[0], move_x_y[1], 0, active_tetrimino, relative=1)
    action = 0
    return limit


# rotation 2D math
def rotate(origin, point, angle):

    ox, oy = origin
    px, py = point

    qx = round(ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
    qy = round(oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))
    return [qx, qy]


# process rotate
def rotate_tetris(active_tetrimino, active_part):
    global action
    global matrix_pos
    origin_pos = cmds.xform(active_part[0], q=1, ws=1, t=1)
    offset = [0, 0]
    new_pos = []

    if origin_pos[0] <= -4:
        offset[0] += 1
    elif origin_pos[0] >= 5:
        offset[0] -= 1
    if origin_pos[1] >= 19:
        offset[1] -= 1
    elif origin_pos[1] <= 0:
        offset[1] += 1

    verif = [0, 0, 0, 0]

    pos_part = []
    for i in range(3):
        pos_part.append(cmds.xform(active_part[i + 1], q=1, ws=1, t=1))

    for i in range(3):
        new_pos = []
        for pos in pos_part:
            result_rot = rotate([origin_pos[0]+offset[0], origin_pos[1]+offset[1]],
                                [pos[0]+offset[0], pos[1]+offset[1]], math.radians(-90))
            new_pos.append(result_rot)
            side_l_r = result_rot[0] - (origin_pos[0] + offset[0])
            side_u_d = result_rot[1] - (origin_pos[1] + offset[1])
            if result_rot[0] < -4:
                offset[0] += 1
                verif[0] = 1
            elif result_rot[0] > 5:
                offset[0] -= 1
                verif[1] = 1
            if result_rot[1] < 0:
                offset[1] += 1
                verif[2] = 1
            elif result_rot[1] > 19:
                offset[1] -= 1
                verif[3] = 1

            if 5 >= result_rot[0] >= -4 and 19 >= result_rot[1] >= 0:
                if matrix_pos[int(result_rot[1])][int(result_rot[0]) + 4] == 1:
                    if side_l_r <= -1:  # left
                        offset[0] += 1
                        verif[0] = 1
                    elif side_l_r >= 1:  # right
                        offset[0] -= 1
                        verif[1] = 1
                    if side_u_d <= -1:  # down
                        offset[1] += 1
                        verif[2] = 1
                    elif side_u_d >= 1:  # up
                        offset[1] -= 1
                        verif[3] = 1

    if verif.count(1) <= 1:
        cmds.move(origin_pos[0] + offset[0], origin_pos[1] + offset[1], 0, active_tetrimino, ws=1, absolute=1)
        for i in range(3):
            cmds.move(new_pos[i][0], new_pos[i][1], 0, active_part[i + 1], ws=1, absolute=1)

    action = 0


# hold process
def move_hold_tetris(hold_tetrimino):
    if hold_tetrimino.find("tetriminoI") != -1:
        cmds.move(-7.9, 15, 0, hold_tetrimino, absolute=1)
    elif hold_tetrimino.find("tetriminoO") != -1:
        cmds.move(-7.85, 15.4, 0, hold_tetrimino, absolute=1)
    else:
        cmds.move(-7.5, 15.25, 0, hold_tetrimino, absolute=1)
    cmds.scale(.85, .85, .85, hold_tetrimino, a=1)


def hold_tetris(active_tetrimino, active_part, pos_part):
    global hold_tetrimino
    global action
    for i in range(4):
        part = active_part[i]
        cmds.move(pos_part[i][0], pos_part[i][1], 0, part, absolute=1, localSpace=1)

    if hold_tetrimino == "":
        hold_tetrimino = active_tetrimino
        move_hold_tetris(hold_tetrimino)
        active_tetrimino = ""

    else:
        # active vers hold
        temp = active_tetrimino
        move_hold_tetris(temp)
        active_tetrimino = hold_tetrimino
        hold_tetrimino = temp
        # hold vers active
        cmds.move(0, 19, 0, active_tetrimino, absolute=1)
        cmds.scale(1, 1, 1, active_tetrimino, a=1)

    action = 0
    return active_tetrimino


# ----------------------Game Process----------------------
def run_game():
    # -----------------Game Variables-----------------
    global action
    global matrix_pos
    global score_tetris
    global level_tetris
    global total_lines

    # Info construction Tetrimino (position, nom, couleur)
    tetrimino_t = [[0, 0, 0], [1, 0, 0], [-1, 0, 0], [0, -1, 0], "T", [0.23, 0.0, 0.27]]
    tetrimino_o = [[0, 0, 0], [0, -1, 0], [1, 0, 0], [1, -1, 0], "O", [.7, .65, .02]]
    tetrimino_l = [[0, 0, 0], [-1, -1, 0], [1, 0, 0], [-1, 0, 0], "L", [0.75, 0.25, 0]]
    tetrimino_j = [[0, 0, 0], [1, -1, 0], [1, 0, 0], [-1, 0, 0], "J", [0.02, 0.02, 0.65]]
    tetrimino_z = [[0, 0, 0], [0, -1, 0], [-1, 0, 0], [1, -1, 0], "Z", [.65, 0.02, 0.02]]
    tetrimino_s = [[0, 0, 0], [0, -1, 0], [1, 0, 0], [-1, -1, 0], "S", [0.02, .65, 0.02]]
    tetrimino_i = [[0, 0, 0], [-1, 0, 0], [1, 0, 0], [2, 0, 0], "I", [0, .5, 1]]

    ls_tetrimino = [tetrimino_t, tetrimino_o, tetrimino_l, tetrimino_j, tetrimino_z, tetrimino_s, tetrimino_i]
    ls_tetrimino_hold = [tetrimino_t, tetrimino_o, tetrimino_l, tetrimino_j, tetrimino_z, tetrimino_s, tetrimino_i]
    ls_tetrimino_name = ['tetrimino_t', 'tetrimino_o', 'tetrimino_l', 'tetrimino_j', 'tetrimino_z',
                         'tetrimino_s', 'tetrimino_i']

    # Matrice position
    nbr_cols = 10
    nbr_rows = 20
    matrix_pos = [[0] * nbr_cols for i in range(nbr_rows)]  # matrix_pos[row Y][col X] X 0 = index 4
    # Matrice name
    matrix_name = [[0] * nbr_cols for i in range(nbr_rows)]

    hold_used = 0

    # ----------------------Game----------------------

    time_step = 0.5
    game_over = 0
    next_level = 0
    increment = 0

    # initialisation de la file d attente des tetriminos
    queue_tetrimino = range(14)
    shuffle(ls_tetrimino)
    for j in range(7):
        queue_tetrimino[j + 7] = ls_tetrimino[j]

    # countdown
    for i in range(3):
        cmds.headsUpMessage('Start in {0}'.format(3 - i), time=1)
        sleep(1)

    cmds.refresh()

    while game_over != 1:
        # liste des 14 prochains tetriminos a apparaitre
        shuffle(ls_tetrimino)
        for j in range(7):
            queue_tetrimino[j] = queue_tetrimino[j + 7]
            queue_tetrimino[j + 7] = ls_tetrimino[j]

        # --------boucle tetrimino---------
        for j in range(7):
            active_tetrimino = tetrimino_maker(j + increment, queue_tetrimino[j])
            active_part = cmds.listRelatives(active_tetrimino, children=1)
            # pos_part=[]
            cmds.move(0, 19, 0, active_tetrimino, absolute=1)

            # tetrimino suivant
            future_tetrimino = tetrimino_maker(j + increment + 1, queue_tetrimino[j + 1])
            if future_tetrimino.find("tetrimino_i") != -1:
                cmds.move(8.125, 15, 0, future_tetrimino, absolute=1)
            elif future_tetrimino.find("tetrimino_o") != -1:
                cmds.move(8.125, 15.35, 0, future_tetrimino, absolute=1)
            else:
                cmds.move(8.5, 15.25, 0, future_tetrimino, absolute=1)
            cmds.scale(.85, .85, .85, future_tetrimino, a=1)

            # check si la place est deja occupe a la creation du tetrimino
            limit = 0
            for part in active_part:
                pos_part = cmds.xform(part, ws=1, q=1, t=1)
                if matrix_pos[int(pos_part[1])][int(pos_part[0] + 4)] == 1:
                    limit = 1
                    break
            if limit == 1:
                print "game over"
                game_over = 1
                break

            if j + increment >= 1:
                hold_used = 0
            i = 0
            while i < 20:

                for f in range(10):  # actualisation
                    pos_tetrimino = cmds.xform(active_tetrimino, q=1, t=1)
                    if action == 1:  # leftmove
                        move_tetris([-1, 0], active_tetrimino, active_part, [-4, 0, 3], 0)

                    elif action == 2:  # rightmove
                        move_tetris([1, 0], active_tetrimino, active_part, [5, 0, 5], 0)

                    elif action == 3:  # softdrop
                        move_tetris([0, -1], active_tetrimino, active_part, [0, -1, 4], 1)
                        score_tetris += 1

                    elif action == 4:  # hardrop
                        limit = 0
                        while limit != 1:
                            limit = move_tetris([0, -1], active_tetrimino, active_part, [0, -1, 4], 1)
                            score_tetris += 2
                        break
                    elif action == 5 and active_tetrimino.find("tetrimino_o") == -1:  # rotate right
                        rotate_tetris(active_tetrimino, active_part)

                    elif action == 6 and hold_used == 0:  # hold
                        active_tetrimino = hold_tetris(active_tetrimino, active_part,
                                                       ls_tetrimino_hold[ls_tetrimino_name.index(active_tetrimino[0:10])])
                        if active_tetrimino == "":
                            active_part = []
                            i = 0
                            break
                        else:
                            active_part = cmds.listRelatives(active_tetrimino, children=1)
                            i = 0
                        hold_used = 1

                    cmds.refresh()
                    sleep(time_step/10)
                if active_tetrimino == "":
                    break

                limit = 0
                for part in active_part:
                    pos_part = cmds.xform(part, ws=1, q=1, t=1)
                    # teste si le sol ou un tetrimino est deja en dessous
                    if pos_part[1] == 0 or matrix_pos[int(pos_part[1] - 1)][int(pos_part[0] + 4)] == 1:
                        limit = 1
                        break

                if limit == 1:
                    for part in active_part:
                        pos_part = cmds.xform(part, ws=1, q=1, t=1)
                        # actualise les matrices avec les nouvelles cases occupees
                        matrix_pos[int(pos_part[1])][int(pos_part[0] + 4)] = 1
                        matrix_name[int(pos_part[1])][int(pos_part[0] + 4)] = part
                    break

                elif limit == 0:
                    cmds.move(0, -1, 0, active_tetrimino, relative=1)  # fais descendre le tetrimino d une case

                i += 1

            # ----------check les cases-------
            index_r = 0
            row_score = 0

            while index_r < 20:
                row = matrix_pos[index_r]
                # check si la ligne est complete
                if row.count(1) == 10:
                    row_score += 1
                    for part in matrix_name[index_r]:
                        cmds.delete(part)  # delete la ligne complete

                    r = index_r + 1
                    dropped = 0
                    while r < 20:
                        # descend d une case la lignes superieur si non vide
                        if matrix_pos[r].count(1) != 0:
                            for part_drop in matrix_name[r]:
                                if part_drop != 0:
                                    cmds.move(0, -1, 0, part_drop, relative=1)

                            # actualisation des matrices
                            matrix_pos[r - 1] = [x for x in matrix_pos[r]]
                            matrix_name[r - 1] = [x for x in matrix_name[r]]
                            dropped = 1

                        else:
                            matrix_pos[r - 1] = [0 for x in matrix_pos[r]]
                            matrix_name[r - 1] = [0 for x in matrix_name[r]]
                        r += 1

                    # fait revenir le scan a l index precedant si des blocs ont ete descendus
                    index_r = index_r - dropped

                index_r += 1

            # ------augmentation du score---------
            if row_score == 1:
                score_tetris += 100
            elif row_score == 2:
                score_tetris += 300
            elif row_score == 3:
                score_tetris += 500
            elif row_score == 4:
                score_tetris += 800
            next_level += row_score
            total_lines += row_score

            # ------niveau suivant---------
            if next_level >= 10:
                next_level -= 10
                level_tetris += 1
                time_step = time_step * 0.75

            # --------------end check case------------------

            cmds.delete(future_tetrimino)
            # supprime les groupes vides
            ls_grp = cmds.ls('tetrimino*grp')
            for grp in ls_grp:
                if cmds.listRelatives(grp, children=1) is None:
                    cmds.delete(grp)

        # --------end boucle tetrimino---------
        increment += 7

    cmds.refresh()
    cmds.confirmDialog(title="Score", button="Ok",
                       message="Game Over\n\n Final Score: {0}\n Lines: "
                               "{1}\n Final Level: {2}".format(score_tetris, total_lines, level_tetris))


# -------------Launch process-------------
def launch_game_process():
    cmds.file(f=1, new=1)
    # cmds.setFocus('modelPanel4')
    clean_game()
    # hotkey_set()
    viewport_ui()
    run_game()
    restore_ui()