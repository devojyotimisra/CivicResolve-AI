import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { billService } from "@/services/billService";
import { facilityService } from "@/services/facilityService";
import { StatsCard } from "@/components/common/StatsCard";
import { Receipt, Calendar } from "lucide-react";
import { toast } from "sonner";

export const CitizenDashboard = () => {
    const { user } = useAuth();
    const [bills, setBills] = useState([]);
    const [bookings, setBookings] = useState([]);
    useEffect(() => {
        const loadDashboardData = async () => {
            if (!user) return;
            try {
                const [billData, bookData] = await Promise.all([
                    billService.getUserBills(user.id),
                    facilityService.getUserBookings(user.id),
                ]);
                setBills(billData);
                setBookings(bookData);
            } catch {
                toast.error("Failed to load dashboard metrics");
            }
        };

        loadDashboardData();
    }, [user]);

    const pendingBillsCount = bills.filter((b) => b.status === "Pending").length;
    const pendingBillsAmount = bills
        .filter((b) => b.status === "Pending")
        .reduce((acc, b) => acc + (b.amount || 0), 0);
    const confirmedBookingsCount = bookings.filter((b) => b.status === "Confirmed").length;
    const upcomingBookingsCount = bookings.filter(
        (b) => new Date(b.bookedDate) >= new Date()
    ).length;

    return (
        <div className="space-y-10 pb-12 max-w-6xl mx-auto min-h-[calc(100vh-10rem)] flex flex-col justify-start">
            <div className="bg-muted/40 flex flex-col md:flex-row md:items-center justify-between gap-4 py-12 sm:py-16 px-8 sm:px-12 rounded-3xl border shadow-sm">
                <div className="space-y-2">
                    <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
                        Welcome back, {user?.name}
                    </h1>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 flex-1">
                <StatsCard
                    title="Pending Utility Bills"
                    value={`₹${pendingBillsAmount.toLocaleString("en-IN")}`}
                    icon={Receipt}
                    description={`${pendingBillsCount} bills awaiting online settlement`}
                    color="primary"
                    trend={pendingBillsCount > 0 ? "Action Required" : "All Clear"}
                    trendUp={pendingBillsCount === 0}
                    className="min-h-[260px] sm:min-h-[300px] flex flex-col justify-center rounded-2xl shadow-lg border-border/80"
                />
                <StatsCard
                    title="Confirmed Bookings"
                    value={confirmedBookingsCount}
                    icon={Calendar}
                    description={`${upcomingBookingsCount} upcoming reservation${upcomingBookingsCount !== 1 ? "s" : ""} scheduled`}
                    color="primary"
                    className="min-h-[260px] sm:min-h-[300px] flex flex-col justify-center rounded-2xl shadow-lg border-border/80"
                />
            </div>
        </div>
    );
};
