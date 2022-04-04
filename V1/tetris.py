# ---------------------Tetris For Maya----------------------------------
#
# Version : 1.0
#
# Warnings:
#     Only works on Maya 2016 or lower
#
#
# Copyright (c) 2016 Mathieu Bouzard.
#
# This file is part of Tetris For Maya
# (see https://gitlab.com/mathbou/TetrisMaya).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import maya.cmds as cmds
from random import shuffle
from time import sleep
import maya.mel as mel
import math


# --------------CLEAN--------------

def cleanGame():
    global scoreTetris
    global levelTetris
    global totalLines
    global action
    global hotkeyMapping
    global holdTetrimino
    if (cmds.ls('grilleTetrisGrp')):
        cmds.delete('grilleTetrisGrp')
    if (cmds.ls('*TetriminoEnv')):
        cmds.delete('*TetriminoEnv')
    if (cmds.ls('*Txgrp')):
        cmds.delete('*Txgrp')
    if (cmds.ls('tetrisCam')):
        cmds.delete('tetrisCam')
    if (cmds.ls('tetrimino*grp')):
        cmds.delete('tetrimino*grp')
    if (cmds.hotkeySet('tetrisMaya', q=1, exists=1)):
        cmds.hotkeySet('tetrisMaya', edit=1, delete=1)
    scoreTetris = 0.0
    levelTetris = 1
    totalLines = 0
    action = 0
    hotkeyMapping = ""
    holdTetrimino = ""


# -----------------------------------------WORK-----------------------------------------

# global variable
scoreTetris = 0.0
levelTetris = 1
totalLines = 0
action = 0
hotkeyMapping = ""
lsHUD = []
lsHUDactivate = []
holdTetrimino = ""


# --------------UI Process----------

# process Hud score
def scoreTetrisP():
    global scoreTetris
    return float(scoreTetris)


# process Hud level
def levelTetrisP():
    global levelTetris
    return int(levelTetris)


# process Hud lines
def linesTetrisP():
    global totalLines
    return int(totalLines)


def viewportUI():
    # game environnement
    global lsHUD
    global lsHUDactivate

    cmds.group(name="grilleTetrisGrp", empty=1)
    for x in range(10):
        for y in range(20):
            nameCube = "GrilleTetris{0}{1}Env".format(x, y)
            cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, cuv=0, ch=0, n=nameCube)
            cmds.polyBevel3('{0}.e[0:11]'.format(nameCube), segments=1, ch=0, o=0.05, oaf=0, ws=1, at=30)
            cmds.move(x - 4, y, -1, nameCube, absolute=1)
            cmds.parent(nameCube, 'grilleTetrisGrp')

    cmds.polyTorus(r=3.2, sr=0.3, tw=0, sx=4, sy=3, cuv=0, ch=0, n="futureTetriminoEnv")
    cmds.move(8.5, 15, -1, "futureTetriminoEnv", absolute=1)
    cmds.rotate('90deg', 0, '-45deg', "futureTetriminoEnv", a=1)

    cmds.polyTorus(r=3.2, sr=0.3, tw=0, sx=4, sy=3, cuv=0, ch=0, n="holdTetriminoEnv")
    cmds.move(-7.5, 15, -1, "holdTetriminoEnv", absolute=1)
    cmds.rotate('90deg', 0, '-45deg', "holdTetriminoEnv", a=1)

    # texte environnement
    lsText = ["Next", "Hold"]
    for text in lsText:
        grpName = cmds.group(name="{0}Txgrp".format(text), empty=1)
        crvTx = cmds.textCurves(f="Arial|wt:75|sz:32|sl:n|st:100", t=text)
        for letter in text:
            cmds.planarSrf('Char_{0}_1'.format(letter), name="Char_{0}_1_tetris".format(letter), ch=0, tol=0.01, o=1,
                           po=0)[0]
            cmds.parent("Char_{0}_1_tetris".format(letter), "{0}Txgrp".format(text))
        cmds.delete(crvTx)

    cmds.move(7.2, 18, 0, "NextTxgrp", absolute=1)
    cmds.move(-8.7, 18, 0, "HoldTxgrp", absolute=1)

    cmds.modelEditor('modelPanel4', e=1, hud=1, gr=0, ha=0, sdw=0)  # hud on - grid off - handles off
    cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)  # ambiant occlusion
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)  # anti-aliasing

    # camera
    tetrisCam = cmds.camera(position=[1.231, 9.496, 404], fl=300, ncp=10)
    cmds.rename(tetrisCam[0], "tetrisCam")
    cmds.lookThru("tetrisCam")
    lsAttr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    for attr in lsAttr:
        cmds.setAttr('tetrisCam.{0}'.format(attr), lock=True)

    # desactivation hud
    lsHUD = cmds.headsUpDisplay(q=1, listHeadsUpDisplays=1)
    lsHUDactivate = []
    for hud in lsHUD:
        if (cmds.headsUpDisplay(hud, q=1, vis=1) == True):
            cmds.headsUpDisplay(hud, e=1, vis=0)
            lsHUDactivate.append(1)
        else:
            lsHUDactivate.append(0)

    # hud score
    cmds.headsUpDisplay('tetrisScoreHUD', section=0, block=11, blockSize="small", label="Score :",
                        labelFontSize="large", command=scoreTetrisP, dfs="large", atr=1)

    # hud level
    cmds.headsUpDisplay('tetrisLevelHUD', section=0, block=12, blockSize="small", label="Level :",
                        labelFontSize="large", command=levelTetrisP, dfs="large", atr=1)

    # hud lines
    cmds.headsUpDisplay('tetrisLinesHUD', section=0, block=13, blockSize="small", label="Lines :",
                        labelFontSize="large", command=linesTetrisP, dfs="large", atr=1)


