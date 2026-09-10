package katas.k02;

import java.util.List;

/**
 * K02 - Calculo de Desconto por Combo (issue #22).
 */
public class Solution {

    /**
     * Calcula o valor total do pedido aplicando o desconto de combo: cada vez
     * que for possivel formar um par (um item da categoria "principal" com um
     * item da categoria "bebida") ainda nao usado em outro combo, aplica-se
     * {@code percentualDesconto} sobre o valor do item mais barato do par.
     * Itens sem par formado sao cobrados pelo valor cheio. A formacao de
     * pares deve priorizar sempre o principal mais caro disponivel com a
     * bebida mais cara disponivel, para maximizar o valor descontado.
     *
     * @param itens              itens do pedido
     * @param percentualDesconto percentual de desconto, ex.: 0.20 para 20%
     */
    public double calcularTotal(List<Item> itens, double percentualDesconto) {
        throw new UnsupportedOperationException();
    }

    public record Item(String nome, Categoria categoria, double valor) {
    }

    public enum Categoria {
        PRINCIPAL, BEBIDA
    }
}
