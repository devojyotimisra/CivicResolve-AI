import client from "@/api/client";
import { authService } from "./authService";

export const billService = {
  getUserBills: async (userId) => {
    try {
      const response = await client.get("/citizen/bills");
      return response.data.bills || [];
    } catch (error) {
      console.error("Error fetching user bills:", error);
      throw error;
    }
  },

  getAllBills: async (filters = {}) => {
    try {
      const session = authService.getCurrentSession();
      if (!session) throw new Error("No active session");

      let endpoint = "";
      if (session.user.role === "citizen") endpoint = "/citizen/bills";
      else if (session.user.role === "commissioner") endpoint = "/commissioner/bills";
      else endpoint = "/citizen/bills";

      const response = await client.get(endpoint, { params: filters });
      return response.data.bills || [];
    } catch (error) {
      console.error("Error fetching all bills:", error);
      throw error;
    }
  },

  payBill: async (billId) => {
    try {
      const response = await client.post(`/citizen/pay_bill/${billId}`);
      return response.data.bill;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to pay bill.");
    }
  },

  generateBill: async (billData) => {
    try {
      const response = await client.post("/commissioner/bill", billData);
      return response.data.bill;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to generate bill.");
    }
  },

  getBillTypes: async () => {
    try {

      const response = await client.get("/commissioner/bill_types").catch(() => ({ data: [] }));
      return response.data;
    } catch (error) {
      return [];
    }
  },

  saveBillType: async (typeData) => {
    try {
      if (typeData.id) {
        const response = await client.put(`/commissioner/bill_type/${typeData.id}`, typeData);
        return response.data;
      } else {
        const response = await client.post("/commissioner/bill_type", typeData);
        return response.data;
      }
    } catch (error) {
      throw new Error("Failed to save bill type.");
    }
  },

  deleteBillType: async (typeId) => {
    try {
      await client.delete(`/commissioner/bill_type/${typeId}`);
      return true;
    } catch (error) {
      throw new Error("Failed to delete bill type.");
    }
  }
};
