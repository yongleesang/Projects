import requests
import bs4
import numpy as np


def main():
    print('sudoku solver')
    level = input("level of difficulty from 1-4 ")
    suduko_id = input("sudoku map id ")
    gridurl = "https://grid.websudoku.com/?level={}&set_id={}&goto=+Go+to+this+puzzle+".format(level, suduko_id)
    resp = requests.get(gridurl)
    if resp.status_code in {400, 404, 500}:
        print("Error: {}".format(resp.text))

    soup = bs4.BeautifulSoup(resp.content, 'html.parser')
    answers_sudoku = soup.find(id='cheat')['value']
    sudoku_mask = soup.find(id='editmask')['value']
    non_answered_sudoku = get_unanswered_sudoku(answers_sudoku, sudoku_mask)
    sudoku_map = get_matrix_grid(non_answered_sudoku, 9)
    print(np.mat(sudoku_map))
    solve(sudoku_map)


def get_unanswered_sudoku(answer, mask):
    new_answer = ''
    for i in range(len(mask)):
        if mask[i] == '1':
            new_answer += '0'
        else:
            new_answer += answer[i]

    return new_answer


# Function to string into grid form
def get_matrix_grid(str, k):
    wholelst = []
    for i in range(len(str)):
        if i % k == 0:
            sub = str[i:i + k]
            lst = []
            for j in sub:
                lst.append(int(j))
            wholelst.append(lst)

    return wholelst


def possible(y, x, n, sudoku):
    for i in range(0, 9):
        if sudoku[y][i] == n:
            return False
    for i in range(0, 9):
        if sudoku[i][x] == n:
            return False
    x0 = (x//3)*3
    y0 = (y//3)*3
    for i in range(0, 3):
        for j in range(0, 3):
            if sudoku[y0+i][x0+j] == n:
                return False
    return True


def solve(sudoku):
    for y in range(9):
        for x in range(9):
            if sudoku[y][x] == 0:
                for n in range(1, 10):
                    if possible(y, x, n, sudoku):
                        sudoku[y][x] = n
                        solve(sudoku)
                        sudoku[y][x] = 0
                return

    print(np.mat(sudoku))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
