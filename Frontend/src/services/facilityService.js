import { INITIAL_FACILITIES, INITIAL_BOOKINGS } from "@/api/mockSeedData";

const FACILITIES_KEY = "civic_facilities";
const BOOKINGS_KEY = "civic_bookings";

function getFacilitiesFromStorage() {
  const data = localStorage.getItem(FACILITIES_KEY);
  if (!data) {
    localStorage.setItem(FACILITIES_KEY, JSON.stringify(INITIAL_FACILITIES));
    return INITIAL_FACILITIES;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_FACILITIES;
  }
}

function saveFacilitiesToStorage(facilities) {
  localStorage.setItem(FACILITIES_KEY, JSON.stringify(facilities));
}

function getBookingsFromStorage() {
  const data = localStorage.getItem(BOOKINGS_KEY);
  if (!data) {
    localStorage.setItem(BOOKINGS_KEY, JSON.stringify(INITIAL_BOOKINGS));
    return INITIAL_BOOKINGS;
  }
  try {
    return JSON.parse(data);
  } catch {
    return INITIAL_BOOKINGS;
  }
}

function saveBookingsToStorage(bookings) {
  localStorage.setItem(BOOKINGS_KEY, JSON.stringify(bookings));
}

export const facilityService = {
  getAllFacilities: async (type = "all") => {
    await new Promise((res) => setTimeout(res, 300));
    const facilities = getFacilitiesFromStorage();
    if (type && type !== "all") {
      return facilities.filter((f) => f.facilityType?.toLowerCase() === type.toLowerCase());
    }
    return facilities;
  },

  getFacilityById: async (id) => {
    await new Promise((res) => setTimeout(res, 250));
    const facilities = getFacilitiesFromStorage();
    const found = facilities.find((f) => f.id === id);
    if (!found) throw new Error("Facility not found");
    return found;
  },

  checkAvailability: async (facilityId, dateStr) => {
    await new Promise((res) => setTimeout(res, 200));
    const bookings = getBookingsFromStorage();
    const isBooked = bookings.some((b) => b.facilityId === facilityId && b.bookedDate === dateStr && b.status !== "Cancelled");
    return !isBooked;
  },

  bookFacility: async (bookingData) => {
    await new Promise((res) => setTimeout(res, 700));
    const facilities = getFacilitiesFromStorage();
    const facIndex = facilities.findIndex((f) => f.id === bookingData.facilityId);
    if (facIndex === -1) throw new Error("Facility not found");

    const facility = facilities[facIndex];
    if (facility.isActive === false) {
      throw new Error("This facility is currently not accepting reservations.");
    }
    const bookings = getBookingsFromStorage();
    if (bookings.some((b) => b.facilityId === bookingData.facilityId && b.bookedDate === bookingData.bookedDate && b.status !== "Cancelled")) {
      throw new Error("This date has already been booked by another citizen.");
    }
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let refPart = "";
    for (let i = 0; i < 6; i++) {
      refPart += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    const refCode = `BKG-${refPart}`;

    const newBooking = {
      id: `bkg_${Date.now()}`,
      bookingReference: refCode,
      userId: bookingData.userId,
      citizenName: bookingData.citizenName,
      facilityId: bookingData.facilityId,
      facilityName: facility.name,
      bookedDate: bookingData.bookedDate,
      amountPaid: facility.pricePerDay,
      status: "Confirmed",
      createdAt: new Date().toISOString(),
      purpose: bookingData.purpose || "Community Gathering"
    };

    bookings.unshift(newBooking);
    saveBookingsToStorage(bookings);
    return newBooking;
  },

  getUserBookings: async (userId) => {
    await new Promise((res) => setTimeout(res, 300));
    const bookings = getBookingsFromStorage();
    return bookings.filter((b) => b.userId === userId).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  },

  getAllBookings: async () => {
    await new Promise((res) => setTimeout(res, 300));
    const bookings = getBookingsFromStorage();
    return bookings.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  },

  saveFacility: async (facilityData) => {
    await new Promise((res) => setTimeout(res, 400));
    const facilities = getFacilitiesFromStorage();

    if (facilityData.id) {
      const index = facilities.findIndex((f) => f.id === facilityData.id);
      if (index !== -1) {
        facilities[index] = {
          ...facilities[index],
          ...facilityData,
          pricePerDay: parseFloat(String(facilityData.pricePerDay !== undefined ? facilityData.pricePerDay : facilities[index].pricePerDay).replace(/,/g, "")) || 0,
          capacity: facilityData.capacity !== undefined && facilityData.capacity !== "" && facilityData.capacity !== null ? (parseInt(facilityData.capacity, 10) || null) : (facilities[index].capacity || null)
        };
        saveFacilitiesToStorage(facilities);
        return facilities[index];
      }
    }

    const newFac = {
      id: `fac_${Date.now()}`,
      isActive: true,
      ...facilityData,
      pricePerDay: parseFloat(String(facilityData.pricePerDay || 0).replace(/,/g, "")) || 0,
      capacity: facilityData.capacity !== undefined && facilityData.capacity !== "" && facilityData.capacity !== null ? (parseInt(facilityData.capacity, 10) || null) : null
    };

    facilities.push(newFac);
    saveFacilitiesToStorage(facilities);
    return newFac;
  },

  toggleFacilityStatus: async (facilityId) => {
    await new Promise((res) => setTimeout(res, 300));
    const facilities = getFacilitiesFromStorage();
    const index = facilities.findIndex((f) => f.id === facilityId);
    if (index === -1) throw new Error("Facility not found");

    facilities[index].isActive = !facilities[index].isActive;
    saveFacilitiesToStorage(facilities);
    return facilities[index];
  },

  deleteFacility: async (facilityId) => {
    await new Promise((res) => setTimeout(res, 300));
    let facilities = getFacilitiesFromStorage();
    const index = facilities.findIndex((f) => f.id === facilityId);
    if (index === -1) throw new Error("Facility not found");

    facilities.splice(index, 1);
    saveFacilitiesToStorage(facilities);
    return true;
  },

  deleteBooking: async (bookingId) => {
    await new Promise((res) => setTimeout(res, 300));
    let bookings = getBookingsFromStorage();
    const index = bookings.findIndex((b) => b.id === bookingId);
    if (index === -1) throw new Error("Booking not found");

    bookings.splice(index, 1);
    saveBookingsToStorage(bookings);
    return true;
  }
};
