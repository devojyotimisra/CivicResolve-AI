import client from "@/api/client";
import { authService } from "./authService";

export const adminService = {
  getOfficers: async () => {
    try {
      const response = await client.get("/commissioner/officers");
      return response.data.officers;
    } catch (error) {
      console.error("Error fetching officers:", error);
      throw error;
    }
  },

  provisionOfficer: async (officerData) => {
    try {
      const response = await client.post("/commissioner/officer", officerData);
      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to provision officer.");
    }
  },

  updateOfficer: async (officerId, officerData) => {
    try {
      const response = await client.put(`/commissioner/officer/${officerId}`, officerData);
      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to update officer.");
    }
  },

  deactivateOfficer: async (officerId) => {
    try {
      const response = await client.delete(`/commissioner/officer/${officerId}`);
      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to deactivate officer.");
    }
  },

  deleteOfficer: async (officerId) => {

    return await adminService.deactivateOfficer(officerId);
  },

  getCitizens: async () => {
    try {
      const response = await client.get("/commissioner/citizens");
      return response.data.citizens;
    } catch (error) {
      console.error("Error fetching citizens:", error);
      throw error;
    }
  },

  getDepartments: async () => {
    try {

      const response = await client.get("/commissioner/categories").catch(() => ({ data: { categories: [] } }));
      return response.data.categories;
    } catch (error) {
      return [];
    }
  },

  saveDepartment: async (departmentData) => {
    try {
      if (departmentData.id) {

        const response = await client.post("/commissioner/category", departmentData);
        return response.data;
      } else {
        const response = await client.post("/commissioner/category", departmentData);
        return response.data;
      }
    } catch (error) {
      throw new Error("Failed to save department/category.");
    }
  },

  deleteDepartment: async (departmentId) => {
    try {
      await client.delete(`/commissioner/category/${departmentId}`);
      return true;
    } catch (error) {
      throw new Error("Failed to delete department.");
    }
  },

  getDashboardStats: async () => {
    try {
      const response = await client.get("/commissioner/dash");
      const data = response.data;
      return {
        totalComplaints: data.totalComplaints ?? data.total_complaints ?? 0,
        pendingComplaints: data.pendingComplaints ?? data.pending_complaints ?? 0,
        resolvedComplaints: data.resolvedComplaints ?? data.resolved_complaints ?? 0,
        closedComplaints: data.closedComplaints ?? data.closed_complaints ?? 0,
        criticalComplaints: data.criticalComplaints ?? data.critical_complaints ?? 0,
        totalOfficers: data.totalOfficers ?? data.total_officers ?? 0,
        totalCitizens: data.totalCitizens ?? data.total_citizens ?? 0,
        totalRevenue: data.totalRevenue ?? data.total_revenue ?? 0,
        billRevenue: data.billRevenue ?? data.bill_revenue ?? 0,
        bookingRevenue: data.bookingRevenue ?? data.booking_revenue ?? 0,
        byDepartment: data.complaintsByCategory ?? data.complaints_by_category ?? [],
        byStatus: data.complaintsByStatus ?? data.complaints_by_status ?? [],
        trend: []
      };
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      throw error;
    }
  },

  getSystemAnalytics: async () => {
    try {
      const response = await client.get("/commissioner/dash");
      const data = response.data;
      return {
        totalComplaints: data.totalComplaints ?? data.total_complaints ?? 0,
        pendingComplaints: data.pendingComplaints ?? data.pending_complaints ?? 0,
        resolvedComplaints: data.resolvedComplaints ?? data.resolved_complaints ?? 0,
        closedComplaints: data.closedComplaints ?? data.closed_complaints ?? 0,
        criticalComplaints: data.criticalComplaints ?? data.critical_complaints ?? 0,
        totalOfficers: data.totalOfficers ?? data.total_officers ?? 0,
        totalCitizens: data.totalCitizens ?? data.total_citizens ?? 0,
        totalRevenue: data.totalRevenue ?? data.total_revenue ?? 0,
        billRevenue: data.billRevenue ?? data.bill_revenue ?? 0,
        bookingRevenue: data.bookingRevenue ?? data.booking_revenue ?? 0,
        byDepartment: data.complaintsByCategory ?? data.complaints_by_category ?? [],
        byStatus: data.complaintsByStatus ?? data.complaints_by_status ?? [],
        trend: []
      };
    } catch (error) {
      console.error("Error fetching system analytics:", error);
      throw error;
    }
  },

  globalSearch: async (query) => {
    try {
      const session = authService.getCurrentSession();
      if (!session) return { complaints: [], bills: [], bookings: [], users: [] };

      let endpoint = "";
      if (session.user.role === "citizen") endpoint = "/citizen/search";
      else if (session.user.role === "commissioner") endpoint = "/commissioner/search";
      else if (session.user.role === "field_officer") endpoint = "/officer/search";

      const response = await client.post(endpoint, { query });
      return response.data;
    } catch (error) {
      console.error("Error performing search:", error);
      return { complaints: [], bills: [], bookings: [], users: [] };
    }
  }
};
