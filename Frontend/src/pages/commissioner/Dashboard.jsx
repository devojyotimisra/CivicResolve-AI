import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { adminService } from "@/services/adminService";
import { StatsCard } from "@/components/common/StatsCard";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Building2, ShieldAlert, Clock, IndianRupee } from "lucide-react";
import { toast } from "sonner";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Legend,
} from "recharts";

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#8dd1e1",
  "#f472b6",
];
const STATUS_COLORS = ["#f59e0b", "#10b981"];
const SEVERITY_COLORS = ["#3b82f6", "#ef4444"];
const REVENUE_COLORS = ["#8b5cf6", "#ec4899"];

export const CommissionerDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true);
      try {
        const data = await adminService.getSystemAnalytics();
        setStats(data);
      } catch {
        toast.error("Failed to load executive city metrics");
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
      <div className="rounded-xl border bg-card px-8 py-6 shadow-sm text-center">
        <p className="text-lg font-medium">Loading Dashboard...</p>
        <p className="text-sm text-muted-foreground mt-1">
          Please wait while we fetch the latest analytics.
        </p>
      </div>
    </div>
    );
  }

  const activeComplaints = stats.totalComplaints - stats.resolvedComplaints;
  const normalComplaints = stats.totalComplaints - stats.criticalComplaints;

  const statusData = [
    { name: "Active", value: activeComplaints },
    { name: "Finished", value: stats.resolvedComplaints },
  ];

  const severityData = [
    { name: "Normal", value: normalComplaints },
    { name: "Severe", value: stats.criticalComplaints },
  ];

  const revenueData = [
    { name: "Utility Bills", value: stats.billRevenue },
    { name: "Facility Bookings", value: stats.bookingRevenue },
  ];

  const formatCurrency = (value) => `₹${value.toLocaleString("en-IN")}`;

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 rounded-3xl border bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/20 dark:to-amber-950/20 p-8 shadow-lg">
        <div className="space-y-1">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
           <p className="text-sm text-muted-foreground">
            City analytics overview and performance insights
          </p>
            Commissioner Dashboard: {user?.name}
          </h1>
        </div>
      </div>

      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          title="Total Civic Reports"
          value={stats.totalComplaints ?? 0}
          icon={Building2}
          description="Logged across all departments"
          color="primary"
        />
        <StatsCard
          title="Active Field Caseload"
          value={activeComplaints}
          icon={Clock}
          description="Currently en route, on site, or in progress"
          color="primary"
        />
        <StatsCard
          title="Critical Safety Hazards"
          value={stats.criticalComplaints ?? 0}
          icon={ShieldAlert}
          description="Immediate emergency attention required"
          color="destructive"
        />
        <StatsCard
          title="Total City Revenue"
          value={formatCurrency(stats.totalRevenue ?? 0)}
          icon={IndianRupee}
          description="Combined bills and bookings revenue"
          color="primary"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="rounded-2xl border bg-card shadow-sm hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="pb-4 border-b bg-muted/30 rounded-t-2xl">
            <CardTitle className="text-base font-bold">
              Tickets by Department
            </CardTitle>
            <CardDescription className="text-xs">
              Distribution of cases across civic engineering departments.
            </CardDescription>
          </CardHeader>
            <CardContent className="h-[400px] mt-4">
              {stats.byDepartment.length === 0 || stats.totalComplaints === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm font-medium">
                  No department distribution data available
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.byDepartment}
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {stats.byDepartment.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card className="border shadow-md">
            <CardHeader className="pb-2 border-b">
              <CardTitle className="text-base font-bold">
                Active vs Finished Tickets
              </CardTitle>
              <CardDescription className="text-xs">
                Current operational status of all reported cases.
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] mt-4">
              {stats.totalComplaints === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm font-medium">
                  No ticket status data available
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      innerRadius={75}
                      outerRadius={120}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={STATUS_COLORS[index % STATUS_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card className="border shadow-md">
            <CardHeader className="pb-2 border-b">
              <CardTitle className="text-base font-bold">
                Normal vs Severe Tickets
              </CardTitle>
              <CardDescription className="text-xs">
                Priority breakdown of civic incidents.
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] mt-4">
              {stats.totalComplaints === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm font-medium">
                  No priority breakdown data available
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={severityData}
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {severityData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={SEVERITY_COLORS[index % SEVERITY_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card className="border shadow-md">
            <CardHeader className="pb-2 border-b">
              <CardTitle className="text-base font-bold">
                Total Revenue Distribution
              </CardTitle>
              <CardDescription className="text-xs">
                Financial breakdown between Utility Bills and Facility Bookings.
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] mt-4">
              {stats.totalRevenue === 0 ? (
                <div className="h-full flex items-center justify-center text-muted-foreground text-sm font-medium">
                  No revenue data available
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={revenueData}
                      cx="50%"
                      cy="50%"
                      innerRadius={75}
                      outerRadius={120}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {revenueData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={REVENUE_COLORS[index % REVENUE_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <RechartsTooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>

      <Card className="border shadow-md mt-6">
        <CardHeader className="pb-2 border-b">
          <CardTitle className="text-base font-bold">
            7-Day Operational Trend
          </CardTitle>
          <CardDescription className="text-xs">
            Daily throughput comparison of tickets filed vs. tickets resolved.
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[350px] mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={stats.trend}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis dataKey="day" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar
                dataKey="filed"
                name="Tickets Filed"
                fill="#8884d8"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="resolved"
                name="Tickets Resolved"
                fill="#82ca9d"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};
