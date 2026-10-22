package com.commitsleuth.demo;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

class ValidatorTest {
    private final Validator v = new Validator();
    @Test void positiveNumber() { assertTrue(v.isPositive(5)); }
    @Test void evenNumber() { assertTrue(v.isEven(4)); }
    @Test void rangeCheck() { assertTrue(v.isInRange(5, 1, 10)); assertFalse(v.isInRange(15, 1, 10)); }
}
