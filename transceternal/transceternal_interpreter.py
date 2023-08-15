#!/usr/bin/python3

import re
import sys

# Note that /\s/.test() in JavaScript and str.isspace() in Python differ
# /\s/.test(x): [9, 10, 11, 12, 13,                 32,      160, 5760, ...]
# x.isspace():  [9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 133, 160, 5760, ...]
JS_WHITESPACE = '\x09\x0a\x0b\x0c\x0d \xa0\u1680'

def dump_graph(names, root):
    print(f'root = {names[id(root)]}')
    print(f'b0 = {names[id(root[0][0][0])]}')
    print(f'b1 = {names[id(root[0][0][1])]}')
    stack = [root]
    visited = {id(root)}
    while len(stack) > 0:
        node = stack.pop()
        print(names[id(node)], names[id(node[0])], names[id(node[1])])
        if id(node[0]) not in visited:
            visited.add(id(node[0]))
            stack.append(node[0])
        if id(node[1]) not in visited:
            visited.add(id(node[1]))
            stack.append(node[1])

def run(src, input_, verbose=False):
    if any(c in src for c in JS_WHITESPACE):
        tokens = re.split(f'[{JS_WHITESPACE}]+', src.strip(JS_WHITESPACE))
    else:
        tokens = list(src)

    root = []
    if len(tokens) > 0:
        names = {}
        nodes = {}
        stack = [root]
        names[id(root)] = tokens[0]
        nodes[tokens[0]] = root
        for token in tokens[1:]:
            if len(stack) == 0:
                break
            last = stack[-1]
            if token in nodes.keys():
                node = nodes[token]
            else:
                node = []
                names[id(node)] = token
                nodes[token] = node
            last.append(node)
            while len(stack[-1]) == 2:
                stack.pop()
                if len(stack) == 0:
                    break
            if node == []:
                stack.append(node)
        while len(stack) > 0:
            node = stack.pop()
            while len(node) < 2:
                node.append(node)
    else:
        names = {'(empty)': id(root)}
        root.append(root)
        root.append(root)

    input_bits = []
    for s in input_:
        x = ord(s)
        for b in range(8):
            input_bits.append(x & 1)
            x >>= 1

    root = [root]
    names[id(root)] = 'root'
    ionode = root
    for i, b in enumerate(input_bits):
        newnode = [root[0][0][b]]
        names[id(newnode)] = f'input[{i}]'
        ionode.append(newnode)
        ionode = newnode
    ionode.append(root[0][0][0])

    def get(addr):
        node = root
        for bit in addr:
            node = node[int(bit)]
        return node

    def set_(addr, val):
        nonlocal root
        if len(addr) == 0:
            root = val
            return val
        node = get(addr[:-1])
        node[int(addr[-1])] = val
        return val

    def add(addr, val1, val2):
        return set_(addr, [val1, val2])

    def addr(node):
        b0 = id(root[0][0][0])
        visited = set()
        address = ''
        while id(node) != b0 and id(node) not in visited:
            visited.add(id(node))
            address += '1' if id(node[0]) != b0 else '0'
            node = node[1]
        return address

    def nodename(pc):
        return f'{names[id(pc)]}'

    def addrname(addr, isdest=False):
        if len(addr) > 0 and isdest:
            return f'{addr}<{names[id(get(addr[:-1]))]}[{addr[-1]}]>'
        else:
            return f'{addr}<{names[id(get(addr))]}>'

    # dump_graph(names, root)

    while True:
        pc = root[0][1]
        if id(pc) == id(root[0][0][0]):
            break

        type_ = id(pc[0][0])
        node = pc[0][1]
        if type_ == id(root[0][0][0]):
            d = addr(node[0])
            s = addr(node[1])
            if verbose:
                print(f'{nodename(pc)}: set {addrname(d, True)} {addrname(s)}')
            set_(d, get(s))
            root[0][1] = root[0][1][1]
        elif type_ == id(root[0][0][1]):
            d = addr(node[0])
            s0 = addr(node[1][0])
            s1 = addr(node[1][1])
            if verbose:
                print(f'{nodename(pc)}: add {addrname(d, True)} ({addrname(s0)}, {addrname(s1)})')
            add(d, get(s0), get(s1))
            root[0][1] = root[0][1][1]
        else:
            s0 = addr(node[0][0])
            s1 = addr(node[0][1])
            if verbose:
                print(f'{nodename(pc)}: if {addrname(s0)} == {addrname(s1)} ? {nodename(node[1])} : {nodename(pc[1])}')
            if id(get(s0)) == id(get(s1)):
                root[0][1] = node[1]
            else:
                root[0][1] = root[0][1][1]

    output = addr(root[1])

    ret = ''
    for ix in range(0, len(output), 8):
        bs = output[ix:ix+8]
        ret += chr(sum(int(b) << i for i, b in enumerate(bs)))
    return ret

def main():
    with open(sys.argv[1]) as f:
        src = f.read()
    # Caution: this rstrip() is added for convenience and not compatible with the original JS implementation
    while src[-1] in JS_WHITESPACE:
        src = src[:-1]
    input_ = sys.stdin.read()
    output = run(src, input_, len(sys.argv) > 2)
    print(output, end='')

if __name__ == '__main__':
    main()
