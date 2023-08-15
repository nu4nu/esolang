#!/usr/bin/python3

import transceternal_interpreter as ti

class Const(object):
    def __init__(self, bits):
        self.bits = bits

    def __repr__(self):
        return f'Const("{self.bits}")'

class Graph(object):
    def __init__(self, reserved, verbose=False):
        # Preferring printable 1-byte characters in [33...126] for debuggability
        self.chars = [chr(s) for s in range(128) if chr(s).isprintable() and chr(s) not in ti.JS_WHITESPACE]
        # The next candidates are the rest of 1-byte characters
        self.chars.extend([chr(s) for s in range(128) if not chr(s).isprintable() and chr(s) not in ti.JS_WHITESPACE])
        # Finally falling back to 2-byte printable characters
        self.chars.extend([chr(s) for s in range(0x80, 0x800) if chr(s).isprintable() and chr(s) not in ti.JS_WHITESPACE])
        for char in reserved:
            self.chars.remove(char)
        self.verbose = verbose
        self.nodes = {}
        self.const_cache = {}
        self.set_cache = {}
        self.branch_cache = {}
        self.if_cache = {}

    def add(self, label, node0, node1):
        self.nodes[label] = (node0, node1)

    def new(self, node0, node1):
        label = self.chars[0]
        self.chars = self.chars[1:]
        self.add(label, node0, node1)
        return label

    def new_node_with_cache(self, node0, node1, cache, label, type_):
        sig = (node0, node1)
        if sig in cache:
            return cache[sig]
        else:
            ret = self.new(node0, node1)
            cache[sig] = ret
            if self.verbose:
                print(f'{label}: add {type_} node {ret} ({node0}, {node1})')
            return ret

    def new_const_with_cache(self, addr0, addr1, is_swappable, label):
        sig0 = (addr0, addr1)
        sig1 = (addr1, addr0)
        if sig0 in self.const_cache:
            return self.const_cache[sig0]
        elif is_swappable and sig1 in self.const_cache:
            return self.const_cache[sig1]
        else:
            if addr1 == '':
                ret = self.new(Const(addr0), '2')
            else:
                ret = self.new(Const(addr0), Const(addr1))
            self.const_cache[sig0] = ret
            if self.verbose:
                print(f'{label}: add const node {ret} ("{addr0}", "{addr1}")')
            return ret

    def gen_set(self, label, dest, src, cont):
        cval = self.new_const_with_cache(dest, src, False, label)
        sval = self.new_node_with_cache('2', cval, self.set_cache, label, 'set')
        self.add(label, sval, cont)

    def gen_if(self, label, src0, src1, taken, cont):
        cval = self.new_const_with_cache(src0, src1, True, label)
        bval = self.new_node_with_cache(cval, taken, self.branch_cache, label, 'branch')
        ival = self.new_node_with_cache('0', bval, self.if_cache, label, 'if')
        self.add(label, ival, cont)

    def dump(self):
        for node, (node0, node1) in self.nodes.items():
            print(node, node0, node1)

    def serialize(self):
        nodes = set()
        stack = ['0']
        ret = ''
        while len(stack) > 0:
            node = stack.pop()
            ret += node
            if node not in nodes:
                nodes.add(node)
                stack.append(self.nodes[node][1])
                stack.append(self.nodes[node][0])
        return ret

    def calc_addrs(self):
        self.addrs = {}
        for node in self.nodes:
            node0, node1 = self.nodes[node]
            if node == '2':
                self.addrs['2'] = ''
                continue
            if node in ('0', '1', '3'):
                continue
            s = '0' if node0 == '2' or (isinstance(node0, Const) and node0.bits == '') else '1'
            visited = {node}
            trace = [node, node1]
            while True:
                if isinstance(node1, Const):
                    self.addrs[node] = s + node1.bits
                    break
                if node1 == '2' or node1 in visited:
                    self.addrs[node] = s
                    break
                if node1 in ('0', '1', '3'):
                    break
                visited.add(node1)
                node0, node1 = self.nodes[node1]
                s += '0' if node0 == '2' or (isinstance(node0, Const) and node0.bits == '') else '1'
                trace.append(node1)
            if self.verbose:
                print(trace)

    def dump_addrs(self):
        for node, (node0, node1) in self.nodes.items():
            if node0 in self.addrs.keys():
                node0str = f'"{self.addrs[node0]}"({node0})'
            elif isinstance(node0, Const):
                node0str = f'"{node0.bits}"'
            else:
                node0str = f'{node0}'
            if node1 in self.addrs.keys():
                node1str = f'"{self.addrs[node1]}"({node1})'
            elif isinstance(node1, Const):
                node1str = f'"{node1.bits}"'
            else:
                node1str = f'{node1}'
            print(f'{node}: ({node0str}, {node1str})')

    def gen_consts(self):
        self.calc_addrs()
        if self.verbose:
            self.dump_addrs()
        consts = {}
        for node, addr in self.addrs.items():
            if addr not in consts:
                consts[addr] = node

        if self.verbose:
            for const, node in consts.items():
                print(const, node)

        unresolved_consts = []
        for node0, node1 in self.nodes.values():
            if isinstance(node0, Const) and node0.bits not in consts.keys():
                v = (len(node0.bits), node0.bits)
                if v not in unresolved_consts:
                    unresolved_consts.append(v)
            if isinstance(node1, Const) and node1.bits not in consts.keys():
                v = (len(node1.bits), node1.bits)
                if v not in unresolved_consts:
                    unresolved_consts.append(v)

        unresolved_consts.sort()
        if self.verbose:
            print('unresolved consts:')
            for const in unresolved_consts:
                print(const)

        count = 0
        for _, const in unresolved_consts:
            stack = []
            while const not in consts.keys():
                stack.append(const[0])
                const = const[1:]
            node1 = consts[const]
            count += len(stack)
            while len(stack) > 0:
                head = stack.pop()
                node1 = self.new('2' if head == '0' else '0', node1)
                const = head + const
                consts[const] = node1

        if self.verbose:
            for const in consts:
                print(f'{const}: {len(consts[const].encode("utf-8"))}')

        for node, (node0, node1) in self.nodes.items():
            if isinstance(node0, Const):
                node0 = consts[node0.bits]
            if isinstance(node1, Const):
                node1 = consts[node1.bits]
            self.nodes[node] = (node0, node1)

    def rename_label(self, from_, to, is_swap=False):
        newnodes = {}
        for node, (node0, node1) in self.nodes.items():
            if node0 == from_:
                node0 = to
            elif is_swap and node0 == to:
                node0 = from_
            if node1 == from_:
                node1 = to
            elif is_swap and node1 == to:
                node1 = from_
            if is_swap:
                if node == from_:
                    node = to
                elif node == to:
                    node = from_
            else:
                if node == from_:
                    # TODO: Clean up cache
                    self.chars = [from_] + self.chars
                    del self.addrs[from_]
                    continue
            newnodes[node] = (node0, node1)
        self.nodes = newnodes

    def swap(self):
        counts = {}
        for node0, node1 in self.nodes.values():
            if node0 in counts:
                counts[node0] += 1
            else:
                counts[node0] = 1
            if node1 in counts:
                counts[node1] += 1
            else:
                counts[node1] = 1
        ones = [node for node in counts.keys() if counts[node] == 1 and len(node.encode('utf-8')) == 1 and not node.isprintable()]
        multis = [node for node in counts.keys() if counts[node] > 1 and len(node.encode('utf-8')) > 1]
        assert len(multis) <= len(ones)
        for i, dest in enumerate(multis):
            src = ones[i]
            self.rename_label(src, dest, True)
