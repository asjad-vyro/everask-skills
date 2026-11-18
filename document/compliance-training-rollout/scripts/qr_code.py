#!/usr/bin/env python3
"""Make a QR code for a link, as an SVG (for posters and printouts).

Usage:
    python3 qr_code.py --url "https://example.com/training" [--out qr.svg] [--ecc M]

--ecc: error correction L, M (default), Q or H. Q or H survive a scuffed or
partly covered floor poster better but make a denser code.

Prints JSON: {"url", "version", "ecc", "modules", "mask", "svg_file", "svg"}.
"svg" is the code itself (black squares on white, 4-module quiet border), ready to
paste into HTML. Links up to about 200 characters fit. Stdlib only, no network.
"""

import json
import sys

# Error-correction codewords per block and number of blocks, indexed
# [level][version] for versions 1-40 (QR Code spec, ISO/IEC 18004 table 9).
ECC_CODEWORDS_PER_BLOCK = {
    "L": (-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
    "M": (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),
    "Q": (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
    "H": (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
}
NUM_BLOCKS = {
    "L": (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),
    "M": (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),
    "Q": (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68),
    "H": (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81),
}
FORMAT_BITS = {"L": 1, "M": 0, "Q": 3, "H": 2}
MAX_VERSION = 15


def gf_mul(x, y):
    z = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def rs_divisor(degree):
    result = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for j in range(degree):
            result[j] = gf_mul(result[j], root)
            if j + 1 < degree:
                result[j] ^= result[j + 1]
        root = gf_mul(root, 0x02)
    return result


def rs_remainder(data, divisor):
    result = [0] * len(divisor)
    for b in data:
        factor = b ^ result.pop(0)
        result.append(0)
        for i, coef in enumerate(divisor):
            result[i] ^= gf_mul(coef, factor)
    return result


def raw_modules(ver):
    result = (16 * ver + 128) * ver + 64
    if ver >= 2:
        n = ver // 7 + 2
        result -= (25 * n - 10) * n - 55
        if ver >= 7:
            result -= 36
    return result


def data_codewords(ver, ecc):
    return raw_modules(ver) // 8 - ECC_CODEWORDS_PER_BLOCK[ecc][ver] * NUM_BLOCKS[ecc][ver]


def alignment_positions(ver):
    if ver == 1:
        return []
    n = ver // 7 + 2
    step = (ver * 8 + n * 3 + 5) // (n * 4 - 4) * 2
    size = ver * 4 + 17
    result = [size - 7 - i * step for i in range(n - 1)] + [6]
    return list(reversed(result))


def encode_data(payload, ecc):
    for ver in range(1, MAX_VERSION + 1):
        count_bits = 8 if ver <= 9 else 16
        capacity = data_codewords(ver, ecc) * 8
        if 4 + count_bits + len(payload) * 8 <= capacity:
            break
    else:
        raise ValueError("Link too long for a QR code this script makes (max about 200 characters)")
    bits = []

    def put(value, length):
        bits.extend((value >> i) & 1 for i in reversed(range(length)))

    put(0b0100, 4)
    put(len(payload), count_bits)
    for b in payload:
        put(b, 8)
    put(0, min(4, capacity - len(bits)))
    put(0, (8 - len(bits) % 8) % 8)
    pad = 0xEC
    while len(bits) < capacity:
        put(pad, 8)
        pad ^= 0xEC ^ 0x11
    codewords = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    return ver, codewords


def add_ecc_and_interleave(data, ver, ecc):
    num_blocks = NUM_BLOCKS[ecc][ver]
    block_ecc = ECC_CODEWORDS_PER_BLOCK[ecc][ver]
    raw = raw_modules(ver) // 8
    num_short = num_blocks - raw % num_blocks
    short_len = raw // num_blocks
    divisor = rs_divisor(block_ecc)
    blocks, k = [], 0
    for i in range(num_blocks):
        dat = data[k:k + short_len - block_ecc + (0 if i < num_short else 1)]
        k += len(dat)
        ecc_part = rs_remainder(dat, divisor)
        if i < num_short:
            dat = dat + [0]
        blocks.append(dat + ecc_part)
    result = []
    for i in range(len(blocks[0])):
        for j, blk in enumerate(blocks):
            if i != short_len - block_ecc or j >= num_short:
                result.append(blk[i])
    return result


class Matrix:
    def __init__(self, ver):
        self.ver = ver
        self.size = ver * 4 + 17
        self.mod = [[False] * self.size for _ in range(self.size)]
        self.func = [[False] * self.size for _ in range(self.size)]

    def set_func(self, x, y, dark):
        self.mod[y][x] = dark
        self.func[y][x] = True

    def draw_function_patterns(self, ecc):
        s = self.size
        for i in range(s):
            self.set_func(6, i, i % 2 == 0)
            self.set_func(i, 6, i % 2 == 0)
        for cx, cy in ((3, 3), (s - 4, 3), (3, s - 4)):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < s and 0 <= y < s:
                        self.set_func(x, y, max(abs(dx), abs(dy)) not in (2, 4))
        pos = alignment_positions(self.ver)
        last = len(pos) - 1
        for i, a in enumerate(pos):
            for j, b in enumerate(pos):
                if (i == 0 and j == 0) or (i == 0 and j == last) or (i == last and j == 0):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        self.set_func(a + dx, b + dy, max(abs(dx), abs(dy)) != 1)
        self.draw_format(ecc, 0)
        if self.ver >= 7:
            rem = self.ver
            for _ in range(12):
                rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
            bits = self.ver << 12 | rem
            for i in range(18):
                dark = (bits >> i) & 1 == 1
                a, b = s - 11 + i % 3, i // 3
                self.set_func(a, b, dark)
                self.set_func(b, a, dark)

    def draw_format(self, ecc, mask):
        data = FORMAT_BITS[ecc] << 3 | mask
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = (data << 10 | rem) ^ 0x5412
        bit = lambda i: (bits >> i) & 1 == 1
        s = self.size
        for i in range(6):
            self.set_func(8, i, bit(i))
        self.set_func(8, 7, bit(6))
        self.set_func(8, 8, bit(7))
        self.set_func(7, 8, bit(8))
        for i in range(9, 15):
            self.set_func(14 - i, 8, bit(i))
        for i in range(8):
            self.set_func(s - 1 - i, 8, bit(i))
        for i in range(8, 15):
            self.set_func(8, s - 15 + i, bit(i))
        self.set_func(8, s - 8, True)

    def draw_codewords(self, data):
        s, i = self.size, 0
        right = s - 1
        while right >= 1:
            if right == 6:
                right = 5
            for vert in range(s):
                for j in range(2):
                    x = right - j
                    upward = ((right + 1) & 2) == 0
                    y = s - 1 - vert if upward else vert
                    if not self.func[y][x] and i < len(data) * 8:
                        self.mod[y][x] = (data[i >> 3] >> (7 - (i & 7))) & 1 == 1
                        i += 1
            right -= 2

    def apply_mask(self, mask):
        tests = (
            lambda x, y: (x + y) % 2 == 0,
            lambda x, y: y % 2 == 0,
            lambda x, y: x % 3 == 0,
            lambda x, y: (x + y) % 3 == 0,
            lambda x, y: (x // 3 + y // 2) % 2 == 0,
            lambda x, y: x * y % 2 + x * y % 3 == 0,
            lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
            lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
        )
        t = tests[mask]
        for y in range(self.size):
            for x in range(self.size):
                if not self.func[y][x] and t(x, y):
                    self.mod[y][x] = not self.mod[y][x]

    def penalty(self):
        s, m, score = self.size, self.mod, 0
        lines = [row[:] for row in m] + [[m[y][x] for y in range(s)] for x in range(s)]
        pat_a = [False] * 4 + [True, False, True, True, True, False, True]
        pat_b = [True, False, True, True, True, False, True] + [False] * 4
        for line in lines:
            run, prev = 0, None
            for v in line:
                if v == prev:
                    run += 1
                else:
                    if run >= 5:
                        score += 3 + run - 5
                    run, prev = 1, v
            if run >= 5:
                score += 3 + run - 5
            padded = [False] * 4 + line + [False] * 4
            for i in range(len(padded) - 10):
                window = padded[i:i + 11]
                if window == pat_a or window == pat_b:
                    score += 40
        for y in range(s - 1):
            for x in range(s - 1):
                c = m[y][x]
                if c == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                    score += 3
        dark = sum(v for row in m for v in row)
        total = s * s
        k = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        return score + k * 10


def make_qr(url, ecc="M", mask=None):
    ecc = ecc.upper()
    if ecc not in FORMAT_BITS:
        raise ValueError("ecc must be L, M, Q or H")
    ver, data = encode_data(url.encode("utf-8"), ecc)
    codewords = add_ecc_and_interleave(data, ver, ecc)
    best = None
    for m in ([mask] if mask is not None else range(8)):
        mat = Matrix(ver)
        mat.draw_function_patterns(ecc)
        mat.draw_codewords(codewords)
        mat.apply_mask(m)
        mat.draw_format(ecc, m)
        p = mat.penalty()
        if best is None or p < best[0]:
            best = (p, m, mat)
    return best[2], best[1]


def to_svg(mat, border=4):
    size = mat.size + border * 2
    parts = []
    for y in range(mat.size):
        for x in range(mat.size):
            if mat.mod[y][x]:
                parts.append("M%d,%dh1v1h-1z" % (x + border, y + border))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'shape-rendering="crispEdges"><rect width="100%%" height="100%%" fill="#fff"/>'
            '<path d="%s" fill="#000"/></svg>') % (size, size, "".join(parts))


def main(argv):
    if "--url" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    url = argv[argv.index("--url") + 1].strip()
    ecc = argv[argv.index("--ecc") + 1] if "--ecc" in argv else "M"
    out = argv[argv.index("--out") + 1] if "--out" in argv else ""
    if not url:
        print(json.dumps({"error": "Empty link"}))
        return 1
    try:
        mat, mask = make_qr(url, ecc)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    svg = to_svg(mat)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(svg)
    print(json.dumps({"url": url, "version": mat.ver, "ecc": ecc.upper(), "modules": mat.size,
                      "mask": mask, "svg_file": out, "svg": svg}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
