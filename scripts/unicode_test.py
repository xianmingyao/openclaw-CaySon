#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unicodedata

test = b'\xe7\xad\x96\xe7\x95\xa5'.decode('utf-8')
print(f'Char 1: {repr(test[0])}, name: {unicodedata.name(test[0], "UNKNOWN")}')
print(f'Char 2: {repr(test[1])}, name: {unicodedata.name(test[1], "UNKNOWN")}')
print(f'Expected: 策 = {hex(ord("策"))}, 略 = {hex(ord("略"))}')

# Check if test[0] is actually '策'
print(f'test[0] == "策": {test[0] == "策"}')
print(f'test[0] == "{test[0]}": {test[0] == chr(0x7b56)}')
