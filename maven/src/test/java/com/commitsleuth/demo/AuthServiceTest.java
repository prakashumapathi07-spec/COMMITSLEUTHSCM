package com.commitsleuth.demo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AuthServiceTest {

    private AuthService auth;

    @BeforeEach
    void setUp() {
        auth = new AuthService();
        auth.registerUser("prakash", "securePass123");
        auth.registerUser("karthik", "reportSecret789");
    }

    @Test
    void testSuccessfulAuthentication() {
        assertTrue(auth.authenticate("prakash", "securePass123"));
        assertTrue(auth.isSessionActive("prakash"));
    }

    @Test
    void testInvalidPasswordFails() {
        assertFalse(auth.authenticate("prakash", "wrongPassword"));
        assertFalse(auth.isSessionActive("prakash"));
    }

    @Test
    void testLogoutClearsSession() {
        auth.authenticate("karthik", "reportSecret789");
        assertTrue(auth.isSessionActive("karthik"));
        auth.logout("karthik");
        assertFalse(auth.isSessionActive("karthik"));
    }
}
