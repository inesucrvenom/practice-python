import argparse

def show_matrix(mat):
    result = '\n'.join([''.join(['{:3}'.format(item) for item in row])
                        for row in mat])
    print(result, '\n')



# dummy version, for testing purposes
def slow_print(m, n, l, t):
    sum_all = 0
    for row in range(n):
        line = ''
        sum_line = 0
        for col in range(m):
            item = row ^ col
            item = item - l if item >= l else 0
            line += '{:>3}'.format(item)
            sum_line += item
            if col % 8 == 7:
                line += '  '
        line += ' = {}'.format(sum_line)
        print(line)
        sum_all += sum_line
        if row % 8 == 7:
            print()
    print('== ', sum_all % t)

#
#
# parser = argparse.ArgumentParser()
# parser.add_argument("fn", type=str, help="which function to call")
# parser.add_argument("debug", type=int, help="debug level")
# parser.add_argument("col", type=int, help="columns of the matrix")
# parser.add_argument("row", type=int, help="rows of the matrix")
# parser.add_argument("loss", type=int, help="amount of loss")
# parser.add_argument("t", type=int, help="modulo")
# args = parser.parse_args()
#
# debug = args.debug
#
#
# if args.fn == 'slow':
#     slow_print(args.col, args.row, args.loss, args.t)

DELTAS = [
    [0, 1, 2, 3, 4, 5, 6, 7],
    [1, 0, 3, 2, 5, 4, 7, 6],
    [2, 3, 0, 1, 6, 7, 4, 5],
    [3, 2, 1, 0, 7, 6, 5, 4],
    [4, 5, 6, 7, 0, 1, 2, 3],
    [5, 4, 7, 6, 1, 0, 3, 2],
    [6, 7, 4, 5, 2, 3, 0, 1],
    [7, 6, 5, 4, 3, 2, 1, 0]]

def a_print_8x8(a, m, n, l, t):
    print(a, m, n, l, t)
    sum_all = 0
    for row in range(n):
        line = ''
        sum_line = 0
        for col in range(m):
            item = a + DELTAS[row][col]
            item = item - l if item >= l else 0
            line += '{:>4}'.format(item)
            sum_line += item
            if col % 8 == 7:
                line += '  '
        line += ' = {}'.format(sum_line)
        print(line)
        sum_all += sum_line
        if row % 8 == 7:
            print()
    print('== ', sum_all % t)

tests = [
    (8, 7, 6, 10, 10),
    (8, 5, 8, 20, 10),
    (16, 2, 3, 5, 10),
    (16, 5, 3, 15, 10),
    (8, 8, 8, 8, 10),
    (8, 7, 6, 10, 100),
    (8, 5, 8, 20, 100),
    (800, 2, 3, 50, 100),
    (1600, 5, 3, 1500, 100),
    (80, 8, 8, 78, 100),
]
#
# if __name__ == '__main__':
#     for test in tests:
#         (a, c, r, loss, mod) = test
#         a_print_8x8(a, c, r, loss, mod)

if __name__ == '__main__':
    slow_print(16, 4, 1, 1000)
