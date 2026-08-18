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

      const response = await client.get(endpoint, { params: { type: type !== "all" ? type : undefined } });
      return response.data.facilities || response.data;
    } catch (error) {
      console.error("Error fetching facilities:", error);
      throw error;
    }
  },

  getFacilityById: async (id) => {
    try {
      const response = await client.get(`/citizen/facility/${id}`);
      return response.data.facility || response.data;
    } catch (error) {
      throw new Error("Facility not found");
    }
  },

  checkAvailability: async (facilityId, dateStr) => {


    return true;
  },

  bookFacility: async (bookingData) => {
    try {
      const response = await client.post(`/citizen/book_facility/${bookingData.facilityId}`, {
        booked_date: bookingData.bookedDate,
        purpose: bookingData.purpose || "Community Gathering"
      });
      return response.data.booking || response.data;
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

  getUserBookings: async (userId) => {
    try {
      const response = await client.get("/citizen/bookings");
      return response.data.bookings || response.data;
    } catch (error) {
      console.error("Error fetching user bookings:", error);
      throw error;
    }
  },

  getAllBookings: async () => {

    return [];
  },

  saveFacility: async (facilityData) => {
    try {
      if (facilityData.id) {

        const payload = {};
        if (facilityData.name) payload.name = facilityData.name;
        if (facilityData.facilityType || facilityData.facility_type) payload.facility_type = facilityData.facilityType || facilityData.facility_type;
        if (facilityData.address) payload.address = facilityData.address;
        if (facilityData.pincode) payload.pincode = facilityData.pincode;
        if (facilityData.pricePerDay || facilityData.price_per_day) payload.price_per_day = facilityData.pricePerDay || facilityData.price_per_day;
        if (facilityData.description !== undefined) payload.description = facilityData.description;
        if (facilityData.is_active !== undefined) payload.is_active = facilityData.is_active;
        if (facilityData.isActive !== undefined) payload.is_active = facilityData.isActive;

        const response = await client.put(`/commissioner/facility/${facilityData.id}`, payload);
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

  toggleFacilityStatus: async (facilityId) => {
    try {

      const detailResponse = await client.get(`/citizen/facility/${facilityId}`);
      const facilityData = detailResponse.data.facility || detailResponse.data;
      const currentActive = facilityData.is_active ?? facilityData.isActive ?? true;


      const updateResponse = await client.put(`/commissioner/facility/${facilityId}`, {
        is_active: !currentActive
      });
      return updateResponse.data;
    } catch (error) {
      throw new Error("Failed to toggle facility status.");
    }
  },

  deleteFacility: async (facilityId) => {
    try {
      await client.delete(`/commissioner/facility/${facilityId}`);
      return true;
    } catch (error) {
      throw new Error("Failed to delete facility.");
    }
  },

  deleteBooking: async (bookingId) => {

    throw new Error("Booking cancellation is not currently supported. Please contact the administration office.");
  }
};
