package katas.k02;

import katas.k02.Solution.Categoria;
import katas.k02.Solution.Item;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Testes de aceitacao do K02 (issue #22). Nao alterar durante o trial.
 */
class SolutionTest {

    private final Solution solution = new Solution();
    private static final double DELTA = 0.001;

    @Test
    void umComboCompletoAplicaDescontoNoItemMaisBarato() {
        List<Item> itens = List.of(
            new Item("Prato feito", Categoria.PRINCIPAL, 10.0),
            new Item("Suco", Categoria.BEBIDA, 6.0)
        );

        double total = solution.calcularTotal(itens, 0.20);

        assertEquals(14.8, total, DELTA);
    }

    @Test
    void principalSemParFicaComValorCheio() {
        List<Item> itens = List.of(
            new Item("Prato feito", Categoria.PRINCIPAL, 12.0),
            new Item("Marmita", Categoria.PRINCIPAL, 8.0),
            new Item("Suco", Categoria.BEBIDA, 5.0)
        );

        double total = solution.calcularTotal(itens, 0.20);

        assertEquals(24.0, total, DELTA);
    }

    @Test
    void semBebidaNaoAplicaDesconto() {
        List<Item> itens = List.of(
            new Item("Prato feito", Categoria.PRINCIPAL, 10.0),
            new Item("Marmita", Categoria.PRINCIPAL, 8.0)
        );

        double total = solution.calcularTotal(itens, 0.20);

        assertEquals(18.0, total, DELTA);
    }

    @Test
    void doisCombosParelhamMaioresComMaiores() {
        List<Item> itens = List.of(
            new Item("Prato feito", Categoria.PRINCIPAL, 15.0),
            new Item("Marmita", Categoria.PRINCIPAL, 9.0),
            new Item("Suco grande", Categoria.BEBIDA, 10.0),
            new Item("Suco pequeno", Categoria.BEBIDA, 4.0)
        );

        double total = solution.calcularTotal(itens, 0.20);

        assertEquals(35.2, total, DELTA);
    }

    @Test
    void pedidoVazioRetornaZero() {
        double total = solution.calcularTotal(List.of(), 0.20);

        assertEquals(0.0, total, DELTA);
    }
}
