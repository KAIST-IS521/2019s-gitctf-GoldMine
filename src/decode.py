#!/usr/bin/env python
# coding:UTF-8

import cv2


class Blend():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height

        self.mask_one_list = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_one = self.mask_one_list.pop(0)
        self.mask_zero_list = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_zero = self.mask_zero_list.pop(0)

        self.current_width = 0
        self.current_height = 0
        self.current_channel = 0

    def put_binary_data(self, bits):
        for c in bits:
            val = list(self.image[self.current_height,self.current_width])
            if int(c) == 1:
                val[self.current_channel] = int(val[self.current_channel]) | self.mask_one
            else:
                val[self.current_channel] = int(val[self.current_channel]) & self.mask_zero

            self.image[self.current_height,self.current_width] = tuple(val)
            self.next_slot()

    def next_slot(self):
        if self.current_channel == self.nbchannels - 1:
            self.current_channel = 0
            if self.current_width == self.width - 1:
                self.current_width = 0
                if self.current_height == self.height - 1:
                    self.current_height = 0
                    if self.mask_one == 128:
                        raise Exception("All slot is filled")
                    else:
                        self.mask_one = self.mask_one_list.pop(0)
                        self.mask_zero = self.mask_zero_list.pop(0)
                else:
                    self.current_height += 1
            else:
                self.current_width += 1
        else:
            self.current_channel += 1

    def read_data(self):
        val = self.image[self.current_height,self.current_width][self.current_channel]
        val = int(val) & self.mask_one
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"

    def read_datas(self, nb):
        bits = ""
        for _ in range(nb):
            bits += self.read_data()
        return bits

    def binary_data(self, val, bitsize):
        binary_value = bin(val)[2:]
        if len(binary_value) > bitsize:
            raise Exception("The data is larger than expected")
        while len(binary_value) < bitsize:
            binary_value = "0"+binary_value
        return binary_value

    def decode(self):
        ls = self.read_datas(16)
        l = int(ls, 2)
        i = 0
        result = ""
        ind = max(l, self.size / 50)
        while i < ind:
            tmp = self.read_datas(8)
            if (i < l):
                result += chr(int(tmp, 2))
            i += 1
        return result
