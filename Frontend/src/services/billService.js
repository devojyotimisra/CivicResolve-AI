import { INITIAL_BILLS, INITIAL_BILL_TYPES } from "@/api/mockSeedData";

const BILLS_KEY = "civic_bills";
const BILL_TYPES_KEY = "civic_bill_types";

function getBillsFromStorage() {
  const data = localStorage.getItem(BILLS_KEY);
  if (!data) {
    localStorage.setItem(BILLS_KEY, JSON.stringify(INITIAL_BILLS));
    return INITIAL_BILLS;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_BILLS;
  }
}

function saveBillsToStorage(bills) {
  localStorage.setItem(BILLS_KEY, JSON.stringify(bills));
}

function getBillTypesFromStorage() {
  const data = localStorage.getItem(BILL_TYPES_KEY);
  if (!data) {
    localStorage.setItem(BILL_TYPES_KEY, JSON.stringify(INITIAL_BILL_TYPES));
    return INITIAL_BILL_TYPES;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_BILL_TYPES;
  }
}

function saveBillTypesToStorage(types) {
  localStorage.setItem(BILL_TYPES_KEY, JSON.stringify(types));
}

export const billService = {
  getUserBills: async (userId) => {
    await new Promise((res) => setTimeout(res, 300));
    const bills = getBillsFromStorage();
    return bills.filter((b) => b.userId === userId);
  },

  getAllBills: async (filters = {}) => {
    await new Promise((res) => setTimeout(res, 300));
    let bills = getBillsFromStorage();
    if (filters.status && filters.status !== "all") {
      bills = bills.filter((b) => b.status === filters.status);
    }
    if (filters.billType && filters.billType !== "all") {
      bills = bills.filter((b) => b.billType === filters.billType);
    }
    return bills.sort((a, b) => new Date(b.generatedAt) - new Date(a.generatedAt));
  },

  payBill: async (billId) => {
    await new Promise((res) => setTimeout(res, 800));
    const bills = getBillsFromStorage();
    const index = bills.findIndex((b) => b.id === billId || b.billNumber === billId);
    if (index === -1) throw new Error("Utility bill not found");

    const bill = bills[index];
    if (bill.status === "Paid") {
      throw new Error("This bill has already been paid.");
    }

    bill.status = "Paid";
    bill.paidAt = new Date().toISOString();
    bill.paymentRef = `TXN_ONLINE_${Math.floor(10000000 + Math.random() * 90000000)}`;

    bills[index] = bill;
    saveBillsToStorage(bills);
    return bill;
  },

  generateBill: async (billData) => {
    await new Promise((res) => setTimeout(res, 400));
    const bills = getBillsFromStorage();

    const newBill = {
      id: `bill_${Date.now()}`,
      billNumber: billData.billNumber || `BILL-2026-${Math.floor(1000 + Math.random() * 9000)}`,
      userId: billData.userId,
      citizenName: billData.citizenName,
      billType: billData.billType,
      amount: parseFloat(String(billData.amount).replace(/,/g, "")) || 0,
      dueDate: billData.dueDate,
      status: "Pending",
      period: billData.period || "Current Quarter Assessment",
      generatedAt: new Date().toISOString().split("T")[0]
    };

    bills.unshift(newBill);
    saveBillsToStorage(bills);
    return newBill;
  },

  getBillTypes: async () => {
    await new Promise((res) => setTimeout(res, 200));
    return getBillTypesFromStorage();
  },

  saveBillType: async (typeData) => {
    await new Promise((res) => setTimeout(res, 300));
    const types = getBillTypesFromStorage();

    if (typeData.id) {
      const index = types.findIndex((t) => t.id === typeData.id);
      if (index !== -1) {
        types[index] = { ...types[index], ...typeData };
        saveBillTypesToStorage(types);
        return types[index];
      }
    }

    const newType = {
      id: `bt_${Date.now()}`,
      ...typeData
    };

    types.push(newType);
    saveBillTypesToStorage(types);
    return newType;
  },

  deleteBillType: async (typeId) => {
    await new Promise((res) => setTimeout(res, 200));
    let types = getBillTypesFromStorage();
    const filtered = types.filter((t) => t.id !== typeId);
    if (filtered.length === types.length) {
      throw new Error("Bill type not found");
    }
    saveBillTypesToStorage(filtered);
    return true;
  }
};
