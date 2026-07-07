import { INITIAL_BILLS } from "@/api/mockSeedData";

const BILLS_KEY = "civic_bills";

function getBillsFromStorage() {
  const data = localStorage.getItem(BILLS_KEY);
  if (!data) {
    localStorage.setItem(BILLS_KEY, JSON.stringify(INITIAL_BILLS));
    return INITIAL_BILLS;
  }
  try {
    return JSON.parse(data);
  } catch (e) {
    return INITIAL_BILLS;
  }
}

function saveBillsToStorage(bills) {
  localStorage.setItem(BILLS_KEY, JSON.stringify(bills));
}

export const billService = {
  getUserBills: async (citizenId) => {
    await new Promise((res) => setTimeout(res, 300));
    const bills = getBillsFromStorage();
    return bills.filter((b) => b.citizenId === citizenId);
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
      citizenId: billData.citizenId,
      citizenName: billData.citizenName,
      billType: billData.billType,
      amount: Number(billData.amount),
      dueDate: billData.dueDate,
      status: "Pending",
      period: billData.period || "Current Quarter Assessment",
      generatedAt: new Date().toISOString().split("T")[0]
    };

    bills.unshift(newBill);
    saveBillsToStorage(bills);
    return newBill;
  }
};
