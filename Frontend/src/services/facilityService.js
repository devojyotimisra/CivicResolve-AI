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
  } catch (e) {
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
  } catch (e) {
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
      return facilities.filter((f) => f.type?.toLowerCase() === type.toLowerCase());
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
    const facility = await facilityService.getFacilityById(facilityId);
    return !facility.bookedDates?.includes(dateStr);
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
    if (facility.bookedDates?.includes(bookingData.bookedDate)) {
      throw new Error("This date has already been booked by another citizen.");
    }

    // Add date to facility bookedDates
    if (!facility.bookedDates) facility.bookedDates = [];
    facility.bookedDates.push(bookingData.bookedDate);
    facilities[facIndex] = facility;
    saveFacilitiesToStorage(facilities);

    // Create booking record
    const bookings = getBookingsFromStorage();
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let refPart = "";
    for (let i = 0; i < 6; i++) {
      refPart += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    const refCode = `BKG-${refPart}`;

    const newBooking = {
      id: `bkg_${Date.now()}`,
      referenceCode: refCode,
      citizenId: bookingData.citizenId,
      citizenName: bookingData.citizenName,
      facilityId: bookingData.facilityId,
      facilityName: facility.name,
      bookedDate: bookingData.bookedDate,
      amountPaid: facility.pricePerDay,
      status: "Confirmed",
      bookedAt: new Date().toISOString(),
      purpose: bookingData.purpose || "Community Gathering"
    };

    bookings.unshift(newBooking);
    saveBookingsToStorage(bookings);
    return newBooking;
  },

  getUserBookings: async (citizenId) => {
    await new Promise((res) => setTimeout(res, 300));
    const bookings = getBookingsFromStorage();
    return bookings.filter((b) => b.citizenId === citizenId).sort((a, b) => new Date(b.bookedAt) - new Date(a.bookedAt));
  },

  getAllBookings: async () => {
    await new Promise((res) => setTimeout(res, 300));
    const bookings = getBookingsFromStorage();
    return bookings.sort((a, b) => new Date(b.bookedAt) - new Date(a.bookedAt));
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
          pricePerDay: Number(facilityData.pricePerDay !== undefined ? facilityData.pricePerDay : facilities[index].pricePerDay),
          capacity: Number(facilityData.capacity !== undefined ? facilityData.capacity : facilities[index].capacity)
        };
        saveFacilitiesToStorage(facilities);
        return facilities[index];
      }
    }

    const newFac = {
      id: `fac_${Date.now()}`,
      isActive: true,
      bookedDates: [],
      image: "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=600&auto=format&fit=crop&q=80",
      ...facilityData,
      pricePerDay: Number(facilityData.pricePerDay),
      capacity: Number(facilityData.capacity)
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
  }
};