def restoreUI():
    # restore hotkey
    global hotkeyMapping
    global lsHUD
    global lsHUDactivate

    cmds.hotkeySet(hotkeyMapping, edit=1, current=1)
    cmds.hotkeySet('tetrisMaya', edit=1, delete=1)

    # restore viewport
    cmds.modelEditor('modelPanel4', e=1, hud=1, gr=1, ha=1, sdw=0)
    cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)

    cmds.headsUpDisplay('tetrisScoreHUD', rem=1)
    cmds.headsUpDisplay('tetrisLevelHUD', rem=1)
    cmds.headsUpDisplay('tetrisLinesHUD', rem=1)

    # restore hud

    i = 0
    while i < len(lsHUD):
        if (lsHUDactivate[i] == 1):
            cmds.headsUpDisplay(lsHUD[i], e=1, vis=1)
        i += 1


# -----------------Hotkey Process-----------------
def hotkeySet():
    global hotkeyMapping
    hotkeyMapping = cmds.hotkeySet(q=1, current=1)
    cmds.hotkeySet('tetrisMaya', current=1)
    global action

    # left move
    mel.eval('''
	global proc leftMove()
	{
		python("action = 1");
	}''')

    # right move
    mel.eval('''
	global proc rightMove()
	{
		python("action = 2");
	}''')

    # soft drop
    mel.eval('''
	global proc softDrop()
	{
	python("action = 3");
	}''')

    # hard drop
    mel.eval('''
	global proc hardDrop()
	{
	python("action = 4");
	}''')

    # rotate right
    mel.eval('''
	global proc rotateRight()
	{
	python("action = 5");
	}''')

    # hold tetrimino
    mel.eval('''
	global proc holdT()
	{
	python("action = 6");
	}''')

    cmds.nameCommand('leftMoveKey', stp='mel', ann='Left Move', c='leftMove()')
    cmds.nameCommand('rightMoveKey', stp='mel', ann='Right Move', c='rightMove()')
    cmds.nameCommand('SdropKey', stp='mel', ann='Soft Drop', c='softDrop()')
    cmds.nameCommand('HdropKey', stp='mel', ann='Hard Drop', c='hardDrop()')
    cmds.nameCommand('rRightKey', stp='mel', ann='Rotate Right', c='rotateRight()')
    cmds.nameCommand('holdKey', stp='mel', ann='Hold Tetrimino', c='holdT()')

    lsHotkey = ["leftMoveKey", "rightMoveKey", "SdropKey", "HdropKey", "rRightKey", 'holdKey']
    lsTf = ['tfLmoveUI', 'tfRmoveUI', 'tfSdropUI', 'tfHdropUI', 'tfRotateUI', 'tfHoldUI']
    lsValidHotkey = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                     'u', 'v', 'w', 'x', 'y', 'z', 'Up', 'Down', 'Right', 'Left', 'Home', 'End', 'Page_Up', 'Page_Down',
                     'Insert', 'Return', 'Space']
    lsDefaultHotkey = ['Left', 'Right', 'Down', 'Space', 'Up', 'c']
    for i in range(6):
        tfKey = cmds.textField(lsTf[i], q=1, text=1)
        if (tfKey in lsValidHotkey):
            cmds.hotkey(k=tfKey, name=lsHotkey[i])
        else:
            cmds.hotkey(k=lsDefaultHotkey[i], name=lsHotkey[i])


