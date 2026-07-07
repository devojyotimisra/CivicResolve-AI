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
import { Building2, ShieldAlert, Clock, Layers } from "lucide-react";
import { toast } from "sonner";

export const CommissionerDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true);
      try {
        const data = await adminService.getDashboardStats();
        setStats(data);
      } catch (err) {
        toast.error("Failed to load executive city metrics");
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  if (loading || !stats) {
    return (
      <div className="p-12 text-center text-muted-foreground">
        Loading executive dashboard metrics...
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-muted/40 border shadow-sm">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground mt-1">
            Commissioner Dashboard: {user?.name}
          </h1>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Total Civic Reports"
          value={stats.totalComplaints ?? 0}
          icon={Building2}
          description="Logged across all departments"
          color="primary"
        />
        <StatsCard
          title="Active Field Caseload"
          value={stats.activeComplaints ?? 0}
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
      </div>

      <Card className="border shadow-md">
        <CardHeader className="pb-3 border-b flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base">
              Departmental Caseload Distribution
            </CardTitle>
            <CardDescription className="text-xs">
              Active vs Resolved tickets by civic engineering department.
            </CardDescription>
          </div>
          <Layers className="w-5 h-5 text-primary" />
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          {stats.departmentBreakdown?.map((dept, idx) => {
            const percentage =
              Math.round((dept.count / stats.totalComplaints) * 100) || 0;
            return (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-foreground">{dept.name}</span>
                  <span className="text-muted-foreground">
                    {dept.count} Tickets ({percentage}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
};
