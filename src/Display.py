import numpy as np
import sys
import os
import subprocess
import math
from Screen import Screen
from Colours import COLOURS
from DrawingUtils import *
from res.DisplayElements import *
from Constants import *


if(PLATFORM_PI):
    from serial import Serial


class Display:


    FONT_CHAR_WIDTH = 3
    FONT_CHAR_HEIGHT = 5
    BALL_CHARACTER = ' '
    SERIAL_BAUD_RATE = 115200
    SERIAL_ADDR = "/dev/ttyAMA0"


    def __init__(self):
        if(PLATFORM_PI):
            self._serialPort = Serial(Display.SERIAL_ADDR, Display.SERIAL_BAUD_RATE)
            if (self._serialPort.isOpen() == False):
                self._serialPort.open()

        rows, columns = subprocess.check_output(['stty', 'size']).split()
        self._windowDims = np.array([int(columns), int(rows)], dtype=int)

        # The distance (in characters) between the centre positions of 7 seg digits
        self._numCharCentreDist = int(Display.FONT_CHAR_WIDTH / 2) * 2 + 2

        self._netPosX = int(self._windowDims[0] / 2)
        self._screen = Screen(self._windowDims)

        print(colourResetCode())

        # Reset cursor position
        self.printOutput("\033[2J")

        # Hide cursor code
        self.printOutput(cursorVisibiltyCode(False))


    def printOutput(self, str):
        if(PLATFORM_PI and not PRINT_TO_TERMINAL):
            self._serialPort.write(bytes(str, 'ASCII'))
        else:
            print(str)


    def begin(self):
        self._screen.clear()


    def end(self):
        self.printOutput(self._screen.getOutputString())
        self._screen.swapBuffers()


    def drawBackground(self):
        self.drawNet()


    def drawNet(self):
        for i in range(1, self._windowDims[1]):
            if((i + 1) % 3 == 1 or (i + 2) % 3 == 1):
                self._screen.setColourIdxAt(list(COLOURS.keys()).index("net"), [self._netPosX, i])


    def drawScore(self, score, pos_centre):
        digits = [int(c) for c in str(score)]
        numDigits = len(digits)

        pos_centre_x = pos_centre[0]
        firstDigitPos_x = pos_centre_x - ((numDigits - 1) * (Display.FONT_CHAR_WIDTH + 1) // 2)

        for i in range(0, numDigits):
            digitPos_centre = np.array([firstDigitPos_x + i * self._numCharCentreDist, pos_centre[1]])
            self._draw7SegNumber(digits[i], digitPos_centre)


    def drawPlayer(self, player):
        paddle = player.paddle
        pos = np.around(paddle.position).astype(int)
        size = int(paddle.size)

        # Draw paddle
        for i in range(- size // 2, size // 2):
            p = np.around(np.array(pos) + np.array([0, i])).astype(int)
            colourName = "paddle" + ("Left" if player.side == Side.LEFT else "Right")
            colourCode = list(COLOURS.keys()).index(colourName)
            self._screen.setColourIdxAt(colourCode, p)


    def drawBall(self, ball):
        pos = np.around(ball.pos).astype(int)
        self._screen.setColourIdxAt(list(COLOURS.keys()).index("ball"), pos)


    def drawWinScreen(self, player):
        startPos_TL = np.array([(self._windowDims[0] - winTextWidth) // 2, (self._windowDims[1] - winTextHeight) // 2])
        counter = 0
        for i in range(0, len(winText_RLE)):
            if(i % 2 == 0):
                for j in range(0, winText_RLE[i]):
                    x = counter % winTextWidth
                    y = (counter - x) // winTextWidth
                    counter += 1
                    p = startPos_TL + np.array([x + 1, y + 1])
                    self._screen.setColourIdxAt(list(COLOURS.keys()).index("text"), p)
            else:
                counter += winText_RLE[i]

        self._draw7SegNumber(int(player.side) + 1, self._windowDims // 2)


    def _draw7SegNumber(self, num, pos_centre):
        if(num < 0 or num > 9):
            print("7-segment display can only display single-digit numbers (got " + str(num) + ")") 
            input()
            return

        # Each number should be drawn relative to the CENTRE of the 7 segment block
        pos_centre[0] -= Display.FONT_CHAR_WIDTH // 2 + 1
        pos_centre[1] -= Display.FONT_CHAR_HEIGHT // 2 + 1

        for y in range(0, 5):
            for x in range(0, 3):
                pos = np.array(pos_centre).astype(int) + np.array([x + 1, y + 1])
                if (digits[num][y * 3 + x] == 1):
                    self._screen.setColourIdxAt(list(COLOURS.keys()).index("text"), pos)


    def close(self):
        if(PLATFORM_PI):
            self._serialPort.close()

        self.printOutput(cursorVisibiltyCode(True))
        self.printOutput(colourResetCode())
        self.printOutput(cursorResetCode())


    @property
    def windowDims(self):
        return self._windowDims


    @property
    def netPosX(self):
        return self._netPosX
