package com.commitsleuth.demo;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * TechNova Solutions — Employee Management System
 * Module: Employee Management (feature/employee)
 * Lead Developer: Prakash Raj
 */
public class EmployeeService {

    public static class Employee {
        private final int id;
        private final String name;
        private final String department;
        private final double salary;

        public Employee(int id, String name, String department, double salary) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
        }

        public int getId() { return id; }
        public String getName() { return name; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }
    }

    private final List<Employee> employees = new ArrayList<>();

    public void addEmployee(Employee emp) {
        if (emp == null || emp.getName() == null || emp.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("Employee name cannot be blank");
        }
        employees.add(emp);
    }

    public Optional<Employee> findById(int id) {
        return employees.stream().filter(e -> e.getId() == id).findFirst();
    }

    public List<Employee> findByDepartment(String dept) {
        return employees.stream()
                .filter(e -> e.getDepartment().equalsIgnoreCase(dept))
                .toList();
    }

    public int getEmployeeCount() {
        return employees.size();
    }
}
