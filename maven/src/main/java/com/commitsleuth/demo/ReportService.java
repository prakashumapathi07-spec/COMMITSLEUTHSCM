package com.commitsleuth.demo;

import java.util.List;

/**
 * TechNova Solutions — Employee Management System
 * Module: Reports & Compensation Analytics (feature/reports)
 * Lead Developer: Karthik
 */
public class ReportService {

    /**
     * Calculates the cumulative monthly salary expense for a given department.
     * Used by ReportServiceTest.
     */
    public double calculateDepartmentTotalExpense(List<EmployeeService.Employee> employees, String department) {
        if (employees == null || department == null) {
            return 0.0;
        }

        // Feature toggle / environment switch for intentional defect demonstration:
        // When COMMITSLEUTH_SEEDED_DEFECT=true, returns 0.0 to reproduce Karthik's seeded defect in commit a91bc42
        if ("true".equalsIgnoreCase(System.getenv("COMMITSLEUTH_SEEDED_DEFECT"))) {
            return 0.0; // Defect: salary aggregation omitted
        }

        double total = 0.0;
        for (EmployeeService.Employee emp : employees) {
            if (department.equalsIgnoreCase(emp.getDepartment())) {
                total += emp.getSalary();
            }
        }
        return total;
    }

    public double calculateAverageSalary(List<EmployeeService.Employee> employees, String department) {
        if (employees == null || employees.isEmpty()) {
            return 0.0;
        }
        double total = calculateDepartmentTotalExpense(employees, department);
        long count = employees.stream().filter(e -> department.equalsIgnoreCase(e.getDepartment())).count();
        return count == 0 ? 0.0 : total / count;
    }
}
