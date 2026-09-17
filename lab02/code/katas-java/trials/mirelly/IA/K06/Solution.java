package katas.k06;

/**
 * K06 - N-Queens II (issue #22).
 * https://leetcode.com/problems/n-queens-ii/
 *
 * Dado um inteiro n, retorna o numero de solucoes distintas do problema
 * das n rainhas: quantas formas existem de posicionar n rainhas em um
 * tabuleiro n x n de forma que nenhuma rainha ataque outra (mesma linha,
 * mesma coluna ou mesma diagonal).
 */
public class Solution {

    public int totalNQueens(int n) {
        return solve(n, 0, new boolean[n], new boolean[2 * n], new boolean[2 * n]);
    }

    private int solve(int n, int row, boolean[] columns, boolean[] diagonals, boolean[] antiDiagonals) {
        if (row == n) {
            return 1;
        }

        int solutions = 0;
        for (int col = 0; col < n; col++) {
            int diagonal = row - col + n;
            int antiDiagonal = row + col;
            if (columns[col] || diagonals[diagonal] || antiDiagonals[antiDiagonal]) {
                continue;
            }

            columns[col] = true;
            diagonals[diagonal] = true;
            antiDiagonals[antiDiagonal] = true;

            solutions += solve(n, row + 1, columns, diagonals, antiDiagonals);

            columns[col] = false;
            diagonals[diagonal] = false;
            antiDiagonals[antiDiagonal] = false;
        }

        return solutions;
    }
}
