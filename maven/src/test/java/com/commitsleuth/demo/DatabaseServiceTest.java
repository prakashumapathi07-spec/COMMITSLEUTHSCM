package com.commitsleuth.demo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class DatabaseServiceTest {

    private DatabaseService db;

    @BeforeEach
    void setUp() {
        db = new DatabaseService();
    }

    @Test
    void testInitializeConnection() {
        db.initializeConnection("jdbc:sqlite:commitsleuth.db", "commitsleuth");
        assertTrue(db.isHealthy());
        assertEquals(3, db.getPoolSize());
    }

    @Test
    void testCloseCleansConnection() {
        db.initializeConnection("jdbc:sqlite:commitsleuth.db", "commitsleuth");
        db.close();
        assertFalse(db.isHealthy());
        assertEquals(0, db.getPoolSize());
    }

    @Test
    void testNullUrlThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            db.initializeConnection(null, "commitsleuth");
        });
    }
}
