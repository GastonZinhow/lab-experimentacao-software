package katas.k03;

public class Solution {
    public int rob(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        if (nums.length == 1) {
            return nums[0];
        }
        int casa_anterior = 0;
        int anterior_as_duas_casas = 0;
        for (int i = 0; i < nums.length; i++) {
            int atual = Math.max(casa_anterior, anterior_as_duas_casas +
                    nums[i]);
            anterior_as_duas_casas = casa_anterior;
            casa_anterior = atual;
        }
        return casa_anterior;
    }
}