# --------------GUI Process----------

def helpHotkey():
    messageTx = """The valid keywords are:
a to z
Up, Down, Right, Left,
Home, End, Page_Up, Page_Down, Insert
Return, Space

A wrong keyword will be replaced by the default keyword
"""
    cmds.confirmDialog(button="Ok", message=messageTx, icon="information")


# --------------Game Process----------

# process tetrimino Maker
def tetriminoMaker(idT, partPos):
    partLs = []
    i = 0
    while i < 4:
        pos = partPos[i]
        namePart = cmds.polyCube(w=1, h=1, d=1, sx=1, sy=1, sz=1, ax=[0, 1, 0], ch=0, cuv=0,
                                 n="tetrimino{1}{0}part1".format(idT, partPos[4]))
        cmds.polyBevel3('{0}.e[0:11]'.format(namePart[0]), segments=1, ch=0, o=0.1, oaf=0, ws=1, at=30)
        cmds.polyColorPerVertex(rgb=(partPos[5][0], partPos[5][1], partPos[5][2]), cdo=1, nun=1)
        cmds.move(pos[0], pos[1], 0, namePart, absolute=1)
        partLs.append(namePart[0])
        i += 1
    grpName = cmds.group(partLs, name="tetrimino{1}{0}grp".format(idT, partPos[4]))
    cmds.xform(grpName, piv=[0, 0, 0], ws=1)
    cmds.select(clear=1)
    return grpName


# process move
def moveTetris(moveXY, activeTetrimino, activePart, condition, channel):
    global action
    global matrixPos
    limit = 0
    for part in activePart:
        posPart = cmds.xform(part, ws=1, q=1, t=1)
        if (posPart[channel] == condition[0] or matrixPos[int(posPart[1]) + condition[1]][
            int(posPart[0] + condition[2])] == 1):  # teste si la place dans la directoin du deplacement est occupe
            limit = 1
            break
    if (limit == 0):
        cmds.move(moveXY[0], moveXY[1], 0, activeTetrimino, relative=1)
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
def rotateTetris(activeTetrimino, activePart):
    global action
    global matrixPos
    originPos = cmds.xform(activePart[0], q=1, ws=1, t=1)
    offset = [0, 0]
    newPos = []

    if (originPos[0] <= -4):
        offset[0] += 1
    elif (originPos[0] >= 5):
        offset[0] -= 1
    if (originPos[1] >= 19):
        offset[1] -= 1
    elif (originPos[1] <= 0):
        offset[1] += 1

    verif = [0, 0, 0, 0]

    posPart = []
    for i in range(3):
        posPart.append(cmds.xform(activePart[i + 1], q=1, ws=1, t=1))

    for i in range(3):
        newPos = []
        for pos in posPart:
            resultRot = rotate([originPos[0] + offset[0], originPos[1] + offset[1]],
                               [pos[0] + offset[0], pos[1] + offset[1]], math.radians(-90))
            newPos.append(resultRot)
            sideLR = resultRot[0] - (originPos[0] + offset[0])
            sideUD = resultRot[1] - (originPos[1] + offset[1])
            if (resultRot[0] < -4):
                offset[0] += 1
                verif[0] = 1
            elif (resultRot[0] > 5):
                offset[0] -= 1
                verif[1] = 1
            if (resultRot[1] < 0):
                offset[1] += 1
                verif[2] = 1
            elif (resultRot[1] > 19):
                offset[1] -= 1
                verif[3] = 1

            if (resultRot[0] >= -4 and resultRot[0] <= 5 and resultRot[1] >= 0 and resultRot[1] <= 19):
                if (matrixPos[int(resultRot[1])][int(resultRot[0]) + 4] == 1):
                    if (sideLR <= -1):  # left
                        offset[0] += 1
                        verif[0] = 1
                    elif (sideLR >= 1):  # right
                        offset[0] -= 1
                        verif[1] = 1
                    if (sideUD <= -1):  # down
                        offset[1] += 1
                        verif[2] = 1
                    elif (sideUD >= 1):  # up
                        offset[1] -= 1
                        verif[3] = 1

    if (verif.count(1) <= 1):
        cmds.move(originPos[0] + offset[0], originPos[1] + offset[1], 0, activeTetrimino, ws=1, absolute=1)
        for i in range(3):
            cmds.move(newPos[i][0], newPos[i][1], 0, activePart[i + 1], ws=1, absolute=1)

    action = 0


