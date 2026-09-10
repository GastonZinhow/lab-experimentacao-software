package katas.k05;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K05 (issue #22), baseados nos exemplos oficiais
 * do LeetCode. Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void encontraSubsequenciaPalindromicaDeQuatroCaracteres() {
        assertEquals(4, solution.longestPalindromeSubseq("bbbab"));
    }

    @Test
    void encontraSubsequenciaPalindromicaDeDoisCaracteres() {
        assertEquals(2, solution.longestPalindromeSubseq("cbbd"));
    }

    @Test
    void stringDeUmCaractereEPalindromoDeTamanhoUm() {
        assertEquals(1, solution.longestPalindromeSubseq("a"));
    }

    @Test
    void stringJaPalindromaRetornaOProprioTamanho() {
        assertEquals(5, solution.longestPalindromeSubseq("aba" + "ba"));
    }

    @Test
    void stringSemRepeticaoRetornaUm() {
        assertEquals(1, solution.longestPalindromeSubseq("abcde"));
    }
}
