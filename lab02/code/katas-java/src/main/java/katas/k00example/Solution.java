package katas.k00example;

/**
 * Kata de exemplo (K00) - serve apenas de template/prova de conceito para o
 * setup do Maven + JUnit 5. Os katas reais do experimento (K01-K06, issue
 * #22) devem seguir esta mesma estrutura: um pacote katas.kNN com uma classe
 * de solucao e uma classe de teste correspondente contendo os testes de
 * aceitacao.
 *
 * Durante um trial real, o corpo dos metodos comeca com
 * "throw new UnsupportedOperationException()" e o participante o substitui
 * pela implementacao dentro do time-box.
 */
public class Solution {

    public String reverse(String input) {
        return new StringBuilder(input).reverse().toString();
    }

    public boolean isPalindrome(String input) {
        String normalized = input.toLowerCase().replaceAll("[^a-z0-9]", "");
        return normalized.equals(reverse(normalized));
    }
}
