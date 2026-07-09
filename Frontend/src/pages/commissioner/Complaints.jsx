import React, { useState, useEffect } from "react";
import { complaintService } from "@/services/complaintService";
import { adminService } from "@/services/adminService";
import { StatusBadge } from "@/components/common/StatusBadge";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Search, UserPlus, ShieldAlert } from "lucide-react";
import { toast } from "sonner";

export const CommissionerComplaints = () => {
  const [complaints, setComplaints] = useState([]);
  const [officers, setOfficers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [deptFilter, setDeptFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [selectedOfficerId, setSelectedOfficerId] = useState("");
  const [assigning, setAssigning] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [compData, offData, deptData] = await Promise.all([
        complaintService.getAllComplaints(),
        adminService.getOfficers(),
        adminService.getDepartments(),
      ]);
      setComplaints(compData);
      setOfficers(offData);
      setDepartments(deptData);
    } catch {
      toast.error("Failed to load master city complaints log");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAssignConfirm = async () => {
    if (!selectedComplaint || !selectedOfficerId) {
      toast.error("Please select a field officer to assign.");
      return;
    }
    setAssigning(true);
    try {
      const officer = officers.find((o) => o.id === selectedOfficerId);
      await complaintService.assignOfficer(
        selectedComplaint.id,
        selectedOfficerId,
        officer?.name || "Field Officer",
      );
      toast.success(`Ticket assigned to ${officer?.name}! Officer notified.`);
      setSelectedComplaint(null);
      setSelectedOfficerId("");
      loadData();
    } catch {
      toast.error("Assignment failed");
    } finally {
      setAssigning(false);
    }
  };

  const filtered = complaints.filter((comp) => {
    const matchesSearch =
      comp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.token.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.location.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesDept = deptFilter === "all" || comp.department === deptFilter;
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "en-route-onsite"
        ? comp.status === "En Route" || comp.status === "On Site"
        : comp.status?.toLowerCase() === statusFilter.toLowerCase());
    const matchesSeverity =
      severityFilter === "all" ||
      comp.severity?.toLowerCase() === severityFilter.toLowerCase();

    return matchesSearch && matchesDept && matchesStatus && matchesSeverity;
  });

  return (
    <div className="space-y-6 pb-10">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          City-Wide Master Complaints Log
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Executive supervisory view across all departments. Monitor progress
          and reassign critical issues.
        </p>
      </div>

      <Card className="bg-card/80 border shadow-sm">
        <CardContent className="p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search token, title or street..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 text-xs h-9"
            />
          </div>

          <Select value={deptFilter} onValueChange={setDeptFilter}>
            <SelectTrigger className="text-xs h-9">
              <SelectValue placeholder="Filter by Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map((d) => (
                <SelectItem key={d.id} value={d.name}>
                  {d.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={severityFilter} onValueChange={setSeverityFilter}>
            <SelectTrigger className="text-xs h-9">
              <SelectValue placeholder="Filter by Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="Critical">Critical</SelectItem>
              <SelectItem value="Normal">Normal</SelectItem>
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="text-xs h-9">
              <SelectValue placeholder="Filter by Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="Submitted">Submitted (Unassigned)</SelectItem>
              <SelectItem value="Assigned">Assigned</SelectItem>
              <SelectItem value="en-route-onsite">
                En Route / On Site
              </SelectItem>
              <SelectItem value="In Progress">In Progress</SelectItem>
              <SelectItem value="Resolved">Resolved</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card className="border shadow-md">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 text-center text-muted-foreground text-sm">
              Loading master city reports...
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              title="No Reports Found"
              description={
                complaints.length === 0
                  ? "There are no civic complaints logged across any municipal zone."
                  : "No complaints match your selected supervisory search or filter criteria."
              }
              icon={ShieldAlert}
              inCard
            />
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Token Code</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Hazard Summary</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Assigned Officer</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((comp) => (
                    <TableRow key={comp.id} className="hover:bg-muted/50">
                      <TableCell className="font-mono font-bold text-xs text-primary">
                        {comp.token}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            comp.severity === "Critical"
                              ? "bg-destructive hover:bg-destructive/90 text-destructive-foreground border-transparent text-[10px] uppercase px-1.5 py-0 h-4 leading-4"
                              : "bg-secondary text-secondary-foreground text-[10px] uppercase px-1.5 py-0 h-4 leading-4 hover:bg-secondary/80"
                          }
                        >
                          {comp.severity || "Normal"}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium text-sm max-w-[200px] truncate">
                        <span>{comp.title}</span>
                        <span className="block text-[11px] text-muted-foreground truncate font-normal">
                          {comp.location}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        <span className="font-bold text-foreground block">
                          {comp.department}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs font-semibold">
                        {comp.assignedOfficerName ? (
                          <span className="text-primary font-bold">
                            {comp.assignedOfficerName}
                          </span>
                        ) : (
                          <span className="text-muted-foreground font-semibold">
                            Unassigned
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={comp.status} />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={comp.severity !== "Critical" || comp.status === "Resolved" || comp.status === "Closed"}
                            onClick={() => setSelectedComplaint(comp)}
                            className={`h-8 text-xs font-bold ${
                              comp.severity === "Critical" && comp.status !== "Resolved" && comp.status !== "Closed"
                                ? "text-primary border-primary/30 hover:bg-primary/10"
                                : "opacity-50 cursor-not-allowed border-muted/50 text-muted-foreground"
                            }`}
                          >
                            <UserPlus className="w-3.5 h-3.5 mr-1" /> Assign/Reassign
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={!!selectedComplaint}
        onOpenChange={(open) => !open && setSelectedComplaint(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              <UserPlus className="w-5 h-5" />
              <span>Reassign Field Officer</span>
            </DialogTitle>
            <DialogDescription className="text-xs">
              Select an operational field officer to dispatch for critical
              ticket{" "}
              <strong className="font-mono font-bold text-foreground">
                {selectedComplaint?.token}
              </strong>
              .
            </DialogDescription>
          </DialogHeader>

          {selectedComplaint && (
            <div className="space-y-4 py-3">
              <div className="p-3 rounded-lg bg-muted text-xs space-y-1">
                <div className="font-bold text-foreground">
                  {selectedComplaint.title}
                </div>
                <div className="text-muted-foreground">
                  Department: <strong>{selectedComplaint.department}</strong>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground">
                  Select Field Officer
                </label>
                <Select
                  value={selectedOfficerId}
                  onValueChange={setSelectedOfficerId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose Officer from Directory" />
                  </SelectTrigger>
                  <SelectContent>
                    {officers
                      .filter(
                        (o) => o.department === selectedComplaint.department,
                      )
                      .map((off) => (
                        <SelectItem key={off.id} value={off.id}>
                          {off.name} (Badge: {off.badgeId})
                        </SelectItem>
                      ))}
                    {officers
                      .filter(
                        (o) => o.department !== selectedComplaint.department,
                      )
                      .map((off) => (
                        <SelectItem key={off.id} value={off.id}>
                          {off.name} ({off.department})
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setSelectedComplaint(null)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAssignConfirm}
              disabled={assigning || !selectedOfficerId}
              className="font-bold shadow-md bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {assigning ? "Assigning..." : "Confirm Officer Dispatch"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
