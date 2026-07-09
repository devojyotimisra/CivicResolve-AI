export const INITIAL_USERS = [
  {
    id: "usr_citizen_1",
    name: "Rajesh Kumar",
    email: "citizen1@civicresolveai.org",
    password: "password123",
    role: "citizen",
    phone: "+91 98765 43210",
    address: "42, MG Road, Adyar, Chennai",
    pincode: "600020",
  },
  {
    id: "usr_officer_1",
    name: "Suresh Menon",
    email: "officer1@civicresolveai.org",
    password: "password123",
    role: "officer",
    badgeId: "OFF-104",
    department: "Roads & Traffic",
    phone: "+91 98410 11223",
  },
  {
    id: "usr_officer_2",
    name: "Anita Sharma",
    email: "officer2@civicresolveai.org",
    password: "password123",
    role: "officer",
    badgeId: "OFF-209",
    department: "Solid Waste",
    phone: "+91 98410 44556",
  },
  {
    id: "usr_comm_1",
    name: "Dr. Vikram Aditya",
    email: "commissioner1@civicresolveai.org",
    password: "password123",
    role: "commissioner",
    badgeId: "COM-001",
    phone: "+91 44 2538 1111",
  }
];

export const INITIAL_COMPLAINTS = [
  {
    id: "comp_1",
    token: "CRA-8B2Z9X",
    title: "Severe Pothole Causing Traffic Hazard on 2nd Avenue",
    status: "Assigned",
    description: "A massive crater has formed near the Anna Nagar round-tana traffic light. Multiple two-wheelers have skidded here during evening rush hour. Needs emergency tarmac patching immediately.",
    location: "2nd Avenue, Near Anna Nagar Tower Park, Chennai 600040",
    severity: "Normal",
    createdAt: "2026-07-07T08:30:00Z",
    updatedAt: "2026-07-04T14:15:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: "usr_officer_1",
    assignedOfficerName: "Suresh Menon",
    department: "Roads & Traffic",
    updates: [
      { newStatus: "Submitted", oldStatus: null, updatedById: null, updatedByName: "Citizen Portal", createdAt: "2026-07-02T09:30:00Z", note: "Report filed via citizen portal with initial hazard details." },
      { newStatus: "Assigned", oldStatus: "Submitted", updatedById: "usr_officer_1", updatedByName: "Suresh Menon", createdAt: "2026-07-02T11:45:00Z", note: "Assigned to Field Officer Suresh Menon by Ward Commissioner." }
    ]
  },
  {
    id: "comp_2",
    token: "CRA-3F7Y1K",
    title: "Overflowing Garbage Dumpster Blocking Sidewalk",
    status: "Resolved",
    description: "The primary municipal waste bin outside Besant Nagar beach road has not been cleared for 4 days. Waste is spilling onto the pedestrian walking track causing severe odor and health hazards.",
    location: "4th Main Road, Besant Nagar, Chennai 600090",
    severity: "Normal",
    createdAt: "2026-06-25T14:15:00Z",
    updatedAt: "2026-06-30T11:00:00Z",
    resolvedAt: "2026-06-30T11:00:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: "usr_officer_2",
    assignedOfficerName: "Anita Sharma",
    department: "Solid Waste",
    resolutionPhoto: "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=600&auto=format&fit=crop&q=80",
    resolutionNote: "Compactor truck #SW-402 deployed. Dumpster cleared, sanitized with bleaching powder, and sidewalk washed.",
    updates: [
      { newStatus: "Submitted", oldStatus: null, updatedById: null, updatedByName: "Citizen Portal", createdAt: "2026-06-28T16:20:00Z", note: "Report filed regarding overflowing waste container." },
      { newStatus: "Assigned", oldStatus: "Submitted", updatedById: "usr_officer_2", updatedByName: "Anita Sharma", createdAt: "2026-06-29T09:00:00Z", note: "Assigned to Field Officer Anita Sharma." },
      { newStatus: "En Route", oldStatus: "Assigned", updatedById: "usr_officer_2", updatedByName: "Anita Sharma", createdAt: "2026-06-30T08:30:00Z", note: "Officer en route to inspection site with sanitation crew." },
      { newStatus: "On Site", oldStatus: "En Route", updatedById: "usr_officer_2", updatedByName: "Anita Sharma", createdAt: "2026-06-30T09:15:00Z", note: "Officer and sanitation team arrived on location." },
      { newStatus: "Resolved", oldStatus: "On Site", updatedById: "usr_officer_2", updatedByName: "Anita Sharma", createdAt: "2026-06-30T11:00:00Z", note: "Area cleaned and sanitized. Proof uploaded." }
    ]
  },
  {
    id: "comp_3",
    token: "CRA-9M4P2Q",
    title: "Major Water Pipe Burst Flooding Residential Street",
    status: "Assigned",
    description: "A large water pipe has burst underground, flooding the street and causing a drop in water pressure for the entire block.",
    location: "3rd Cross Street, Kasturba Nagar, Adyar, Chennai 600020",
    severity: "Critical",
    createdAt: "2026-07-05T06:10:00Z",
    updatedAt: "2026-07-05T06:10:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: null,
    assignedOfficerName: null,
    department: "Water Supply",
    updates: [
      { newStatus: "Submitted", oldStatus: null, updatedById: null, updatedByName: "Public Portal", createdAt: "2026-07-05T06:10:00Z", note: "Emergency water burst report submitted." }
    ]
  },
  {
    id: "comp_4",
    token: "CRA-5L1W8V",
    title: "Broken LED Street Lights Creating Safety Risk",
    status: "Assigned",
    description: "The LED street light pole near the Guindy bus stand is broken at the base and leaning dangerously over the pedestrian walkway.",
    location: "Sardar Patel Road, Guindy, Chennai 600032",
    severity: "Critical",
    createdAt: "2026-07-01T19:45:00Z",
    updatedAt: "2026-07-02T10:30:00Z",
    submittedPhoto: null,
    assignedOfficerId: "usr_officer_1",
    assignedOfficerName: "Suresh Menon",
    department: "Electrical & Lighting",
    updates: [
      { newStatus: "Submitted", oldStatus: null, updatedById: null, updatedByName: "Citizen Portal", createdAt: "2026-07-01T19:45:00Z", note: "Report filed regarding broken street light pole." },
      { newStatus: "Assigned", oldStatus: "Submitted", updatedById: "usr_officer_1", updatedByName: "Suresh Menon", createdAt: "2026-07-02T10:30:00Z", note: "Assigned to Field Officer Suresh Menon." }
    ]
  }
];

