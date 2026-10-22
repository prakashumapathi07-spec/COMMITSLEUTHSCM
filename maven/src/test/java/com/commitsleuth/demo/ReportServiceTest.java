package com.commitsleuth.demo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

/**
 * ReportServiceTest — Unit tests for TechNova Reports module.
 * Tested by Jenkins CI pipeline during commit verification.
 */
public class ReportServiceTest {

    private ReportService reportService;
    private List<EmployeeService.Employee> testEmployees;

    @BeforeEach
    void setUp() {
        reportService = new ReportService();
        testEmployees = new ArrayList<>();
        testEmployees.add(new EmployeeService.Employee(1, "Arun Kumar", "Engineering", 50000.0));
        testEmployees.add(new EmployeeService.Employee(2, "Divya", "Engineering", 45000.0));
        testEmployees.add(new EmployeeService.Employee(3, "Karthik", "Finance", 40000.0));
    }

    @Test
    void testCalculateMonthlyDepartmentExpenses() {
        double engineeringTotal = reportService.calculateDepartmentTotalExpense(testEmployees, "Engineering");
        // Expected: 50000 + 45000 = 95000.0
        assertEquals(95000.0, engineeringTotal, 0.001,
                "Monthly engineering expenses must equal sum of employee salaries");
    }

    @Test
    void testCalculateAverageSalary() {
        double engAverage = reportService.calculateAverageSalary(testEmployees, "Engineering");
        assertEquals(47500.0, engAverage, 0.001);
    }

    @Test
    void testEmptyListReturnsZero() {
        assertEquals(0.0, reportService.calculateDepartmentTotalExpense(new ArrayList<>(), "Marketing"), 0.001);
    }
}