# hold process
def moveHoldTetris(holdTetrimino):
    if (holdTetrimino.find("tetriminoI") != -1):
        cmds.move(-7.9, 15, 0, holdTetrimino, absolute=1)
    elif (holdTetrimino.find("tetriminoO") != -1):
        cmds.move(-7.85, 15.4, 0, holdTetrimino, absolute=1)
    else:
        cmds.move(-7.5, 15.25, 0, holdTetrimino, absolute=1)
    cmds.scale(.85, .85, .85, holdTetrimino, a=1)


def holdTetris(activeTetrimino, activePart, posPart):
    global holdTetrimino
    global action
    for i in range(4):
        part = activePart[i]
        cmds.move(posPart[i][0], posPart[i][1], 0, part, absolute=1, localSpace=1)

    if (holdTetrimino == ""):
        holdTetrimino = activeTetrimino
        moveHoldTetris(holdTetrimino)
        activeTetrimino = ""

    else:
        # active vers hold
        temp = activeTetrimino
        moveHoldTetris(temp)
        activeTetrimino = holdTetrimino
        holdTetrimino = temp
        # hold vers active
        cmds.move(0, 19, 0, activeTetrimino, absolute=1)
        cmds.scale(1, 1, 1, activeTetrimino, a=1)

    action = 0
    return activeTetrimino