export const INITIAL_FACILITIES = [
  {
    id: "fac_1",
    name: "Indira Gandhi Municipal Community Hall",
    facilityType: "Community Hall",
    address: "12, TTK Road, Alwarpet, Chennai 600018",
    pincode: "600018",
    pricePerDay: 8500,
    capacity: 450,
    isActive: true,
    description: "A spacious, fully air-conditioned municipal banquet hall suitable for weddings, cultural gatherings, and community meetings. Features power backup, kitchen facilities, and ample parking.",
    amenities: ["Air Conditioning", "500-Car Parking", "Industrial Kitchen", "PA Sound System", "Power Generator"]
  },
  {
    id: "fac_2",
    name: "Nehru Centenary Park & Amphitheatre",
    facilityType: "Park",
    address: "Greenways Road, RA Puram, Chennai 600028",
    pincode: "600028",
    pricePerDay: 4000,
    capacity: 800,
    isActive: true,
    description: "Lush green open-air municipal park featuring a stone amphitheatre, jogging tracks, botanical gardens, and solar-powered lighting. Ideal for yoga retreats, art exhibitions, and musical plays.",
    amenities: ["Open Amphitheatre", "Solar Lighting", "Public Restrooms", "Drinking Water Fountains", "Security Patrol"]
  },
  {
    id: "fac_3",
    name: "Anna Nagar Sports & Civic Arena",
    facilityType: "Community Hall",
    address: "6th Avenue, Anna Nagar East, Chennai 600010",
    pincode: "600010",
    pricePerDay: 12000,
    capacity: 600,
    isActive: true,
    description: "State-of-the-art indoor civic arena with wooden flooring, badminton/basketball courts, conference rooms, and VIP galleries. Perfect for sports tournaments and civic workshops.",
    amenities: ["Wooden Flooring", "Locker Rooms", "LED Scoreboards", "Cafeteria", "24/7 CCTV"]
  },
  {
    id: "fac_4",
    name: "Besant Nagar Beachfront Pavilion",
    facilityType: "Park",
    address: "Edward Elliot Beach Promenade, Chennai 600090",
    pincode: "600090",
    pricePerDay: 5500,
    capacity: 350,
    isActive: true,
    description: "Scenic oceanfront municipal pavilion with shaded gazebos, sea-breeze seating, and direct beach access. Popular for environmental awareness camps and weekend cultural fests.",
    amenities: ["Ocean View Gazebos", "Waste Recycling Stations", "Disabled Ramp Access", "Food Stall Bays"]
  },
  {
    id: "fac_5",
    name: "Shenoy Nagar Gymkhana & Heritage Banquet",
    facilityType: "Community Hall",
    address: "Pulla Avenue, Shenoy Nagar, Chennai 600030",
    pincode: "600030",
    pricePerDay: 9500,
    capacity: 500,
    isActive: true,
    description: "Heritage municipal structure recently restored with modern acoustics, crystal chandeliers, and landscaped lawns. Ideal for banquets and civic exhibitions.",
    amenities: ["Heritage Architecture", "Acoustic Hall", "VIP Lounge", "Valet Parking Area"]
  }
];

