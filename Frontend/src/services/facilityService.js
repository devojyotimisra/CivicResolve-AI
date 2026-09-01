import client from "@/api/client";
import { authService } from "./authService";

export const facilityService = {
    getAllFacilities: async (type = "all") => {
        try {
            const session = authService.getCurrentSession();
            if (!session) throw new Error("No active session");

            let endpoint = "";
            if (session.user.role === "citizen") endpoint = "/citizen/facilities";
            else if (session.user.role === "commissioner") endpoint = "/commissioner/facilities";
            else endpoint = "/citizen/facilities";

            const response = await client.get(endpoint, {
                params: { type: type !== "all" ? type : undefined },
            });
            return response.data.facilities || [];
        } catch (error) {
            console.error("Error fetching facilities:", error);
            throw error;
        }
    },

    getFacilityById: async (id) => {
        try {
            const response = await client.get(`/citizen/facility/${id}`);
            return response.data.facility;
        } catch (error) {
            console.error(error);
            throw new Error("Facility not found");
        }
    },

    bookFacility: async (bookingData) => {
        try {
            const response = await client.post(`/citizen/book_facility/${bookingData.facilityId}`, {
                bookedDate: bookingData.bookedDate,
                purpose: bookingData.purpose,
            });
            return response.data.booking;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            if (error.response && error.response.data && error.response.data.error) {
                throw new Error(error.response.data.error);
            }
            throw new Error("Failed to book facility.");
        }
    },

    getUserBookings: async () => {
        try {
            const response = await client.get("/citizen/bookings");
            return response.data.bookings || [];
        } catch (error) {
            console.error("Error fetching user bookings:", error);
            throw error;
        }
    },

    getAllBookings: async () => {
        try {
            const session = authService.getCurrentSession();
            if (!session) throw new Error("No active session");

            let endpoint = "/citizen/all_bookings";
            if (session.user.role === "commissioner") {
                endpoint = "/commissioner/bookings";
            }

            const response = await client.get(endpoint);
            return response.data.bookings || [];
        } catch (error) {
            console.error("Error fetching all bookings:", error);
            return [];
        }
    },

    saveFacility: async (facilityData) => {
        try {
            if (facilityData.id) {
                const payload = {};
                if (facilityData.name) payload.name = facilityData.name;
                if (facilityData.facilityType) payload.facilityType = facilityData.facilityType;
                if (facilityData.address) payload.address = facilityData.address;
                if (facilityData.pincode) payload.pincode = facilityData.pincode;
                if (facilityData.pricePerDay) payload.pricePerDay = facilityData.pricePerDay;
                if (facilityData.capacity !== undefined) payload.capacity = facilityData.capacity;
                if (facilityData.amenities !== undefined)
                    payload.amenities = facilityData.amenities;
                if (facilityData.description !== undefined)
                    payload.description = facilityData.description;
                if (facilityData.isActive !== undefined) payload.isActive = facilityData.isActive;

                const response = await client.put(
                    `/commissioner/facility/${facilityData.id}`,
                    payload
                );
                return response.data;
            } else {
                const response = await client.post("/commissioner/facility", facilityData);
                return response.data;
            }
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            if (error.response && error.response.data && error.response.data.error) {
                throw new Error(error.response.data.error);
            }
            throw new Error("Failed to save facility.");
        }
    },

    toggleFacilityStatus: async (facilityId, currentActive) => {
        try {
            const updateResponse = await client.put(`/commissioner/facility/${facilityId}`, {
                isActive: !currentActive,
            });
            return updateResponse.data;
        } catch (error) {
            console.error(error);
            throw new Error("Failed to toggle facility status.");
        }
    },

    deleteFacility: async (facilityId) => {
        try {
            await client.delete(`/commissioner/facility/${facilityId}`);
            return true;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to delete facility.");
        }
    },

    getFacilityTypes: async () => {
        try {
            const response = await client.get("/commissioner/facility-types");
            return response.data || [];
        } catch (error) {
            console.error("Error fetching facility types:", error);
            throw error;
        }
    },

    saveFacilityType: async (typeData) => {
        try {
            if (typeData.id) {
                const response = await client.put(
                    `/commissioner/facility-type/${typeData.id}`,
                    typeData
                );
                return response.data;
            } else {
                const response = await client.post("/commissioner/facility-type", typeData);
                return response.data;
            }
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to save facility type.");
        }
    },

    deleteFacilityType: async (typeId) => {
        try {
            await client.delete(`/commissioner/facility-type/${typeId}`);
            return true;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to delete facility type.");
        }
    },

    deleteBooking: async (bookingId) => {
        try {
            const response = await client.post(`/citizen/bookings/${bookingId}/cancel`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.data && error.response.data.detail) {
                throw new Error(error.response.data.detail);
            }
            throw new Error("Failed to cancel booking.");
        }
    },
};