# ----------------------Game Process----------------------
def runGame():
    # -----------------Game Variables-----------------
    global action
    global matrixPos
    global scoreTetris
    global levelTetris
    global totalLines

    # Info construction Tetrimino (position, nom, couleur)
    tetriminoT = [[0, 0, 0], [1, 0, 0], [-1, 0, 0], [0, -1, 0], "T", [0.23, 0.0, 0.27]]
    tetriminoO = [[0, 0, 0], [0, -1, 0], [1, 0, 0], [1, -1, 0], "O", [.7, .65, .02]]
    tetriminoL = [[0, 0, 0], [-1, -1, 0], [1, 0, 0], [-1, 0, 0], "L", [0.75, 0.25, 0]]
    tetriminoJ = [[0, 0, 0], [1, -1, 0], [1, 0, 0], [-1, 0, 0], "J", [0.02, 0.02, 0.65]]
    tetriminoZ = [[0, 0, 0], [0, -1, 0], [-1, 0, 0], [1, -1, 0], "Z", [.65, 0.02, 0.02]]
    tetriminoS = [[0, 0, 0], [0, -1, 0], [1, 0, 0], [-1, -1, 0], "S", [0.02, .65, 0.02]]
    tetriminoI = [[0, 0, 0], [-1, 0, 0], [1, 0, 0], [2, 0, 0], "I", [0, .5, 1]]

    lsTetrimino = [tetriminoT, tetriminoO, tetriminoL, tetriminoJ, tetriminoZ, tetriminoS, tetriminoI]
    lsTetriminoHold = [tetriminoT, tetriminoO, tetriminoL, tetriminoJ, tetriminoZ, tetriminoS, tetriminoI]
    lsTetriminoName = ['tetriminoT', 'tetriminoO', 'tetriminoL', 'tetriminoJ', 'tetriminoZ', 'tetriminoS', 'tetriminoI']

    # Matrice position
    nbrCols = 10
    nbrRows = 20
    matrixPos = [[0] * nbrCols for i in range(nbrRows)]  # matrixPos[row Y][col X] X 0 = index 4

    # Matrice name
    matrixName = [[0] * nbrCols for i in range(nbrRows)]

    holdUsed = 0

    # ----------------------Game----------------------

    timeStep = 0.5
    gameOver = 0
    nextLevel = 0
    increment = 0

    # initialisation de la file d attente des tetriminos
    queueTetrimino = [None]*14
    shuffle(lsTetrimino)
    for j in range(7):
        queueTetrimino[j + 7] = lsTetrimino[j]

    # countdown
    for i in range(3):
        cmds.headsUpMessage('Start in {0}'.format(3 - i), time=1)
        sleep(1)

    cmds.refresh()

    while gameOver != 1:
        # liste des 14 prochains tetriminos a apparaitre
        shuffle(lsTetrimino)
        for j in range(7):
            queueTetrimino[j] = queueTetrimino[j + 7]
            queueTetrimino[j + 7] = lsTetrimino[j]

        # --------boucle tetrimino---------
        for j in range(7):
            activeTetrimino = tetriminoMaker(j + increment, queueTetrimino[j])
            activePart = cmds.listRelatives(activeTetrimino, children=1)
            posPart = []
            cmds.move(0, 19, 0, activeTetrimino, absolute=1)

            # tetrimino suivant
            futureTetrimino = tetriminoMaker(j + increment + 1, queueTetrimino[j + 1])
            if (futureTetrimino.find("tetriminoI") != -1):
                cmds.move(8.125, 15, 0, futureTetrimino, absolute=1)
            elif (futureTetrimino.find("tetriminoO") != -1):
                cmds.move(8.125, 15.35, 0, futureTetrimino, absolute=1)
            else:
                cmds.move(8.5, 15.25, 0, futureTetrimino, absolute=1)
            cmds.scale(.85, .85, .85, futureTetrimino, a=1)

            # check si la place est deja occupe a la creation du tetrimino
            limit = 0
            for part in activePart:
                posPart = cmds.xform(part, ws=1, q=1, t=1)
                if (matrixPos[int(posPart[1])][int(posPart[0] + 4)] == 1):
                    limit = 1
                    break
            if (limit == 1):
                print
                "game over"
                gameOver = 1
                break

            if (j + increment >= 1):
                holdUsed = 0
            i = 0
            while i < 20:

                for f in range(10):  # actualisation
                    posTetrimino = cmds.xform(activeTetrimino, q=1, t=1)
                    if (action == 1):  # leftmove
                        moveTetris([-1, 0], activeTetrimino, activePart, [-4, 0, 3], 0)

                    elif (action == 2):  # rightmove
                        moveTetris([1, 0], activeTetrimino, activePart, [5, 0, 5], 0)

                    elif (action == 3):  # softdrop
                        moveTetris([0, -1], activeTetrimino, activePart, [0, -1, 4], 1)
                        scoreTetris += 1

                    elif (action == 4):  # hardrop
                        limit = 0
                        while (limit != 1):
                            limit = moveTetris([0, -1], activeTetrimino, activePart, [0, -1, 4], 1)
                            scoreTetris += 2
                        break
                    elif (action == 5 and activeTetrimino.find("tetriminoO") == -1):  # rotate right
                        rotateTetris(activeTetrimino, activePart)

                    elif (action == 6 and holdUsed == 0):  # hold
                        activeTetrimino = holdTetris(activeTetrimino, activePart,
                                                     lsTetriminoHold[lsTetriminoName.index(activeTetrimino[0:10])])
                        if (activeTetrimino == ""):
                            activePart = []
                            i = 0
                            break
                        else:
                            activePart = cmds.listRelatives(activeTetrimino, children=1)
                            i = 0
                        holdUsed = 1

                    cmds.refresh()
                    sleep(timeStep / 10)
                if (activeTetrimino == ""):
                    break

                limit = 0
                for part in activePart:
                    posPart = cmds.xform(part, ws=1, q=1, t=1)
                    if (posPart[1] == 0 or matrixPos[int(posPart[1] - 1)][
                        int(posPart[0] + 4)] == 1):  # teste si le sol ou un tetrimino est deja en dessous
                        limit = 1
                        break

                if (limit == 1):
                    for part in activePart:
                        posPart = cmds.xform(part, ws=1, q=1, t=1)
                        matrixPos[int(posPart[1])][
                            int(posPart[0] + 4)] = 1  # actualise les matrices avec les nouvelles cases occupees
                        matrixName[int(posPart[1])][int(posPart[0] + 4)] = part
                    break

                elif (limit == 0):
                    cmds.move(0, -1, 0, activeTetrimino, relative=1)  # fais descendre le tetrimino d une case

                i += 1

            # ----------check les cases-------
            indexR = 0
            rowScore = 0

            while indexR < 20:
                row = matrixPos[indexR]
                # check si la ligne est complete
                if (row.count(1) == 10):
                    rowScore += 1
                    for part in matrixName[indexR]:
                        cmds.delete(part)  # delete la ligne complete

                    r = indexR + 1
                    dropped = 0
                    while r < 20:
                        # descend d une case la lignes superieur si non vide
                        if (matrixPos[r].count(1) != 0):
                            for partDrop in matrixName[r]:
                                if (partDrop != 0):
                                    cmds.move(0, -1, 0, partDrop, relative=1)

                            # actualisation des matrices
                            matrixPos[r - 1] = [x for x in matrixPos[r]]
                            matrixName[r - 1] = [x for x in matrixName[r]]
                            dropped = 1

                        else:
                            matrixPos[r - 1] = [0 for x in matrixPos[r]]
                            matrixName[r - 1] = [0 for x in matrixName[r]]
                        r += 1

                    indexR = indexR - dropped  # fait revenir le scan a l index precedant si des blocs ont ete descendus

                indexR += 1

            # ------augmentation du score---------
            if (rowScore == 1):
                scoreTetris += 100
            elif (rowScore == 2):
                scoreTetris += 300
            elif (rowScore == 3):
                scoreTetris += 500
            elif (rowScore == 4):
                scoreTetris += 800
            nextLevel += rowScore
            totalLines += rowScore

            # ------niveau suivant---------
            if (nextLevel >= 10):
                nextLevel -= 10
                levelTetris += 1
                timeStep = timeStep * 0.75

            # --------------end check case------------------

            cmds.delete(futureTetrimino)
            # supprime les groupes vides
            lsGrp = cmds.ls('tetrimino*grp')
            for grp in lsGrp:
                if (cmds.listRelatives(grp, children=1) == None):
                    cmds.delete(grp)

        # --------end boucle tetrimino---------
        increment += 7

    cmds.refresh()
    cmds.confirmDialog(title="Score", button="Ok",
                       message="Game Over\n\n Final Score: {0}\n Lines: {1}\n Final Level: {2}".format(scoreTetris,
                                                                                                       totalLines,
                                                                                                       levelTetris))


