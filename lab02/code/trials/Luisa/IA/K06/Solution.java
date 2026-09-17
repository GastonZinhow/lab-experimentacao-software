class Solution {
    private int count = 0;

    public int totalNQueens(int n) {
        int[] cols = new int[n]; // cols[row] = coluna da rainha naquela linha
        backtrack(0, n, cols, new boolean[n], new boolean[2 * n - 1], new boolean[2 * n - 1]);
        return count;
    }

    private void backtrack(int row, int n, int[] cols, boolean[] usedCol,
                            boolean[] usedDiag1, boolean[] usedDiag2) {
        if (row == n) {
            count++;
            return;
        }
        for (int col = 0; col < n; col++) {
            int diag1 = row - col + n - 1; // diagonal "\"
            int diag2 = row + col;         // diagonal "/"
            if (usedCol[col] || usedDiag1[diag1] || usedDiag2[diag2]) continue;

            usedCol[col] = usedDiag1[diag1] = usedDiag2[diag2] = true;
            backtrack(row + 1, n, cols, usedCol, usedDiag1, usedDiag2);
            usedCol[col] = usedDiag1[diag1] = usedDiag2[diag2] = false;
        }
    }
}