package com.commitsleuth.demo;

import java.util.HashMap;
import java.util.Map;

/**
 * TechNova Solutions — Employee Management System
 * Module: Authentication & Session Security (feature/login)
 * Lead Developer: Bharathwaraj
 */
public class AuthService {

    private final Map<String, String> userCredentials = new HashMap<>();
    private final Map<String, String> activeSessions = new HashMap<>();

    public void registerUser(String username, String password) {
        if (username == null || username.length() < 3) {
            throw new IllegalArgumentException("Username must be at least 3 characters");
        }
        if (password == null || password.length() < 6) {
            throw new IllegalArgumentException("Password must be at least 6 characters");
        }
        userCredentials.put(username, password);
    }

    public boolean authenticate(String username, String password) {
        if (!userCredentials.containsKey(username)) {
            return false;
        }
        boolean valid = userCredentials.get(username).equals(password);
        if (valid) {
            activeSessions.put(username, "TOKEN-" + username.hashCode() + "-" + System.currentTimeMillis());
        }
        return valid;
    }

    public boolean isSessionActive(String username) {
        return activeSessions.containsKey(username);
    }

    public void logout(String username) {
        activeSessions.remove(username);
    }
}
