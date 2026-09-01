import client from "@/api/client";
import { authService } from "./authService";

export const complaintService = {
    getAllComplaints: async (filters = {}) => {
        try {
            const session = authService.getCurrentSession();
            if (!session) throw new Error("No active session");

            let endpoint = "";
            if (session.user.role === "citizen") {
                return [];
            } else if (session.user.role === "commissioner") {
                endpoint = "/commissioner/complaints";
            } else if (session.user.role === "officer") {
                endpoint = "/officer/history";
            }

            const response = await client.get(endpoint, { params: filters });
            return response.data.complaints || response.data.history || response.data.tickets || [];
        } catch (error) {
            console.error("Error fetching complaints:", error);
            throw error;
        }
    },

    getComplaintByToken: async (token) => {
        try {
            const response = await client.get(`/complaint/track/${token}`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error(
                "No civic report found matching this token. Please check the token code."
            );
        }
    },

    fileAnonymousComplaint: async (complaintData) => {
        try {
            const formData = new FormData();
            formData.append("title", complaintData.title);
            formData.append("description", complaintData.description || "");

            if (complaintData.location) {
                formData.append("addressText", complaintData.location);
            }
            if (complaintData.addressText) {
                formData.append("addressText", complaintData.addressText);
            }
            if (complaintData.categoryId) {
                formData.append("categoryId", complaintData.categoryId);
            }

            if (complaintData.photoFile) {
                formData.append("photo", complaintData.photoFile);
            }

            const response = await client.post("/complaint/anonymous", formData);
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to submit anonymous complaint.");
        }
    },

    updateComplaintStatus: async (
        complaintId,
        newStatus,
        note,
        _officerId = null,
        resolutionFile = null,
        resolutionNote = null
    ) => {
        try {
            if (newStatus === "Resolved") {
                const formData = new FormData();
                formData.append("resolution_note", resolutionNote || note);
                if (resolutionFile) {
                    formData.append("resolution_photo", resolutionFile);
                }
                const response = await client.post(
                    `/officer/ticket/${complaintId}/resolve`,
                    formData
                );
                return response.data;
            } else {
                const response = await client.put(`/officer/ticket/${complaintId}/status`, {
                    status: newStatus,
                    note: note,
                });
                return response.data;
            }
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            if (error.response && error.response.data && error.response.data.error) {
                throw new Error(error.response.data.error);
            }
            throw new Error("Failed to update complaint status.");
        }
    },

    assignOfficer: async (complaintId, officerId, _officerName) => {
        try {
            const response = await client.put(`/commissioner/assign/${complaintId}`, {
                officerId: officerId,
            });
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            if (error.response && error.response.data && error.response.data.error) {
                throw new Error(error.response.data.error);
            }
            throw new Error("Failed to assign officer.");
        }
    },

    getComplaintDetail: async (complaintId) => {
        try {
            const session = authService.getCurrentSession();
            if (!session) throw new Error("No active session");

            let endpoint = "";
            if (session.user.role === "commissioner") {
                endpoint = `/commissioner/complaint/${complaintId}`;
            } else if (session.user.role === "officer") {
                endpoint = `/officer/ticket/${complaintId}`;
            } else {
                throw new Error("Not authorized to view complaint details");
            }

            const response = await client.get(endpoint);
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to fetch complaint details.");
        }
    },

    markAsSpam: async (complaintId) => {
        try {
            const response = await client.put(`/commissioner/complaint/${complaintId}/spam`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to mark ticket as spam.");
        }
    },

    respondToResolution: async (token, accept, note) => {
        try {
            const response = await client.put(`/complaint/track/${token}/resolution`, {
                accept,
                note,
            });
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to submit resolution response.");
        }
    },

    getOfficerComplaints: async (_officerId) => {
        try {
            const response = await client.get("/officer/history");
            return response.data.history || [];
        } catch (error) {
            console.error("Error fetching officer complaints:", error);
            throw error;
        }
    },
};
