import { useState, useEffect } from "react";
import { complaintService } from "@/services/complaintService";
import { adminService } from "@/services/adminService";
import { PhotoViewerModal } from "@/components/common/PhotoViewerModal";
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
import {
    Search,
    UserPlus,
    ShieldAlert,
    Eye,
    MapPin,
    User,
    Camera,
    EyeOff,
    Clock,
    CheckCircle2,
    FileCheck,
} from "lucide-react";
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

    const [viewingComplaint, setViewingComplaint] = useState(null);
    const [complaintUpdates, setComplaintUpdates] = useState([]);
    const [viewingImage, setViewingImage] = useState(null);

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
        } catch (error) {
            console.error(error);
            toast.error("Failed to load master city complaints log");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleViewDetails = async (comp) => {
        try {
            const data = await complaintService.getComplaintDetail(comp.id);
            setViewingComplaint(data.complaint);
            setComplaintUpdates(data.updates || []);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load details");
        }
    };

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
                officer?.name || "Field Officer"
            );
            toast.success(`Ticket assigned to ${officer?.name}! Officer notified.`);
            setSelectedComplaint(null);
            setSelectedOfficerId("");
            loadData();
        } catch (error) {
            console.error(error);
            toast.error("Assignment failed");
        } finally {
            setAssigning(false);
        }
    };

    const filtered = complaints.filter((comp) => {
        const query = searchQuery.toLowerCase();
        const matchesSearch = Object.values(comp).some(
            (val) =>
                val !== null && val !== undefined && val.toString().toLowerCase().includes(query)
        );

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
                    Executive supervisory view across all departments. Monitor progress and reassign
                    critical issues.
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
                            <SelectItem value="en-route-onsite">En Route / On Site</SelectItem>
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
                                        <TableHead>#</TableHead>
                                        <TableHead>Severity</TableHead>
                                        <TableHead>Hazard Summary</TableHead>
                                        <TableHead>Department</TableHead>
                                        <TableHead>Assigned Officer</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {filtered.map((comp, index) => (
                                        <TableRow key={comp.id} className="hover:bg-muted/50">
                                            <TableCell className="font-mono font-bold text-xs text-muted-foreground">
                                                {index + 1}
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
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleViewDetails(comp)}
                                                        className="h-8 text-xs font-bold text-foreground hover:bg-primary/10 hover:text-primary"
                                                    >
                                                        <Eye className="w-3.5 h-3.5 mr-1" />
                                                        View
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        disabled={
                                                            comp.severity !== "Critical" ||
                                                            comp.status === "Resolved" ||
                                                            comp.status === "Closed"
                                                        }
                                                        onClick={() => setSelectedComplaint(comp)}
                                                        className={`h-8 text-xs font-bold ${
                                                            comp.severity === "Critical" &&
                                                            comp.status !== "Resolved" &&
                                                            comp.status !== "Closed"
                                                                ? "text-primary border-primary/30 hover:bg-primary/10"
                                                                : "opacity-50 cursor-not-allowed border-muted/50 text-muted-foreground"
                                                        }`}
                                                    >
                                                        <UserPlus className="w-3.5 h-3.5 mr-1" />{" "}
                                                        Assign/Reassign
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
                <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-primary">
                            <UserPlus className="w-5 h-5" />
                            <span>Reassign Field Officer</span>
                        </DialogTitle>
                        <DialogDescription className="text-xs">
                            Select an operational field officer to dispatch for the critical ticket.
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
                                                (o) =>
                                                    o.department === selectedComplaint.department &&
                                                    o.id !== selectedComplaint.assignedOfficerId &&
                                                    o.id !== selectedComplaint.assigned_officer_id
                                            )
                                            .map((off) => (
                                                <SelectItem key={off.id} value={off.id}>
                                                    {off.name} (Badge: {off.badgeId})
                                                </SelectItem>
                                            ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    )}

                    <DialogFooter>
                        <Button variant="outline" onClick={() => setSelectedComplaint(null)}>
                            Cancel
                        </Button>
                        <Button
                            onClick={handleAssignConfirm}
                            disabled={assigning || !selectedOfficerId}
                            className="font-bold shadow-md bg-primary hover:bg-primary/90 text-primary-foreground"
                        >
                            {assigning ? "Assigning..." : "Confirm Reassignment"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog
                open={!!viewingComplaint}
                onOpenChange={(open) => {
                    if (!open && !viewingImage) {
                        setViewingComplaint(null);
                        setComplaintUpdates([]);
                    }
                }}
            >
                <DialogContent
                    onOpenAutoFocus={(e) => e.preventDefault()}
                    className="max-w-4xl border-2 border-primary/20 shadow-2xl bg-card/95 backdrop-blur-xl p-0 overflow-hidden"
                >
                    <div className="max-h-[85vh] overflow-y-auto p-6 flex flex-col gap-4">
                        <DialogHeader className="border-b pb-4 space-y-2">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-muted-foreground">
                                        Submitted on{" "}
                                        {viewingComplaint?.createdAt &&
                                            new Date(
                                                viewingComplaint.createdAt
                                            ).toLocaleDateString()}
                                    </span>
                                    <Badge variant="outline" className="w-fit ml-2">
                                        {viewingComplaint?.department ||
                                            viewingComplaint?.category ||
                                            (viewingComplaint?.status === "Rejected"
                                                ? "N/A (Rejected)"
                                                : "Pending")}
                                    </Badge>
                                </div>
                                <div className="flex items-center gap-2">
                                    <StatusBadge
                                        status={viewingComplaint?.status}
                                        className="text-xs py-0.5 px-2.5"
                                    />
                                </div>
                            </div>
                            <DialogTitle className="text-2xl font-extrabold text-foreground text-left leading-tight">
                                {viewingComplaint?.title}
                            </DialogTitle>
                        </DialogHeader>

                        <div className="flex flex-col gap-6 w-full pt-2">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-stretch">
                                <div className="flex flex-col gap-4 h-full justify-between">
                                    <div className="p-4 rounded-xl bg-muted/50 border text-xs space-y-2 flex-1">
                                        <div className="flex items-start gap-2.5">
                                            <MapPin className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                                            <div>
                                                <span className="font-semibold text-foreground block">
                                                    Landmark
                                                </span>
                                                <span className="text-muted-foreground leading-relaxed">
                                                    {viewingComplaint?.location}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-2.5 pt-2 border-t">
                                            <User className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                                            <div>
                                                <span className="font-semibold text-foreground block">
                                                    Assigned Officer
                                                </span>
                                                <span className="text-muted-foreground">
                                                    {viewingComplaint?.assignedOfficerName ||
                                                        viewingComplaint?.assignedOfficer ||
                                                        (viewingComplaint?.status === "Rejected"
                                                            ? "N/A (Rejected)"
                                                            : "Awaiting Department Assignment")}
                                                </span>
                                                <span className="block text-[11px] text-muted-foreground mt-0.5">
                                                    Dept:{" "}
                                                    {viewingComplaint?.department ||
                                                        (viewingComplaint?.status === "Rejected"
                                                            ? "N/A"
                                                            : "Pending")}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-1.5 flex-1 flex flex-col">
                                        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                            Description
                                        </h4>
                                        <p className="text-sm leading-relaxed text-foreground bg-muted/30 p-4 rounded-lg border flex-1">
                                            {viewingComplaint?.description}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-4 h-full justify-between">
                                    <Card className="flex-1 border shadow-sm bg-muted/20 flex flex-col justify-center p-5">
                                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                            <div className="space-y-1">
                                                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                                                    <Camera className="w-4 h-4 text-primary" />
                                                    <span>Evidence Uploaded by Citizen</span>
                                                </span>
                                                <p className="text-xs text-muted-foreground">
                                                    Original hazard evidence submitted by reporter
                                                </p>
                                            </div>
                                            {viewingComplaint?.submittedPhotos?.length > 0 ? (
                                                <div className="flex flex-wrap gap-2 justify-end w-full sm:w-auto">
                                                    <Button
                                                        type="button"
                                                        size="sm"
                                                        className="h-10 w-36 px-4 font-bold shadow-sm"
                                                        onClick={() =>
                                                            setViewingImage({
                                                                photos: viewingComplaint.submittedPhotos,
                                                                initialIndex: 0,
                                                                title: "Evidence Gallery",
                                                            })
                                                        }
                                                    >
                                                        <Camera className="w-4 h-4 mr-2" />
                                                        View (
                                                        {viewingComplaint.submittedPhotos.length})
                                                    </Button>
                                                </div>
                                            ) : (
                                                <div className="flex flex-wrap gap-2 justify-end w-full sm:w-auto">
                                                    <div className="flex items-center justify-center gap-2 h-10 w-36 px-4 rounded-md bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                                                        <EyeOff className="w-4 h-4" />
                                                        <span>Not Uploaded</span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </Card>

                                    <Card className="flex-1 border shadow-sm bg-muted/20 flex flex-col justify-center p-5">
                                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                            <div className="space-y-1">
                                                <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                                                    <FileCheck className="w-4 h-4 text-primary" />
                                                    <span>Evidence Uploaded by Field Officer</span>
                                                </span>
                                                <p className="text-xs text-muted-foreground">
                                                    Resolution verification proof submitted by field
                                                    crew
                                                </p>
                                                {viewingComplaint?.resolutionNote && (
                                                    <p className="text-xs italic text-foreground/80 mt-1.5 border-l-2 border-primary/50 pl-2">
                                                        {viewingComplaint.resolutionNote}
                                                    </p>
                                                )}
                                            </div>
                                            {viewingComplaint?.resolutionPhotos?.length > 0 ? (
                                                <div className="flex flex-wrap gap-2 justify-end w-full sm:w-auto">
                                                    <Button
                                                        type="button"
                                                        size="sm"
                                                        className="h-10 w-36 px-4 font-bold shadow-sm"
                                                        onClick={() =>
                                                            setViewingImage({
                                                                photos: viewingComplaint.resolutionPhotos,
                                                                initialIndex: 0,
                                                                title: "Evidence Uploaded by Field Officer",
                                                            })
                                                        }
                                                    >
                                                        <Camera className="w-4 h-4 mr-2" />
                                                        View (
                                                        {viewingComplaint.resolutionPhotos.length})
                                                    </Button>
                                                </div>
                                            ) : (
                                                <div className="flex flex-wrap gap-2 justify-end w-full sm:w-auto">
                                                    <div className="flex items-center justify-center gap-2 h-10 w-36 px-4 rounded-md bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                                                        <EyeOff className="w-4 h-4" />
                                                        <span>Not Uploaded</span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </Card>
                                </div>
                            </div>

                            <div className="w-full space-y-6 pt-4 border-t">
                                <div className="space-y-3">
                                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                                        <Clock className="w-4 h-4 text-primary" />
                                        <span>Resolution Timeline</span>
                                    </h4>

                                    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
                                        {complaintUpdates &&
                                            complaintUpdates.length > 0 &&
                                            complaintUpdates.map((item, idx) => {
                                                const isLatest =
                                                    idx === complaintUpdates.length - 1;
                                                return (
                                                    <div
                                                        key={idx}
                                                        className="relative flex items-start gap-3"
                                                    >
                                                        <div
                                                            className={`absolute -left-6 top-1 h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                                                                isLatest
                                                                    ? "bg-primary border-primary text-primary-foreground shadow-md scale-110"
                                                                    : "bg-muted border-primary/40 text-primary"
                                                            }`}
                                                        >
                                                            <CheckCircle2 className="w-3 h-3" />
                                                        </div>
                                                        <div className="flex-1 rounded-lg bg-muted/40 p-3 border text-xs space-y-1">
                                                            <div className="flex items-center justify-between font-semibold text-foreground">
                                                                <span>
                                                                    Status: {item.newStatus}
                                                                </span>
                                                                <span className="text-[11px] font-normal text-muted-foreground">
                                                                    {item.createdAt
                                                                        ? new Date(
                                                                              item.createdAt
                                                                          ).toLocaleString()
                                                                        : ""}
                                                                </span>
                                                            </div>
                                                            {item.note ? (
                                                                <p className="text-muted-foreground mt-1">
                                                                    {item.note}
                                                                </p>
                                                            ) : null}
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            <PhotoViewerModal
                isOpen={!!viewingImage}
                onClose={() => setViewingImage(null)}
                photos={viewingImage?.photos || []}
                initialIndex={viewingImage?.initialIndex || 0}
                title={viewingImage?.title}
                description="Submitted image evidence."
            />
        </div>
    );
};
