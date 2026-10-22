package com.commitsleuth.demo;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class EmployeeServiceTest {

    private EmployeeService service;

    @BeforeEach
    void setUp() {
        service = new EmployeeService();
    }

    @Test
    void testAddAndFindEmployee() {
        EmployeeService.Employee emp = new EmployeeService.Employee(101, "Arun Kumar", "Engineering", 75000.0);
        service.addEmployee(emp);
        assertEquals(1, service.getEmployeeCount());
        assertTrue(service.findById(101).isPresent());
        assertEquals("Arun Kumar", service.findById(101).get().getName());
    }

    @Test
    void testFindByDepartment() {
        service.addEmployee(new EmployeeService.Employee(101, "Prakash", "Engineering", 90000.0));
        service.addEmployee(new EmployeeService.Employee(102, "Divya", "Engineering", 85000.0));
        service.addEmployee(new EmployeeService.Employee(103, "Karthik", "Finance", 70000.0));

        List<EmployeeService.Employee> eng = service.findByDepartment("Engineering");
        assertEquals(2, eng.size());
    }

    @Test
    void testBlankNameThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            service.addEmployee(new EmployeeService.Employee(104, "", "Marketing", 50000.0));
        });
    }
}
