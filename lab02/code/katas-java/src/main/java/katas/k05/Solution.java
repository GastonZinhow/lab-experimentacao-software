package katas.k05;

import java.util.List;

/**
 * K05 - Detector de Conflito de Horario (issue #22).
 */
public class Solution {

    /**
     * Retorna todos os pares de disciplinas em conflito: mesmo dia da semana
     * e intervalos de horario que se sobrepoem (sobreposicao parcial conta
     * como conflito; uma disciplina terminar exatamente quando a outra
     * comeca NAO conta como conflito). Os pares devem ser retornados na
     * ordem em que aparecem ao comparar a lista de entrada da esquerda para
     * a direita (i antes de j, para todo i &lt; j).
     */
    public List<Conflito> detectarConflitos(List<Disciplina> disciplinas) {
        throw new UnsupportedOperationException();
    }

    public record Disciplina(String nome, String dia, int inicioMin, int fimMin) {
    }

    public record Conflito(String nomeA, String nomeB) {
    }
}