# -------------Launch process-------------
def launchGameProcess():
    cmds.file(f=1, new=1)
    cmds.setFocus('modelPanel4')
    cleanGame()
    hotkeySet()
    viewportUI()
    runGame()
    restoreUI()


# ----------------------GUI----------------------

if (cmds.window('mainTetrisUI', exists=True)):
    cmds.deleteUI('mainTetrisUI', window=True)

cmds.window('mainTetrisUI')

cmds.columnLayout('cl1UI', adjustableColumn=True, rs=7)
cmds.text('tx1UI', label="Tetris for Maya", parent='cl1UI', h=30, font="boldLabelFont")
cmds.button('btnStartUI', label='Start Game', parent='cl1UI', c='launchGameProcess()')
cmds.separator('sep1UI', style="in", parent='cl1UI')

# hotkey et help
cmds.rowLayout('rl0UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('tx2UI', label="Hotkey", parent='rl0UI', h=20, font="plainLabelFont")
cmds.button('btnHelpUI', label="Help", parent='rl0UI', c='helpHotkey()')
# left move
cmds.rowLayout('rl1UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txLmoveUI', label="Left move: ", parent='rl1UI', font="plainLabelFont")
cmds.textField('tfLmoveUI', text="Left", parent='rl1UI')
# right move
cmds.rowLayout('rl2UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txRmoveUI', label="Right move: ", parent='rl2UI', font="plainLabelFont")
cmds.textField('tfRmoveUI', text="Right", parent='rl2UI')
# soft drop
cmds.rowLayout('rl3UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txSdropUI', label="Soft drop: ", parent='rl3UI', font="plainLabelFont")
cmds.textField('tfSdropUI', text="Down", parent='rl3UI')
# hard drop
cmds.rowLayout('rl4UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txHdropUI', label="Hard drop: ", parent='rl4UI', font="plainLabelFont")
cmds.textField('tfHdropUI', text="Space", parent='rl4UI')
# rotate
cmds.rowLayout('rl5UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txrotateUI', label="Rotate : ", parent='rl5UI', font="plainLabelFont")
cmds.textField('tfRotateUI', text="Up", parent='rl5UI')
# rotate
cmds.rowLayout('rl6UI', nc=2, parent='cl1UI', ad2=1)
cmds.text('txHoldUI', label="Hold : ", parent='rl6UI', font="plainLabelFont")
cmds.textField('tfHoldUI', text="c", parent='rl6UI')

cmds.window('mainTetrisUI', edit=1, h=300, w=150, maximizeButton=0, minimizeButton=0, sizeable=0,
            title="Tetris for Maya", cc='cleanGame()\ncmds.windowPref("mainTetrisUI", remove=True )')
cmds.showWindow('mainTetrisUI')