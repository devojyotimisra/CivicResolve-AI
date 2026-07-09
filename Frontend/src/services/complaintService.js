import { INITIAL_COMPLAINTS } from "@/api/mockSeedData";

const COMPLAINTS_KEY = "civic_complaints";

function getComplaintsFromStorage() {
  const data = localStorage.getItem(COMPLAINTS_KEY);
  if (!data) {
    localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(INITIAL_COMPLAINTS));
    return INITIAL_COMPLAINTS;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_COMPLAINTS;
  }
}

function saveComplaintsToStorage(complaints) {
  localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(complaints));
}

export const complaintService = {
  getAllComplaints: async (filters = {}) => {
    await new Promise((res) => setTimeout(res, 300));
    let complaints = getComplaintsFromStorage();

    if (filters.department && filters.department !== "all") {
      complaints = complaints.filter((c) => c.department === filters.department);
    }
    if (filters.status && filters.status !== "all") {
      complaints = complaints.filter((c) => c.status === filters.status);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      complaints = complaints.filter(
        (c) => c.title?.toLowerCase().includes(q) || c.token?.toLowerCase().includes(q) || c.location?.toLowerCase().includes(q)
      );
    }

    return complaints.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  },

  getComplaintByToken: async (token) => {
    await new Promise((res) => setTimeout(res, 250));
    const complaints = getComplaintsFromStorage();
    const found = complaints.find((c) => c.token?.toUpperCase() === token?.trim().toUpperCase());
    if (!found) {
      throw new Error("No civic report found matching this 12-character tracking token. Please check the token code.");
    }
    return found;
  },

  fileAnonymousComplaint: async (complaintData) => {
    await new Promise((res) => setTimeout(res, 600));
    const complaints = getComplaintsFromStorage();

    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let randomPart = "";
    for (let i = 0; i < 6; i++) {
      randomPart += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    const token = `CRA-${randomPart}`;

    const newComplaint = {
      id: `comp_${Date.now()}`,
      token: token,
      title: complaintData.title,
      status: "Submitted",
      description: complaintData.description,
      location: complaintData.location,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      submittedPhoto: complaintData.submittedPhoto || "",
      assignedOfficerId: null,
      assignedOfficerName: null,
      department: "Pending Classification",
      updates: [
        {
          newStatus: "Submitted",
          oldStatus: null,
          updatedById: null,
          updatedByName: "Public Portal",
          createdAt: new Date().toISOString(),
          note: "Report filed via public portal"
        }
      ]
    };

    complaints.unshift(newComplaint);
    saveComplaintsToStorage(complaints);

    return newComplaint;
  },

  updateComplaintStatus: async (complaintId, newStatus, note, officerId = null, resolutionPhoto = null, resolutionNote = null) => {
    await new Promise((res) => setTimeout(res, 400));
    const complaints = getComplaintsFromStorage();
    const index = complaints.findIndex((c) => c.id === complaintId || c.token === complaintId);
    if (index === -1) throw new Error("Complaint not found");

    const complaint = complaints[index];
    const oldStatus = complaint.status;
    complaint.status = newStatus;
    complaint.updatedAt = new Date().toISOString();
    if (newStatus === "Resolved") {
      complaint.resolvedAt = new Date().toISOString();
    }
    if (newStatus === "Closed") {
      complaint.closedAt = new Date().toISOString();
    }

    if (resolutionPhoto) {
      complaint.resolutionPhoto = resolutionPhoto;
    }
    if (resolutionNote) {
      complaint.resolutionNote = resolutionNote;
    }

    const updateItem = {
      newStatus: newStatus,
      oldStatus: oldStatus,
      updatedById: officerId,
      updatedByName: complaint.assignedOfficerName || "Assigned Officer",
      createdAt: new Date().toISOString(),
      note: note || `Status updated to ${newStatus}`
    };
    if (!complaint.updates) complaint.updates = [];
    complaint.updates.push(updateItem);

    complaints[index] = complaint;
    saveComplaintsToStorage(complaints);
    return complaint;
  },

  assignOfficer: async (complaintId, officerId, officerName) => {
    await new Promise((res) => setTimeout(res, 350));
    const complaints = getComplaintsFromStorage();
    const index = complaints.findIndex((c) => c.id === complaintId || c.token === complaintId);
    if (index === -1) throw new Error("Complaint not found");

    const complaint = complaints[index];
    const oldStatus = complaint.status;
    complaint.assignedOfficerId = officerId;
    complaint.assignedOfficerName = officerName;
    if (complaint.status === "Submitted") {
      complaint.status = "Assigned";
    }
    complaint.updatedAt = new Date().toISOString();
    if (!complaint.updates) complaint.updates = [];
    complaint.updates.push({
      newStatus: complaint.status,
      oldStatus: oldStatus,
      updatedById: officerId,
      updatedByName: officerName,
      createdAt: new Date().toISOString(),
      note: `Assigned to Field Officer ${officerName}`
    });

    complaints[index] = complaint;
    saveComplaintsToStorage(complaints);
    return complaint;
  },

  getOfficerComplaints: async (officerId) => {
    await new Promise((res) => setTimeout(res, 300));
    const allComplaints = getComplaintsFromStorage();
    return allComplaints.filter((c) => c.assignedOfficerId === officerId);
  }
};
