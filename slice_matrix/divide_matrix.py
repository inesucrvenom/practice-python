debug = 1


def print_debug(inputs):
    print(">>>", inputs)
    # print(global_previous)


def pretty_print(first_row, first_col, rows, cols):
    print("first_row, first_col, dim", first_row, first_col, rows, cols)
    sum_mat = 0
    for row in range(rows):
        sum_row = 0
        line = ""
        for col in range(cols):
            item = apply_loss_mod((first_row + row) ^ (first_col + col))
            sum_row += item
            line += "{:3}".format(item)
            if col % 8 == 7:
                line += " "
        sum_mat += sum_row
        print(line, " = ", sum_row)
        if row % 8 == 7:
            print()
    print(" == ", sum_mat)


def show_matrix(mat):
    result = "\n".join(
        ["".join(["{:3}".format(item) for item in row]) for row in mat]
    )
    print(result, "\n")


#### end of debug helpers

"""
second approach, aiming for reusing 2**k * 2**k matrices as much as possible

a^b == a XOR b (bitwise XOR) in the code
2**k == pow(2,k) (math exponent 2^k could happen in the comments)

version that uses formula for full square matrices as much as possible
- divides whole table into blocks recursively
- saves intermediary results
- checks for null matrices to return faster


full matrix of 8x8 looks like:

    a    a+1  a+2  a+3  a+4  a+5  a+6  a+7
    a+1  a    a+3  a+2  a+5  a+4  a+7  a+6
    a+2  a+3  a    a+1  a+6  a+7  a+4  a+5
    a+3  a+2  a+1  a    a+7  a+6  a+5  a+4
    a+4  a+5  a+6  a+7  a    a+1  a+2  a+3
    a+5  a+4  a+7  a+6  a+1  a    a+3  a+2
    a+6  a+7  a+4  a+5  a+2  a+3  a    a+1
    a+7  a+6  a+5  a+4  a+3  a+2  a+1  a

If we have full square matrix of any dim = 2**k, with top left element of a
then it's sum is:
sum_full = {all a elements + sum of matrix when a == o }
         = a * dim * dim + (dim / 2) * dim * (0 + dim-1)
         = dim * dim * (a + (dim - 1)/2)
         = { rows * one row}
         = dim * ( dim/2 * (0 + dim-1) + a * dim )

in case of loss, we have bunch of zeroes
sum_with_zero   = {rows * one row} = rows * { (smallest + biggest) * n/2}
                = dim * (0 + dim-1-loss) * (dim - loss)/2



- every matrix split will looks like:
  ```
  A B       top-left = A        top-right = B
  C D       bottom-left = C     bottom-right = D
  ```
  - only A is a guaranteed to be a square matrix
    - until its dimensions are smaller or equal to the OFFSET_SIZE
"""

# constant independent of values given during the execution
OFFSET_SIZE = 16  # todo: see if bigger block makes sense, and which
# todo: check for 32, 64, 128

# globals defined in the initalise function
global_previous = {}  # (min_dim, max_dim, biggest_element_modulo_LOSS) TUPLE!!!
OFFSET = []  # helper matrix of size OFFSET_SIZE
MODULO = 0
LOSS = 0

from math import log2


def get_globals():
    "function for testing purposes"
    return {
        "global_previous": global_previous,
        "OFFSET": OFFSET,
        "MODULO": MODULO,
        "LOSS": LOSS,
    }


def initialise(l, t):
    """
    will initialise
    - MODULO, LOSS : int, global constants
    - global_previous : dict, stores intermediary values of matrix sum calculations
        key: (min_dim, max_dim, biggest_element_modulo_LOSS)
            where dim are number of rows or columns
    - OFFSET : table, store offset values from a in a square matrix - LOSS
        - a is top left element
        - will be used to calculate sums for smallest non square block matrices
        - current size: OFFSET_SIZE
    """
    global MODULO, LOSS, OFFSET, global_previous

    global_previous = {}
    MODULO = t
    LOSS = l
    OFFSET = []

    for row in range(OFFSET_SIZE):
        new_row = []
        for col in range(OFFSET_SIZE):
            new_row.append(apply_mod(row ^ col))
        OFFSET.append(new_row)


def apply_mod(num):
    """ simplifies writing of modulo num """
    return num % MODULO


def apply_loss_mod(num):
    """ simplifies writing of modulo loss """
    tmp = num - LOSS
    tmp = tmp if tmp > 0 else 0
    return apply_mod(tmp)