export const INITIAL_BILLS = [
  {
    id: "bill_1",
    billNumber: "BILL-2026-8831",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    billType: "Property Tax",
    amount: 6450,
    dueDate: "2026-07-31",
    status: "Pending",
    period: "Q2 2026 (July - September)",
    generatedAt: "2026-07-01"
  },
  {
    id: "bill_2",
    billNumber: "BILL-2026-4412",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    billType: "Water & Sewage",
    amount: 1250,
    dueDate: "2026-07-15",
    status: "Pending",
    period: "June 2026 Consumption",
    generatedAt: "2026-07-01"
  },
  {
    id: "bill_3",
    billNumber: "BILL-2026-1092",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    billType: "Municipal Electricity",
    amount: 3420,
    dueDate: "2026-06-25",
    status: "Paid",
    period: "May 2026 Consumption",
    generatedAt: "2026-06-01",
    paidAt: "2026-06-20T11:30:00Z",
    paymentRef: "TXN_UPI_99482716"
  },
  {
    id: "bill_4",
    billNumber: "BILL-2026-0045",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    billType: "Garbage & Sanitation Fee",
    amount: 600,
    dueDate: "2026-05-30",
    status: "Paid",
    period: "Annual Sanitation Levy 2026",
    generatedAt: "2026-05-01",
    paidAt: "2026-05-18T16:10:00Z",
    paymentRef: "TXN_CC_88219034"
  }
];

export const INITIAL_BOOKINGS = [
  {
    id: "bkg_1",
    bookingReference: "BKG-9A8B7C",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    facilityId: "fac_1",
    facilityName: "Indira Gandhi Municipal Community Hall",
    bookedDate: "2026-07-20",
    amountPaid: 8500,
    status: "Confirmed",
    createdAt: "2026-06-25T14:20:00Z",
    purpose: "Family Reunion & Dinner"
  },
  {
    id: "bkg_2",
    bookingReference: "BKG-4X2Y1Z",
    userId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    facilityId: "fac_2",
    facilityName: "Nehru Centenary Park & Amphitheatre",
    bookedDate: "2026-06-15",
    amountPaid: 4000,
    status: "Completed",
    createdAt: "2026-05-20T10:15:00Z",
    purpose: "Neighborhood Environmental Awareness Workshop"
  }
];

