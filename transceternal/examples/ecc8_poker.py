#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import transceternal_assembler as ta
import transceternal_interpreter as ti

verbose = False

graph = ta.Graph([chr(48 + n) for n in range(4)] +
                 [chr(97 + n) for n in range(26)] +
                 [chr(65 + n) for n in range(5)],
                 verbose)

graph.add('0', '1', 'A')
graph.add('1', '2', '1')
graph.add('2', '3', '2')
graph.add('3', '2', '3')
graph.gen_set('A', '010001', '1', 'B')
graph.gen_if('B', '0001', '1'*15+'0', 'v', 'C')
graph.gen_set('C', '', '1'*13+'0', 'D')
graph.add('D', '2', '2')  # dummy if to generate 11...110
graph.gen_set('v', '001', '1', 'w')
graph.gen_set('w', '1110', '1'*8, 'x')
graph.gen_set('x', '1'*13+'0', '1'*12+'0', 'y')
graph.gen_set('y', '1'*12+'0', '', 'z')
graph.gen_set('z', '1'*16+'0', '1'*8, 'a')
graph.gen_if('a', '0010', '10', 'b', 'c', if_addr='00'+'1'*15+'0')  # l
graph.gen_if('b', '00110', '110', 'E', 'c', if_addr='1')  # d,q,u
graph.gen_set('c', '001110', '1'*12+'0', 'E')
graph.gen_if('E', '0001', '1'*15+'0', 'd', 'v', if_addr='0001')  # dummy if to generate 11...11, B
graph.gen_set('d', '1', '1'*9, 'e')
graph.gen_if('e', '10', '0001', 'f', 'g', if_addr='00'+'1'*12+'0')  # i
graph.gen_if('f', '110', '0001', 'l', 'j', if_addr='1'*13+'0')  # x
graph.gen_if('g', '110', '0001', 'h', 'k', if_addr='00'+'1'*14+'0')  # k
graph.gen_if('h', '1110', '0001', 'i', 'm', if_addr='001110')  # c
graph.gen_set('i', '00'+'1'*12+'0', '1'*13+'0', 'n')
graph.gen_set('j', '00'+'1'*13+'0', '0', 'n')
graph.gen_set('k', '00'+'1'*14+'0', '1'*13+'0', 'n')
graph.gen_set('l', '00'+'1'*15+'0', '1'*10, 'n')
graph.gen_set('m', '00'+'1'*16+'0', '1'*14+'0', 'n')
graph.gen_set('n', '10', '1'*9, 'o')
graph.gen_set('o', '110', '1'*9, 'p')
graph.gen_set('p', '1110', '0001', 'q')
graph.gen_set('q', '1', '1'*9, 'r')
graph.gen_if('r', '0001', '1'*15+'0', 'a', 's', if_addr='10')  # n
graph.gen_set('s', '0010', '10', 't')
graph.gen_set('t', '00110', '110', 'u')
graph.gen_set('u', '1', '1'*9, 'B')

graph.gen_consts()
graph.swap()
#graph.dump()
program = graph.serialize()
#print(len(program), len(program.encode('utf-8')))
print(program, end='')

#print(ti.run(program, 'D3A2A5B1C4\nD2D1D3D4D5\nA2A3A2A1A4\nD3C2A2B1A4\n', verbose), end='')
