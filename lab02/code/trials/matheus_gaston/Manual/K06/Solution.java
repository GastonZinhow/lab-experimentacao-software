package katas.k06;

import java.util.HashSet;
import java.util.Set;

/**
 * K06 - N-Queens II (issue #22).
 * https://leetcode.com/problems/n-queens-ii/
 *
 * Dado um inteiro n, retorna o numero de solucoes distintas do problema
 * das n rainhas: quantas formas existem de posicionar n rainhas em um
 * tabuleiro n x n de forma que nenhuma rainha ataque outra (mesma linha,
 * mesma coluna ou mesma diagonal).
 */

class Solution {
    private int boardSize;
    private int numberOfSolutions;

    private boolean[] usedColumn;
    private boolean[] usedMainDiagonal;
    private boolean[] usedSecondaryDiagonal;

    public int totalNQueens(int n) {
        boardSize = n;
        numberOfSolutions = 0;

        usedColumn = new boolean[n];
        usedMainDiagonal = new boolean[2 * n - 1];
        usedSecondaryDiagonal = new boolean[2 * n - 1];

        placeQueenInRow(0);

        return numberOfSolutions;
    }

    private void placeQueenInRow(int row) {
        if (row == boardSize) {
            numberOfSolutions++;
            return;
        }

        for (int column = 0; column < boardSize; column++) {
            if (isPositionUnderAttack(row, column)) {
                continue;
            }

            placeQueen(row, column);
            placeQueenInRow(row + 1);
            removeQueen(row, column);
        }
    }

    private boolean isPositionUnderAttack(int row, int column) {
        return usedColumn[column]
                || usedMainDiagonal[row - column + boardSize - 1]
                || usedSecondaryDiagonal[row + column];
    }

    private void placeQueen(int row, int column) {
        usedColumn[column] = true;
        usedMainDiagonal[row - column + boardSize - 1] = true;
        usedSecondaryDiagonal[row + column] = true;
    }

    private void removeQueen(int row, int column) {
        usedColumn[column] = false;
        usedMainDiagonal[row - column + boardSize - 1] = false;
        usedSecondaryDiagonal[row + column] = false;
    }
}