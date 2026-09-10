package katas.k06;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K06 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();

    @Test
    void compactaApenasSequenciasDeTresOuMaisRepeticoes() {
        assertEquals("a3bbc4d", solution.compactar("aaabbccccd"));
    }

    @Test
    void naoCompactaSequenciasCurtasIsoladas() {
        assertEquals("aab4cca", solution.compactar("aabbbbcca"));
    }

    @Test
    void compactaSequenciaLongaComContagemDeDoisDigitos() {
        assertEquals("a10", solution.compactar("aaaaaaaaaa"));
    }

    @Test
    void textoVazioPermaneceVazio() {
        assertEquals("", solution.compactar(""));
    }

    @Test
    void descompactaSequenciaComCaracteresIsoladosECompactados() {
        assertEquals("aaabbccccd", solution.descompactar("a3bbc4d"));
    }

    @Test
    void descompactaSequenciaComContagemDeDoisDigitos() {
        assertEquals("aaaaaaaaaa", solution.descompactar("a10"));
    }

    @Test
    void compactarEDescompactarSaoInversas() {
        String original = "aabbbbccccccdde";

        String compactado = solution.compactar(original);
        String restaurado = solution.descompactar(compactado);

        assertEquals(original, restaurado);
    }
}
