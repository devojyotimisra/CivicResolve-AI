import { INITIAL_DEPARTMENTS } from "@/api/mockSeedData";
import { authService } from "./authService";
import { complaintService } from "./complaintService";
import { billService } from "./billService";
import { facilityService } from "./facilityService";

const DEPARTMENTS_KEY = "civic_departments";

function getDepartmentsFromStorage() {
  const data = localStorage.getItem(DEPARTMENTS_KEY);
  if (!data) {
    localStorage.setItem(DEPARTMENTS_KEY, JSON.stringify(INITIAL_DEPARTMENTS));
    return INITIAL_DEPARTMENTS;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_DEPARTMENTS;
  }
}

function saveDepartmentsToStorage(departments) {
  localStorage.setItem(DEPARTMENTS_KEY, JSON.stringify(departments));
}

export const adminService = {
  getOfficers: async () => {
    await new Promise((res) => setTimeout(res, 300));
    const users = authService.getUsers();
    return users.filter((u) => u.role === "officer");
  },

  provisionOfficer: async (officerData) => {
    await new Promise((res) => setTimeout(res, 500));
    const users = authService.getUsers();

    if (users.some((u) => u.email?.toLowerCase() === officerData.email?.toLowerCase())) {
      throw new Error("An account with this email address already exists.");
    }
    if (users.some((u) => u.badgeId?.toLowerCase() === officerData.badgeId?.toLowerCase())) {
      throw new Error("An officer with this Badge ID already exists.");
    }

    const newOfficer = {
      id: `usr_officer_${Date.now()}`,
      role: "officer",
      isActive: true,
      ...officerData
    };

    users.push(newOfficer);
    localStorage.setItem("civic_users", JSON.stringify(users));
    return newOfficer;
  },

  updateOfficer: async (officerId, officerData) => {
    await new Promise((res) => setTimeout(res, 400));
    const users = authService.getUsers();
    const index = users.findIndex((u) => u.id === officerId);
    if (index === -1) throw new Error("Officer not found");

    if (
      officerData.email &&
      users.some((u) => u.email?.toLowerCase() === officerData.email?.toLowerCase() && u.id !== officerId)
    ) {
      throw new Error("An account with this email address already exists.");
    }

    if (
      officerData.badgeId &&
      users.some((u) => u.badgeId?.toLowerCase() === officerData.badgeId?.toLowerCase() && u.id !== officerId)
    ) {
      throw new Error("An officer with this Badge ID already exists.");
    }

    users[index] = { ...users[index], ...officerData };
    localStorage.setItem("civic_users", JSON.stringify(users));
    return users[index];
  },

  deactivateOfficer: async (officerId) => {
    await new Promise((res) => setTimeout(res, 300));
    const users = authService.getUsers();
    const index = users.findIndex((u) => u.id === officerId);
    if (index === -1) throw new Error("Officer not found");

    users[index].isActive = !users[index].isActive;
    localStorage.setItem("civic_users", JSON.stringify(users));
    return users[index];
  },

  deleteOfficer: async (officerId) => {
    await new Promise((res) => setTimeout(res, 300));
    const users = authService.getUsers();
    const index = users.findIndex((u) => u.id === officerId);
    if (index === -1) throw new Error("Officer not found");

    users.splice(index, 1);
    localStorage.setItem("civic_users", JSON.stringify(users));
    return true;
  },

  getCitizens: async () => {
    await new Promise((res) => setTimeout(res, 300));
    const users = authService.getUsers();
    return users.filter((u) => u.role === "citizen");
  },

  getDepartments: async () => {
    await new Promise((res) => setTimeout(res, 200));
    return getDepartmentsFromStorage();
  },

  saveDepartment: async (departmentData) => {
    await new Promise((res) => setTimeout(res, 300));
    const departments = getDepartmentsFromStorage();

    if (departmentData.id) {
      const index = departments.findIndex((c) => c.id === departmentData.id);
      if (index !== -1) {
        departments[index] = { ...departments[index], ...departmentData };
        saveDepartmentsToStorage(departments);
        return departments[index];
      }
    }

    const newDept = {
      id: `dept_${Date.now()}`,
      ...departmentData
    };

    departments.push(newDept);
    saveDepartmentsToStorage(departments);
    return newDept;
  },

  deleteDepartment: async (departmentId) => {
    await new Promise((res) => setTimeout(res, 200));
    let departments = getDepartmentsFromStorage();
    const filtered = departments.filter((d) => d.id !== departmentId);
    if (filtered.length === departments.length) {
      throw new Error("Department not found");
    }
    saveDepartmentsToStorage(filtered);
    return true;
  },

  getDashboardStats: async () => {
    await new Promise((res) => setTimeout(res, 350));
    const complaints = await complaintService.getAllComplaints();
    const officers = await adminService.getOfficers();

    const totalComplaints = complaints.length;
    const activeComplaints = complaints.filter(
      (c) => c.status !== "Resolved" && c.status !== "Closed"
    ).length;
    const resolvedComplaints = totalComplaints - activeComplaints;
    const criticalComplaints = complaints.filter(
      (c) => (c.severity === "Critical" || c.severity?.toLowerCase() === "critical") && c.status !== "Resolved" && c.status !== "Closed"
    ).length;

    const deptCounts = {};
    complaints.forEach((c) => {
      const dept = c.department || "Other";
      deptCounts[dept] = (deptCounts[dept] || 0) + 1;
    });
    const departmentBreakdown = Object.keys(deptCounts).map((name) => ({
      name,
      count: deptCounts[name]
    }));

    const recentComplaints = [...complaints]
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 20);

    return {
      totalComplaints,
      activeComplaints,
      resolvedComplaints,
      criticalComplaints,

      totalOfficers: officers.length,
      departmentBreakdown,
      recentComplaints
    };
  },

  getSystemAnalytics: async () => {
    await new Promise((res) => setTimeout(res, 400));
    const complaints = await complaintService.getAllComplaints();
    const bills = await billService.getAllBills();
    const bookings = await facilityService.getAllBookings();
    const officers = await adminService.getOfficers();

    const totalComplaints = complaints.length;
    const resolvedComplaints = complaints.filter((c) => c.status === "Resolved" || c.status === "Closed").length;
    const criticalComplaints = complaints.filter(
      (c) => (c.severity === "Critical" || c.severity?.toLowerCase() === "critical") && c.status !== "Resolved" && c.status !== "Closed"
    ).length;
    const resolutionRate = totalComplaints > 0 ? Math.round((resolvedComplaints / totalComplaints) * 100) : 0;

    const billRevenue = bills.filter((b) => b.status === "Paid").reduce((sum, b) => sum + (b.amount || 0), 0);
    const bookingRevenue = bookings.filter((b) => b.status === "Confirmed" || b.status === "Completed").reduce((sum, b) => sum + (b.amountPaid || 0), 0);
    const totalRevenue = billRevenue + bookingRevenue;

    const departmentCounts = {};
    complaints.forEach((c) => {
      departmentCounts[c.department] = (departmentCounts[c.department] || 0) + 1;
    });
    const byDepartment = Object.keys(departmentCounts).map((dept) => ({
      name: dept,
      count: departmentCounts[dept]
    }));

    const statusCounts = {};
    complaints.forEach((c) => {
      statusCounts[c.status] = (statusCounts[c.status] || 0) + 1;
    });
    const byStatus = Object.keys(statusCounts).map((status) => ({
      name: status,
      value: statusCounts[status]
    }));

    const trend = [
      { day: "Mon", filed: 12, resolved: 10 },
      { day: "Tue", filed: 19, resolved: 15 },
      { day: "Wed", filed: 15, resolved: 18 },
      { day: "Thu", filed: 22, resolved: 20 },
      { day: "Fri", filed: 28, resolved: 25 },
      { day: "Sat", filed: 14, resolved: 16 },
      { day: "Sun", filed: 8, resolved: 12 },
    ];

    return {
      totalComplaints,
      resolvedComplaints,
      criticalComplaints,
      resolutionRate,
      avgResolutionDays: 2.4,
      totalRevenue,
      billRevenue,
      bookingRevenue,
      totalOfficers: officers.length,
      byDepartment,
      byStatus,
      trend
    };
  },

  globalSearch: async (query) => {
    await new Promise((res) => setTimeout(res, 350));
    if (!query || query.trim() === "") return { complaints: [], bills: [], bookings: [], users: [] };

    const q = query.toLowerCase().trim();
    const complaints = await complaintService.getAllComplaints();
    const bills = await billService.getAllBills();
    const bookings = await facilityService.getAllBookings();
    const users = authService.getUsers();

    return {
      complaints: complaints.filter((c) => c.title.toLowerCase().includes(q) || c.token.toLowerCase().includes(q) || c.location.toLowerCase().includes(q)),
      bills: bills.filter((b) => b.billNumber.toLowerCase().includes(q) || b.citizenName?.toLowerCase().includes(q) || b.billType.toLowerCase().includes(q)),
      bookings: bookings.filter((b) => b.bookingReference.toLowerCase().includes(q) || b.facilityName.toLowerCase().includes(q) || b.citizenName?.toLowerCase().includes(q)),
      users: users.filter((u) => u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q) || u.badgeId?.toLowerCase().includes(q))
    };
  }
};
