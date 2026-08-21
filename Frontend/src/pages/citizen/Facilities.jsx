import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { facilityService } from "@/services/facilityService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Calendar } from "@/components/ui/calendar";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Building2,
  Search,
  MapPin,
  Users,
  Calendar as CalendarIcon,
  Download,
  CreditCard,
  CheckCircle2,
  Printer,
} from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

export const CitizenFacilities = () => {
  const { user } = useAuth();
  const [mainTab, setMainTab] = useState("explore");
  const [facilities, setFacilities] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [allBookings, setAllBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [reservationQuery, setReservationQuery] = useState("");
  const [reservationFilter, setReservationFilter] = useState("all");
  const [selectedFacility, setSelectedFacility] = useState(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedDateStr, setSelectedDateStr] = useState("");
  const [purpose, setPurpose] = useState("");
  const [bookingLoading, setBookingLoading] = useState(false);
  const [confirmBooking, setConfirmBooking] = useState(false);
  const [cardName, setCardName] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvv, setCardCvv] = useState("");

  const initBookSubmit = () => {
    if (!selectedDateStr || !selectedFacility) {
      toast.error("Please select a reservation date from the calendar.");
      return;
    }
    const isBooked = allBookings.some(
      (b) =>
        b.facilityId === selectedFacility.id &&
        b.bookedDate === selectedDateStr &&
        b.status !== "Cancelled",
    );
    if (isBooked) {
      toast.error("This date is already booked. Please choose another date.");
      return;
    }
    setConfirmBooking(true);
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [facData, bkgData, allBkgData] = await Promise.all([
        facilityService.getAllFacilities("all"),
        user ? facilityService.getUserBookings(user.id) : Promise.resolve([]),
        facilityService.getAllBookings(),
      ]);
      setFacilities(facData);
      setBookings(bkgData);
      setAllBookings(allBkgData);
    } catch {
      toast.error("Failed to load civic facilities and reservations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const searchedFacilities = facilities.filter((fac) => {
    if (searchQuery.trim() !== "") {
      const keywords = searchQuery
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      return keywords.every((query) => {
        const matchName = (fac.name || "").toLowerCase().includes(query);
        const matchAddress = (fac.address || "").toLowerCase().includes(query);
        const matchDesc = (fac.description || "").toLowerCase().includes(query);
        const matchType = (fac.facilityType || "")
          .toLowerCase()
          .includes(query);
        const matchAmenities = (fac.amenities || []).some((a) =>
          a.toLowerCase().includes(query),
        );
        return (
          matchName || matchAddress || matchDesc || matchType || matchAmenities
        );
      });
    }
    return true;
  });

  const filteredFacilities = searchedFacilities.filter((fac) => {
    if (typeFilter === "all") return true;
    return fac.facilityType?.toLowerCase() === typeFilter.toLowerCase();
  });

  const searchedBookings = bookings.filter((bkg) => {
    if (reservationQuery.trim() !== "") {
      const keywords = reservationQuery
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      return keywords.every((query) => {
        const matchRef = (bkg.bookingReference || "")
          .toLowerCase()
          .includes(query);
        const matchFac = (bkg.facilityName || "").toLowerCase().includes(query);
        const matchPurpose = (bkg.purpose || "").toLowerCase().includes(query);
        const matchStatus = (bkg.status || "").toLowerCase().includes(query);
        const matchAmount = (bkg.amountPaid || "").toString().includes(query);
        const matchDate = (bkg.bookedDate || "").includes(query);
        return (
          matchRef ||
          matchFac ||
          matchPurpose ||
          matchStatus ||
          matchAmount ||
          matchDate
        );
      });
    }
    return true;
  });

  const filteredBookings = searchedBookings.filter((bkg) => {
    if (reservationFilter === "all") return true;
    if (reservationFilter === "confirmed") return bkg.status === "Confirmed";
    if (reservationFilter === "completed") return bkg.status === "Completed";
    return true;
  });

  const handleBookSubmit = async () => {
    if (!selectedDateStr || !selectedFacility) {
      toast.error("Please select a reservation date from the calendar.");
      return;
    }
    const isBooked = allBookings.some(
      (b) =>
        b.facilityId === selectedFacility.id &&
        b.bookedDate === selectedDateStr &&
        b.status !== "Cancelled",
    );
    if (isBooked) {
      toast.error("This date is already booked. Please choose another date.");
      return;
    }

    if (!cardName.trim()) {
      toast.error("Please enter the cardholder name.");
      return;
    }
    const cleanCardNumber = cardNumber.replace(/\s+/g, "");
    if (!/^\d{16}$/.test(cleanCardNumber)) {
      toast.error("Please enter a valid 16-digit card number.");
      return;
    }
    if (!cardExpiry) {
      toast.error("Please select an expiry date.");
      return;
    }
    const today = new Date();
    const [expYear, expMonth] = cardExpiry.split("-").map(Number);
    if (
      expYear < today.getFullYear() ||
      (expYear === today.getFullYear() && expMonth < today.getMonth() + 1)
    ) {
      toast.error("Card expiry date cannot be in the past.");
      return;
    }
    if (!/^\d{3,4}$/.test(cardCvv)) {
      toast.error("Please enter a valid 3 or 4 digit CVV.");
      return;
    }

    setBookingLoading(true);
    try {
      const result = await facilityService.bookFacility({
        userId: user?.id || "cit_1",
        citizenName: user?.name || "Citizen",
        facilityId: selectedFacility.id,
        bookedDate: selectedDateStr,
        purpose: purpose.trim() || "Community Gathering",
      });
      toast.success(
        `Payment successful! Booking confirmed with Reference: ${result.bookingReference}`,
      );
      setSelectedFacility(null);
      setSelectedDate("");
      setSelectedDateStr("");
      await loadData();
      setMainTab("bookings");
      setConfirmBooking(false);
      setCardName("");
      setCardNumber("");
      setCardExpiry("");
      setCardCvv("");
    } catch (err) {
      toast.error(err.message || "Booking failed");
    } finally {
      setBookingLoading(false);
    }
  };

  const handleDownload = (bookingToDownload) => {
    const targetBooking = bookingToDownload?.id ? bookingToDownload : receiptBooking;
    if (!targetBooking) return;
    const printWindow = window.open('', '', 'height=600,width=800');
    if (!printWindow) {
      toast.error("Please allow popups to download the permit.");
      return;
    }
    printWindow.document.write(`
      <html>
        <head>
          <title>Permit - ${targetBooking.bookingReference}</title>
          <style>
            body { font-family: system-ui, -apple-system, sans-serif; padding: 40px; color: #111; }
            h2 { border-bottom: 2px solid #222; padding-bottom: 10px; margin-bottom: 30px; text-align: center; }
            .row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }
            .label { color: #555; }
            .val { font-weight: 600; }
            .total { font-weight: bold; font-size: 1.2em; border-top: 2px solid #222; margin-top: 20px; padding-top: 15px; }
          </style>
        </head>
        <body>
          <h2>Municipal Venue Permit</h2>
          <div class="row"><span class="label">Transaction Ref:</span> <span class="val font-mono">${targetBooking.paymentRef || "TXN-N/A"}</span></div>
          <div class="row"><span class="label">Booking Reference:</span> <span class="val font-mono">${targetBooking.bookingReference}</span></div>
          <div class="row"><span class="label">Citizen Name:</span> <span class="val">${targetBooking.citizenName || user?.name || "Citizen"}</span></div>
          <div class="row"><span class="label">Venue Name:</span> <span class="val">${targetBooking.facilityName}</span></div>
          <div class="row"><span class="label">Reserved Date:</span> <span class="val">${new Date(targetBooking.bookedDate).toLocaleDateString()}</span></div>
          <div class="row"><span class="label">Purpose:</span> <span class="val">${targetBooking.purpose}</span></div>
          <div class="row"><span class="label">Booking Status:</span> <span class="val">${targetBooking.status || "Confirmed"}</span></div>
          <div class="row total"><span class="label">Total Amount Paid:</span> <span class="val">Rs. ${targetBooking.amountPaid?.toLocaleString("en-IN")}</span></div>
          
          <script>
            window.onload = () => {
              window.print();
              setTimeout(() => window.close(), 500);
            }
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
    toast.success("Permit generated successfully!");
    setReceiptBooking(null);
  };

  const disabledDates = [
    { before: new Date() },
    ...allBookings
      .filter(
        (b) =>
          b.facilityId === selectedFacility?.id && b.status !== "Cancelled",
      )
      .map((b) => {
        const [y, m, d] = b.bookedDate.split("-").map(Number);
        return new Date(y, m - 1, d);
      }),
  ];

  const bookedModifiers = {
    booked: allBookings
      .filter(
        (b) =>
          b.facilityId === selectedFacility?.id && b.status !== "Cancelled",
      )
      .map((b) => {
        const [y, m, d] = b.bookedDate.split("-").map(Number);
        return new Date(y, m - 1, d);
      }),
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Civic Facilities & Reservations
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Explore municipal community halls and parks, reserve venues online,
            and view your confirmed booking permits.
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button
            variant={mainTab === "explore" ? "default" : "outline"}
            size="sm"
            onClick={() => setMainTab("explore")}
            className="font-semibold text-xs"
          >
            <Building2 className="mr-1.5 h-4 w-4" /> Explore Venues
          </Button>
          <Button
            variant={mainTab === "bookings" ? "default" : "outline"}
            size="sm"
            onClick={() => setMainTab("bookings")}
            className="font-semibold text-xs"
          >
            <CalendarIcon className="mr-1.5 h-4 w-4" /> My Reservations
          </Button>
        </div>
      </div>

      {mainTab === "explore" ? (
        <>
          <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center justify-between">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by facility name, location, or amenities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 h-9 text-xs sm:text-sm bg-card w-full"
              />
            </div>
            <div className="flex gap-2 shrink-0 overflow-x-auto pb-1 sm:pb-0">
              <Button
                variant={typeFilter === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setTypeFilter("all")}
                className="text-xs font-semibold"
              >
                All Facilities ({searchedFacilities.length})
              </Button>
              <Button
                variant={
                  typeFilter === "Community Hall" ? "default" : "outline"
                }
                size="sm"
                onClick={() => setTypeFilter("Community Hall")}
                className="text-xs font-semibold"
              >
                Community Halls (
                {
                  searchedFacilities.filter(
                    (f) => f.facilityType?.toLowerCase() === "community hall",
                  ).length
                }
                )
              </Button>
              <Button
                variant={typeFilter === "Park" ? "default" : "outline"}
                size="sm"
                onClick={() => setTypeFilter("Park")}
                className="text-xs font-semibold"
              >
                Public Parks (
                {
                  searchedFacilities.filter(
                    (f) => f.facilityType?.toLowerCase() === "park",
                  ).length
                }
                )
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center text-muted-foreground text-sm">
              Loading civic facilities...
            </div>
          ) : filteredFacilities.length === 0 ? (
            <EmptyState
              title="No Facilities Found"
              description="There are no civic facilities matching your current search or type filter."
              icon={Building2}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredFacilities.map((fac) => (
                <Card
                  key={fac.id}
                  className="flex flex-col justify-between overflow-hidden border shadow-md hover:shadow-xl hover:border-primary/50 transition-all duration-300 bg-card"
                >
                  <div>
                    <CardHeader className="pb-3 border-b bg-muted/20">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <Badge
                            variant="outline"
                            className="mb-2 text-[10px] font-semibold text-primary border-primary/30 bg-primary/5"
                          >
                            {fac.facilityType === "Community Hall"
                              ? "Community Hall"
                              : "Public Park"}
                          </Badge>
                          <CardTitle className="text-lg font-bold leading-tight text-foreground">
                            {fac.name}
                          </CardTitle>
                        </div>
                        <Badge
                          className={
                            fac.isActive !== false
                              ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 font-bold text-[10px] shrink-0"
                              : "bg-destructive/15 text-destructive border-destructive/30 font-bold text-[10px] shrink-0"
                          }
                        >
                          {fac.isActive !== false
                            ? "Accepting Reservations"
                            : "Deactivated"}
                        </Badge>
                      </div>
                      <CardDescription className="text-xs flex items-center gap-1.5 text-muted-foreground pt-1">
                        <MapPin className="w-3.5 h-3.5 shrink-0 text-primary" />
                        <span className="truncate">{fac.address}</span>
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4 pt-4 pb-4">
                      <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                        {fac.description}
                      </p>

                      <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-muted/50 border text-xs">
                        <div className="flex items-center gap-2">
                          <div className="p-2 rounded-lg bg-primary/10 text-primary">
                            <Users className="w-4 h-4 shrink-0" />
                          </div>
                          <div>
                            <span className="text-[10px] text-muted-foreground block">
                              Max Capacity
                            </span>
                            <span className="font-bold text-foreground">
                              {fac.capacity} Guests
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="p-2 rounded-lg bg-primary/10 text-primary">
                            <CalendarIcon className="w-4 h-4 shrink-0" />
                          </div>
                          <div>
                            <span className="text-[10px] text-muted-foreground block">
                              Daily Tariff
                            </span>
                            <span className="font-bold text-foreground">
                              ₹{fac.pricePerDay.toLocaleString("en-IN")}/day
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-1.5">
                        <div className="flex flex-wrap gap-1.5 pt-0.5">
                          {fac.amenities?.map((am, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium bg-primary/10 text-primary border border-primary/20"
                            >
                              ✓ {am}
                            </span>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </div>

                  <CardFooter className="pt-3 pb-3 border-t bg-muted/10">
                    <Button
                      onClick={() => {
                        setSelectedFacility(fac);
                        setSelectedDate("");
                        setSelectedDateStr("");
                      }}
                      disabled={fac.isActive === false}
                      className={`w-full font-bold shadow-md ${fac.isActive === false ? "bg-muted text-muted-foreground cursor-not-allowed border" : "bg-primary hover:bg-primary/90 text-primary-foreground"}`}
                    >
                      <span>
                        {fac.isActive === false
                          ? "Deactivated"
                          : "Check Calendar & Book"}
                      </span>
                      {fac.isActive !== false && (
                        <CalendarIcon className="ml-2 w-4 h-4" />
                      )}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center justify-between">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by reference code, venue name, date, purpose, amount, or status..."
                value={reservationQuery}
                onChange={(e) => setReservationQuery(e.target.value)}
                className="pl-9 h-9 text-xs sm:text-sm bg-card w-full"
              />
            </div>
            <div className="flex gap-2 shrink-0 overflow-x-auto pb-1 sm:pb-0">
              <Button
                variant={reservationFilter === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setReservationFilter("all")}
                className="text-xs font-semibold"
              >
                All Reservations ({searchedBookings.length})
              </Button>
              <Button
                variant={
                  reservationFilter === "confirmed" ? "default" : "outline"
                }
                size="sm"
                onClick={() => setReservationFilter("confirmed")}
                className="text-xs font-semibold"
              >
                Confirmed (
                {
                  searchedBookings.filter((b) => b.status === "Confirmed")
                    .length
                }
                )
              </Button>
              <Button
                variant={
                  reservationFilter === "completed" ? "default" : "outline"
                }
                size="sm"
                onClick={() => setReservationFilter("completed")}
                className="text-xs font-semibold"
              >
                Completed (
                {
                  searchedBookings.filter((b) => b.status === "Completed")
                    .length
                }
                )
              </Button>
            </div>
          </div>

          <Card className="border shadow-md">
            <CardContent className="p-0">
              {loading ? (
                <div className="p-12 text-center text-muted-foreground text-sm">
                  Loading your reservations...
                </div>
              ) : filteredBookings.length === 0 ? (
                <EmptyState
                  title="No Reservations Found"
                  description={
                    bookings.length === 0
                      ? "You haven't reserved any municipal community halls or public parks yet."
                      : "No reservations match your search or filter criteria."
                  }
                  icon={CalendarIcon}
                  inCard
                />
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Reference Code</TableHead>
                        <TableHead>Venue Name</TableHead>
                        <TableHead>Reserved Date</TableHead>
                        <TableHead>Purpose</TableHead>
                        <TableHead>Amount Paid</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">
                          Permit Action
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredBookings.map((bkg) => (
                        <TableRow key={bkg.id} className="hover:bg-muted/50">
                          <TableCell className="font-mono font-bold text-xs text-primary">
                            {bkg.bookingReference}
                          </TableCell>
                          <TableCell className="font-bold text-sm max-w-[200px] truncate">
                            {bkg.facilityName}
                          </TableCell>
                          <TableCell className="font-semibold text-xs text-foreground">
                            {new Date(bkg.bookedDate).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground max-w-[180px] truncate">
                            {bkg.purpose}
                          </TableCell>
                          <TableCell className="font-extrabold text-sm text-primary">
                            ₹{bkg.amountPaid.toLocaleString("en-IN")}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className="bg-primary/10 text-primary border-primary/20 font-bold"
                            >
                              {bkg.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDownload(bkg)}
                              className="h-8 text-xs font-semibold text-primary border-primary/30 hover:bg-primary/10"
                            >
                              <Printer className="w-3.5 h-3.5 mr-1" /> Print
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      <Dialog
        open={!!selectedFacility}
        onOpenChange={(open) => !open && setSelectedFacility(null)}
      >
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-lg font-bold">
              <Building2 className="w-5 h-5 text-primary" />
              <span>Reserve {selectedFacility?.name}</span>
            </DialogTitle>
            <DialogDescription className="text-xs">
              {selectedFacility?.address} • Tariff: ₹
              {selectedFacility?.pricePerDay?.toLocaleString("en-IN")}/day
            </DialogDescription>
          </DialogHeader>

          {selectedFacility && (
            <div className="space-y-4 py-2">
              <div className="flex flex-col md:flex-row gap-6 items-start justify-center bg-muted/30 p-4 rounded-xl border">
                <div className="flex flex-col items-center">
                  <span className="text-xs font-bold text-foreground mb-2 flex items-center gap-1.5">
                    <CalendarIcon className="w-4 h-4 text-primary" /> Select
                    Available Reservation Date
                  </span>
                  <div className="bg-background rounded-xl border p-2 shadow-sm">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={(date) => {
                        if (date) {
                          const y = date.getFullYear();
                          const m = String(date.getMonth() + 1).padStart(
                            2,
                            "0",
                          );
                          const d = String(date.getDate()).padStart(2, "0");
                          const dateStr = `${y}-${m}-${d}`;
                          const isBooked = allBookings.some(
                            (b) =>
                              b.facilityId === selectedFacility?.id &&
                              b.bookedDate === dateStr &&
                              b.status !== "Cancelled",
                          );
                          if (isBooked) {
                            toast.error(
                              "This date is already booked! Please choose another date.",
                            );
                            return;
                          }
                          setSelectedDate(date);
                          setSelectedDateStr(dateStr);
                        } else {
                          setSelectedDate("");
                          setSelectedDateStr("");
                        }
                      }}
                      disabled={disabledDates}
                      modifiers={bookedModifiers}
                      modifiersClassNames={{
                        booked:
                          "bg-destructive/20 !text-destructive font-bold line-through border border-destructive/40 !opacity-100",
                      }}
                      className="p-3"
                    />
                  </div>
                  <div className="flex items-center gap-4 mt-3 text-[11px] text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-primary inline-block"></span>
                      <span>Selected</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-destructive/20 border border-destructive/40 inline-block line-through text-destructive text-[9px] text-center font-bold">
                        ×
                      </span>
                      <span>Booked</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-muted border inline-block"></span>
                      <span>Available</span>
                    </div>
                  </div>
                </div>

                <div className="flex-1 space-y-4 w-full">
                  <div className="p-3 rounded-xl bg-card border space-y-2">
                    <span className="text-xs font-semibold text-muted-foreground block">
                      Booking Summary
                    </span>
                    <div className="flex justify-between items-center text-sm font-bold">
                      <span>Facility Tariff:</span>
                      <span>
                        ₹{selectedFacility.pricePerDay.toLocaleString("en-IN")}{" "}
                        / day
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-sm font-bold">
                      <span>Max Capacity:</span>
                      <span>{selectedFacility.capacity} Guests</span>
                    </div>
                    <div className="flex justify-between items-center text-sm font-bold border-t pt-2 mt-2">
                      <span>Selected Date:</span>
                      <span
                        className={
                          selectedDateStr
                            ? "text-primary font-extrabold"
                            : "text-muted-foreground font-normal text-xs"
                        }
                      >
                        {selectedDateStr || "No date selected"}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs font-semibold">
                      Purpose of Booking
                    </Label>
                    <Input
                      value={purpose}
                      onChange={(e) => setPurpose(e.target.value)}
                      placeholder="e.g. Community Wedding & Cultural Gathering"
                      className="text-xs h-9"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setSelectedFacility(null)}>
              Cancel
            </Button>
            <Button
              onClick={initBookSubmit}
              disabled={!selectedDateStr || bookingLoading}
              className="font-bold shadow-md bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {bookingLoading
                ? "Processing Reservation..."
                : `Confirm Reservation (₹${selectedFacility?.pricePerDay?.toLocaleString("en-IN")})`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      <Dialog open={confirmBooking} onOpenChange={(open) => !open && !bookingLoading && setConfirmBooking(false)}>
        <DialogContent className="sm:max-w-md border" onOpenAutoFocus={(e) => e.preventDefault()}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-xl font-bold">
              <CreditCard className="w-5 h-5 text-primary" />
              Secure Payment Gateway
            </DialogTitle>
            <DialogDescription className="text-xs">
              Complete your payment for booking {selectedFacility?.name} on {selectedDateStr}.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-2">
            <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-between">
              <span className="text-sm font-semibold text-primary/80">Total Amount Due</span>
              <span className="text-2xl font-extrabold text-primary">₹{selectedFacility?.pricePerDay?.toLocaleString("en-IN")}</span>
            </div>
            
            <div className="space-y-3">
              <div className="space-y-1.5">
                <Label className="text-xs font-semibold">Cardholder Name</Label>
                <Input 
                  value={cardName} 
                  onChange={(e) => setCardName(e.target.value)} 
                  placeholder="John Doe" 
                  className="text-xs h-9" 
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs font-semibold">Card Number</Label>
                <Input 
                  value={cardNumber} 
                  onChange={(e) => setCardNumber(e.target.value)} 
                  placeholder="0000 0000 0000 0000" 
                  maxLength={19} 
                  className="text-xs h-9 font-mono" 
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold">Expiry Date</Label>
                  <Input 
                    type="month" 
                    value={cardExpiry} 
                    onChange={(e) => setCardExpiry(e.target.value)} 
                    min={new Date().toISOString().slice(0, 7)}
                    className="text-xs h-9 font-mono uppercase" 
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold">CVV</Label>
                  <Input 
                    type="password" 
                    value={cardCvv} 
                    onChange={(e) => setCardCvv(e.target.value)} 
                    placeholder="•••" 
                    maxLength={4} 
                    className="text-xs h-9 font-mono" 
                  />
                </div>
              </div>
            </div>
          </div>
          
          <DialogFooter className="gap-2 sm:gap-0 mt-2">
            <Button variant="outline" onClick={() => setConfirmBooking(false)} disabled={bookingLoading}>
              Cancel
            </Button>
            <Button 
              onClick={handleBookSubmit} 
              disabled={bookingLoading}
              className="bg-primary hover:bg-primary/90 font-bold"
            >
              {bookingLoading ? "Processing..." : `Pay ₹${selectedFacility?.pricePerDay?.toLocaleString("en-IN")}`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
