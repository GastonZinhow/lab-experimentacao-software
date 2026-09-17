package katas.k01;

/**
 * K01 - Is Subsequence (issue #22).
 * https://leetcode.com/problems/is-subsequence/
 *
 * Dadas duas strings s e t, determina se s e uma subsequencia de t (ou
 * seja, se e possivel obter s removendo alguns caracteres de t, sem
 * reordenar os caracteres restantes).
 */
public class Solution {
    public boolean isSubsequence(String s, String t) {
        int i = 0;
        int j = 0;

        while (i < s.length() && j < t.length()) {
            if (s.charAt(i) == t.charAt(j)) {
                i++;
                j++;
            } else {
                j++;
            }
        }

        if (i == s.length()) {
            return true;
        } else {
            return false;
        }

    }
}