def sum_split_squares(first_row_id, first_col_id, dim_rows, dim_cols):
    """
    gets top left element indices, number of rows and columns
    find biggest k so that dim = 2**k <= smallest dim of B
    split B into new AA, BB, CC, DD where you use formula on AA and
        call split_into_squares on the rest

    returns sum_of_elements
    """
    if debug:
        print_debug(
            ["split squares", first_row_id, first_col_id, dim_rows, dim_cols]
        )

    if dim_rows <= OFFSET_SIZE and dim_cols <= OFFSET_SIZE:
        return sum_per_offset(first_row_id, first_col_id, dim_rows, dim_cols)

    # something smaller than offset but only in one dimension
    result = 0

    if dim_rows <= OFFSET_SIZE:
        result += sum_per_offset(
            first_row_id, first_col_id, dim_rows, OFFSET_SIZE
        )
        result += sum_split_squares(
            first_row_id,
            first_col_id + OFFSET_SIZE,
            dim_rows,
            dim_cols - OFFSET_SIZE,
        )
        return result

    if dim_cols <= OFFSET_SIZE:
        result += sum_per_offset(
            first_row_id, first_col_id, OFFSET_SIZE, dim_cols
        )
        result += sum_split_squares(
            first_row_id + OFFSET_SIZE,
            first_col_id,
            dim_rows - OFFSET_SIZE,
            dim_cols,
        )
        return result

    # find smallest k that 2**k x 2**k fits into dim_rows x dim_cols matrix
    kr = int(log2(dim_rows))
    kc = int(log2(dim_cols))
    dim_splitter = 2 ** min(kr, kc)

    # nothing to split into
    if dim_rows == dim_cols == dim_splitter:
        return sum_square(first_row_id, first_col_id, dim_splitter)

    # top left, 2**k x 2**k - sum only here, the rest are a new splits
    result += sum_square(first_row_id, first_col_id, dim_splitter)

    dim_bottom_rows = dim_rows - dim_splitter
    dim_right_cols = dim_cols - dim_splitter

    # bottom_right, 2**(r-k) x 2**(c-k)
    result += sum_split_squares(
        first_row_id + dim_splitter,
        first_col_id + dim_splitter,
        dim_bottom_rows,
        dim_right_cols,
    )

    # bottom left, 2**(r-k) x 2**k
    result += sum_split_squares(
        first_row_id + dim_splitter,
        first_col_id,
        dim_bottom_rows,
        dim_splitter,
    )

    # top right, 2**k x 2**(c-k)
    result += sum_split_squares(
        first_row_id, first_col_id + dim_splitter, dim_splitter, dim_right_cols,
    )

    if debug:
        print("end split", apply_mod(result))
    return apply_mod(result)


def sum_square(first_row_id, first_col_id, dim):
    """ returns sum of matrix of dimension 2**k using formula"""
    global global_previous
    if debug:
        print_debug([sum_square, first_row_id, first_col_id, dim, dim])
        pretty_print(first_row_id, first_col_id, dim, dim)

    # right_neighbour_el = apply_loss_mod(first_row_id ^ (first_col_id + 1))

    potentially_smallest_el = first_row_id ^ first_col_id
    potentially_biggest_el = first_row_id ^ (first_col_id + dim - 1)

    if MODULO < (potentially_biggest_el - LOSS):
        # hard to calculate how many zeroes, easier to just sum directly
        sum_row = 0
        for col in range(dim):
            sum_row += apply_loss_mod(first_row_id ^ (first_col_id + col))
        sum_mat = apply_mod(dim * sum_row)
        global_previous[(biggest_el, dim)] = sum_mat
        return sum_mat

    smallest_el = apply_loss_mod(potentially_smallest_el)
    biggest_el = apply_loss_mod(potentially_biggest_el)
    row_num_el = biggest_el + 1 if biggest_el < dim else dim

    if smallest_el == 0 and biggest_el == 0:
        return 0

    # already have it
    check = global_previous.get((biggest_el, dim))
    if check is not None:
        return check

    # can use formula for matrix
    sum_row = (smallest_el + biggest_el) * (row_num_el) / 2
    sum_mat = apply_mod(dim * sum_row)
    global_previous[(biggest_el, dim)] = sum_mat

    return sum_mat

def sum_per_offset(first_row_id, first_col_id, dim_rows, dim_cols):
    if debug:
        print_debug(
            ["---smallest---", first_row_id, first_col_id, dim_rows, dim_cols]
        )
        pretty_print(first_row_id, first_col_id, dim_rows, dim_cols)

    smallest_el = apply_mod(first_row_id ^ first_col_id)
    result_sum = 0
    for row in range(dim_rows):
        for col in range(dim_cols):
            tmp = OFFSET[row][col]
            item = apply_loss_mod(smallest_el + OFFSET[row][col])
            result_sum = apply_mod(result_sum + item)

    if debug:
        print("end smallest", apply_mod(result_sum))
    return apply_mod(result_sum)


def elder_age(cols, rows, loss, mod):
    initialise(loss, mod)
    return sum_split_squares(0, 0, rows, cols)


# for debugging purposes
if __name__ == "__main__":
    # print(elder_age(25, 34, 1, 100000), 776)
    initialise(10, 1000)
    print(sum_square(8, 0, 8), 120)
