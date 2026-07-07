import { INITIAL_COMPLAINTS } from "@/api/mockSeedData";
import { authService } from "./authService";

const COMPLAINTS_KEY = "civic_complaints_v2";

function getComplaintsFromStorage() {
  const data = localStorage.getItem(COMPLAINTS_KEY);
  if (!data) {
    localStorage.setItem(COMPLAINTS_KEY, JSON.stringify(INITIAL_COMPLAINTS));
    return INITIAL_COMPLAINTS;
  }
  try {
    return JSON.parse(data);
  } catch (e) {
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
        (c) => c.title.toLowerCase().includes(q) || c.token.toLowerCase().includes(q) || c.location.toLowerCase().includes(q)
      );
    }

    // Sort by latest submitted
    return complaints.sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));
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

    // Generate random 12 char token (e.g., CRA-8X9Y2Z)
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
      submittedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      submittedPhoto: complaintData.submittedPhoto || "",
      assignedOfficerId: null,
      assignedOfficerName: null,
      department: "Pending Classification",
      citizenId: null,
      timeline: [
        {
          status: "Submitted",
          timestamp: new Date().toISOString(),
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
    complaint.status = newStatus;
    complaint.updatedAt = new Date().toISOString();

    if (resolutionPhoto) {
      complaint.resolutionPhoto = resolutionPhoto;
    }
    if (resolutionNote) {
      complaint.resolutionNote = resolutionNote;
    }

    const timelineItem = {
      status: newStatus,
      timestamp: new Date().toISOString()
    };
    if (note) {
      timelineItem.note = note;
    }
    complaint.timeline.push(timelineItem);

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
    complaint.assignedOfficerId = officerId;
    complaint.assignedOfficerName = officerName;
    if (complaint.status === "Submitted") {
      complaint.status = "Assigned";
    }
    complaint.updatedAt = new Date().toISOString();
    complaint.timeline.push({
      status: "Assigned",
      timestamp: new Date().toISOString(),
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