export const INITIAL_DEPARTMENTS = [
  { id: "dept_1", name: "Roads & Traffic" },
  { id: "dept_2", name: "Solid Waste" },
  { id: "dept_3", name: "Water Supply" },
  { id: "dept_4", name: "Electrical & Lighting" },
  { id: "dept_5", name: "Horticulture & Parks" },
  { id: "dept_6", name: "Public Health" },
  { id: "dept_7", name: "Veterinary Services" }
];

export const INITIAL_NOTIFICATIONS = {
  citizen: [
    {
      id: "cit-1",
      title: "Water Tax Bill #4829 Due",
      message: "Your Q2 water tax bill of ₹1,450 is due in 3 days. Pay now to avoid late fees.",
      notifType: "warning",
      createdAt: "2026-07-07T08:30:00Z",
      isRead: false,
    },
    {
      id: "cit-2",
      title: "Complaint Status Updated",
      message: "Your road repair complaint #TKN-8831 has been marked as 'In Progress' by Ward Officer.",
      notifType: "info",
      createdAt: "2026-07-07T07:00:00Z",
      isRead: false,
    },
    {
      id: "cit-3",
      title: "Facility Booking Confirmed",
      message: "Your booking for Community Hall (Anna Nagar) on July 15 has been confirmed.",
      notifType: "success",
      createdAt: "2026-07-07T04:00:00Z",
      isRead: true,
    },
  ],
  officer: [
    {
      id: "off-1",
      title: "New Severe Complaint",
      message: "A severe water leakage complaint has been reported in Ward 12 requiring immediate attention.",
      notifType: "alert",
      createdAt: "2026-07-07T08:45:00Z",
      isRead: false,
    },
    {
      id: "off-2",
      title: "Review Meeting Scheduled",
      message: "Commissioner has scheduled a ward review meeting tomorrow at 11:00 AM.",
      notifType: "info",
      createdAt: "2026-07-07T07:30:00Z",
      isRead: false,
    },
    {
      id: "off-3",
      title: "Daily Target Achieved",
      message: "You have resolved 80% of assigned tickets this week. Great job!",
      notifType: "success",
      createdAt: "2026-07-07T05:00:00Z",
      isRead: true,
    },
  ],
  commissioner: [
    {
      id: "com-1",
      title: "Resolution Speed Alert",
      message: "City-wide resolution time dropped by 2.4% over the last 48 hours.",
      notifType: "alert",
      createdAt: "2026-07-07T08:40:00Z",
      isRead: false,
    },
    {
      id: "com-2",
      title: "Pending Officer Approvals",
      message: "3 new field officers are awaiting ward reassignment approval.",
      notifType: "warning",
      createdAt: "2026-07-07T06:00:00Z",
      isRead: false,
    },
    {
      id: "com-3",
      title: "Monthly Report Generated",
      message: "The comprehensive Q2 Civic Infrastructure & Revenue Report is ready for review.",
      notifType: "info",
      createdAt: "2026-07-06T20:00:00Z",
      isRead: true,
    },
  ],
};

export const INITIAL_BILL_TYPES = [
  { id: "bt_1", name: "Property Tax" },
  { id: "bt_2", name: "Water & Sewage" },
  { id: "bt_3", name: "Municipal Electricity" },
  { id: "bt_4", name: "Garbage & Sanitation Fee" },
  { id: "bt_5", name: "Trade License Fee" },
  { id: "bt_6", name: "Building Plan Fee" }
];
