package katas.k00example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Testes de aceitacao do kata de exemplo K00. Em um trial real estes testes
 * NAO sao alterados pelo participante: eles definem o "pronto" da tarefa e
 * sao usados pelo script de cronometragem (issue #20) para calcular o
 * time-to-green e a taxa de sucesso ao final do time-box.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @ParameterizedTest
    @CsvSource({
        "abc, cba",
        "kata, atak",
        "a, a",
        "'', ''"
    })
    void reverseInvertsCharacters(String input, String expected) {
        assertEquals(expected, solution.reverse(input));
    }

    @Test
    void isPalindromeAcceptsSimplePalindrome() {
        assertTrue(solution.isPalindrome("arara"));
    }

    @Test
    void isPalindromeIgnoresCaseAndPunctuation() {
        assertTrue(solution.isPalindrome("A man, a plan, a canal: Panama"));
    }

    @Test
    void isPalindromeRejectsNonPalindrome() {
        assertFalse(solution.isPalindrome("kata"));
    }
}
