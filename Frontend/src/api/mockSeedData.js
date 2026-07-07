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
    title: "Field Officer",
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
    title: "Field Officer",
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
    title: "Commissioner",
    phone: "+91 44 2538 1111",
  }
];

export const INITIAL_COMPLAINTS = [
  {
    id: "comp_1",
    token: "CRA-8B2Z9X",
    title: "Severe Pothole Causing Traffic Hazard on 2nd Avenue",
    status: "In Progress",
    description: "A massive crater has formed near the Anna Nagar round-tana traffic light. Multiple two-wheelers have skidded here during evening rush hour. Needs emergency tarmac patching immediately.",
    location: "2nd Avenue, Near Anna Nagar Tower Park, Chennai 600040",
    severity: "Normal",
    submittedAt: "2026-07-07T08:30:00Z",
    updatedAt: "2026-07-04T14:15:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: "usr_officer_1",
    assignedOfficerName: "Suresh Menon",
    department: "Roads & Traffic",
    timeline: [
      { status: "Submitted", timestamp: "2026-07-02T09:30:00Z" },
      { status: "Assigned", timestamp: "2026-07-02T11:45:00Z" },
      { status: "En Route", timestamp: "2026-07-03T08:20:00Z" },
      { status: "On Site", timestamp: "2026-07-03T09:10:00Z" },
      { status: "In Progress", timestamp: "2026-07-04T14:15:00Z" }
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
    submittedAt: "2026-06-25T14:15:00Z",
    updatedAt: "2026-06-30T11:00:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1605600659908-0ef719419d41?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: "usr_officer_2",
    assignedOfficerName: "Anita Sharma",
    department: "Solid Waste",
    resolutionPhoto: "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=600&auto=format&fit=crop&q=80",
    resolutionNote: "Compactor truck #SW-402 deployed. Dumpster cleared, sanitized with bleaching powder, and sidewalk washed.",
    timeline: [
      { status: "Submitted", timestamp: "2026-06-28T16:20:00Z" },
      { status: "Assigned", timestamp: "2026-06-29T09:00:00Z" },
      { status: "En Route", timestamp: "2026-06-30T08:30:00Z" },
      { status: "On Site", timestamp: "2026-06-30T09:15:00Z" },
      { status: "Resolved", timestamp: "2026-06-30T11:00:00Z", note: "Area cleaned and sanitized. Proof uploaded." }
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
    submittedAt: "2026-07-05T06:10:00Z",
    updatedAt: "2026-07-05T06:10:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: null,
    assignedOfficerName: null,
    department: "Water Supply",
    timeline: [
      { status: "Submitted", timestamp: "2026-07-05T06:10:00Z" }
    ]
  },
  {
    id: "comp_4",
    token: "CRA-5L1W8V",
    title: "Broken LED Street Lights Creating Safety Risk",
    status: "In Progress",
    description: "The LED street light pole near the Guindy bus stand is broken at the base and leaning dangerously over the pedestrian walkway.",
    location: "Sardar Patel Road, Guindy, Chennai 600032",
    severity: "Critical",
    submittedAt: "2026-07-01T19:45:00Z",
    updatedAt: "2026-07-02T10:30:00Z",
    submittedPhoto: "https://images.unsplash.com/photo-1508873696983-2df529a3c882?w=600&auto=format&fit=crop&q=80",
    assignedOfficerId: "usr_officer_1",
    assignedOfficerName: "Suresh Menon",
    department: "Electrical & Lighting",
    timeline: [
      { status: "Submitted", timestamp: "2026-07-01T19:45:00Z" },
      { status: "Assigned", timestamp: "2026-07-02T10:30:00Z" }
    ]
  }
];

export const INITIAL_FACILITIES = [
  {
    id: "fac_1",
    name: "Indira Gandhi Municipal Community Hall",
    type: "Community Hall",
    address: "12, TTK Road, Alwarpet, Chennai 600018",
    pincode: "600018",
    pricePerDay: 8500,
    capacity: 450,
    isActive: true,
    description: "A spacious, fully air-conditioned municipal banquet hall suitable for weddings, cultural gatherings, and community meetings. Features power backup, kitchen facilities, and ample parking.",
    amenities: ["Air Conditioning", "500-Car Parking", "Industrial Kitchen", "PA Sound System", "Power Generator"],
    bookedDates: ["2026-07-10", "2026-07-11", "2026-07-15", "2026-07-20", "2026-07-25", "2026-08-01", "2026-08-05"]
  },
  {
    id: "fac_2",
    name: "Nehru Centenary Park & Amphitheatre",
    type: "Park",
    address: "Greenways Road, RA Puram, Chennai 600028",
    pincode: "600028",
    pricePerDay: 4000,
    capacity: 800,
    isActive: true,
    description: "Lush green open-air municipal park featuring a stone amphitheatre, jogging tracks, botanical gardens, and solar-powered lighting. Ideal for yoga retreats, art exhibitions, and musical plays.",
    amenities: ["Open Amphitheatre", "Solar Lighting", "Public Restrooms", "Drinking Water Fountains", "Security Patrol"],
    bookedDates: ["2026-07-08", "2026-07-12", "2026-07-18", "2026-07-22", "2026-07-30"]
  },
  {
    id: "fac_3",
    name: "Anna Nagar Sports & Civic Arena",
    type: "Community Hall",
    address: "6th Avenue, Anna Nagar East, Chennai 600010",
    pincode: "600010",
    pricePerDay: 12000,
    capacity: 600,
    isActive: true,
    description: "State-of-the-art indoor civic arena with wooden flooring, badminton/basketball courts, conference rooms, and VIP galleries. Perfect for sports tournaments and civic workshops.",
    amenities: ["Wooden Flooring", "Locker Rooms", "LED Scoreboards", "Cafeteria", "24/7 CCTV"],
    bookedDates: ["2026-07-09", "2026-07-14", "2026-07-21", "2026-08-10"]
  },
  {
    id: "fac_4",
    name: "Besant Nagar Beachfront Pavilion",
    type: "Park",
    address: "Edward Elliot Beach Promenade, Chennai 600090",
    pincode: "600090",
    pricePerDay: 5500,
    capacity: 350,
    isActive: true,
    description: "Scenic oceanfront municipal pavilion with shaded gazebos, sea-breeze seating, and direct beach access. Popular for environmental awareness camps and weekend cultural fests.",
    amenities: ["Ocean View Gazebos", "Waste Recycling Stations", "Disabled Ramp Access", "Food Stall Bays"],
    bookedDates: ["2026-07-16", "2026-07-17", "2026-07-23", "2026-07-24"]
  },
  {
    id: "fac_5",
    name: "Shenoy Nagar Gymkhana & Heritage Banquet",
    type: "Community Hall",
    address: "Pulla Avenue, Shenoy Nagar, Chennai 600030",
    pincode: "600030",
    pricePerDay: 9500,
    capacity: 500,
    isActive: true,
    description: "Heritage municipal structure recently restored with modern acoustics, crystal chandeliers, and landscaped lawns. Ideal for banquets and civic exhibitions.",
    amenities: ["Heritage Architecture", "Acoustic Hall", "VIP Lounge", "Valet Parking Area"],
    bookedDates: []
  }
];

export const INITIAL_BILLS = [
  {
    id: "bill_1",
    billNumber: "BILL-2026-8831",
    citizenId: "usr_citizen_1",
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
    citizenId: "usr_citizen_1",
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
    citizenId: "usr_citizen_1",
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
    citizenId: "usr_citizen_1",
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
    referenceCode: "BKG-9A8B7C",
    citizenId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    facilityId: "fac_1",
    facilityName: "Indira Gandhi Municipal Community Hall",
    bookedDate: "2026-07-20",
    amountPaid: 8500,
    status: "Confirmed",
    bookedAt: "2026-06-25T14:20:00Z",
    purpose: "Family Reunion & Dinner"
  },
  {
    id: "bkg_2",
    referenceCode: "BKG-4X2Y1Z",
    citizenId: "usr_citizen_1",
    citizenName: "Rajesh Kumar",
    facilityId: "fac_2",
    facilityName: "Nehru Centenary Park & Amphitheatre",
    bookedDate: "2026-06-15",
    amountPaid: 4000,
    status: "Completed",
    bookedAt: "2026-05-20T10:15:00Z",
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
      type: "warning",
      timestamp: "2026-07-07T08:30:00Z",
      read: false,
      link: "/dash/citizen/bills",
    },
    {
      id: "cit-2",
      title: "Complaint Status Updated",
      message: "Your road repair complaint #TKN-8831 has been marked as 'In Progress' by Ward Officer.",
      type: "info",
      timestamp: "2026-07-07T07:00:00Z",
      read: false,
      link: "/complaint/track",
    },
    {
      id: "cit-3",
      title: "Facility Booking Confirmed",
      message: "Your booking for Community Hall (Anna Nagar) on July 15 has been confirmed.",
      type: "success",
      timestamp: "2026-07-07T04:00:00Z",
      read: true,
      link: "/dash/citizen/facilities",
    },
  ],
  officer: [
    {
      id: "off-1",
      title: "New Severe Complaint",
      message: "A severe water leakage complaint has been reported in Ward 12 requiring immediate attention.",
      type: "alert",
      timestamp: "2026-07-07T08:45:00Z",
      read: false,
      link: "/dash/officer",
    },
    {
      id: "off-2",
      title: "Review Meeting Scheduled",
      message: "Commissioner has scheduled a ward review meeting tomorrow at 11:00 AM.",
      type: "info",
      timestamp: "2026-07-07T07:30:00Z",
      read: false,
      link: "/dash/officer",
    },
    {
      id: "off-3",
      title: "Daily Target Achieved",
      message: "You have resolved 80% of assigned tickets this week. Great job!",
      type: "success",
      timestamp: "2026-07-07T05:00:00Z",
      read: true,
      link: "/dash/officer",
    },
  ],
  commissioner: [
    {
      id: "com-1",
      title: "Resolution Speed Alert",
      message: "City-wide resolution time dropped by 2.4% over the last 48 hours.",
      type: "alert",
      timestamp: "2026-07-07T08:40:00Z",
      read: false,
      link: "/dash/commissioner/analytics",
    },
    {
      id: "com-2",
      title: "Pending Officer Approvals",
      message: "3 new field officers are awaiting ward reassignment approval.",
      type: "warning",
      timestamp: "2026-07-07T06:00:00Z",
      read: false,
      link: "/dash/commissioner/officers",
    },
    {
      id: "com-3",
      title: "Monthly Report Generated",
      message: "The comprehensive Q2 Civic Infrastructure & Revenue Report is ready for review.",
      type: "info",
      timestamp: "2026-07-06T20:00:00Z",
      read: true,
      link: "/dash/commissioner",
    },
  ],
};
