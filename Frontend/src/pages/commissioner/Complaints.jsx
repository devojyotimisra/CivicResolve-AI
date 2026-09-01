import { useState, useEffect } from "react";
import { complaintService } from "@/services/complaintService";
import { adminService } from "@/services/adminService";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";
import { PhotoViewerModal } from "@/components/common/PhotoViewerModal";
import { StatusBadge } from "@/components/common/StatusBadge";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
    GitMerge,
    Settings,
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
    const [mergeComplaint, setMergeComplaint] = useState(null);
    const [masterIdInput, setMasterIdInput] = useState("");
    const [merging, setMerging] = useState(false);
    const [confirmMergeOpen, setConfirmMergeOpen] = useState(false);
    const [markingSpam, setMarkingSpam] = useState(false);
    const [confirmSpamOpen, setConfirmSpamOpen] = useState(false);
    const [spamComplaint, setSpamComplaint] = useState(null);

    const [unmergeComplaint, setUnmergeComplaint] = useState(null);
    const [unmerging, setUnmerging] = useState(false);
    const [confirmUnmergeOpen, setConfirmUnmergeOpen] = useState(false);

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
            setComplaints((prev) =>
                prev.map((c) => (c.id === data.complaint.id ? { ...c, ...data.complaint } : c))
            );
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
            const msg = error.response?.data?.detail || "Assignment failed";
            toast.error(msg);
        } finally {
            setAssigning(false);
        }
    };

    const handleOpenConfirm = () => {
        if (!mergeComplaint || !masterIdInput) {
            toast.error("Please enter a master ticket ID.");
            return;
        }

        const masterIdInt = parseInt(masterIdInput, 10);
        if (masterIdInt === mergeComplaint.id) {
            toast.error("Cannot merge a ticket into itself.");
            return;
        }

        const masterTicket = complaints.find((c) => c.id === masterIdInt);
        if (masterTicket) {
            if (masterTicket.status === "Duplicate") {
                toast.error("Cannot merge into a master ticket that is a Duplicate.");
                return;
            }
            if (masterTicket.status === "Closed") {
                const daysSinceUpdate =
                    (new Date() - new Date(masterTicket.updated_at)) / (1000 * 60 * 60 * 24);
                if (daysSinceUpdate > 30) {
                    toast.error(
                        "Cannot merge into a ticket that has been closed for more than 30 days."
                    );
                    return;
                }
            }
        }

        setConfirmMergeOpen(true);
    };

    const handleMergeConfirm = async () => {
        setMerging(true);
        try {
            await adminService.mergeComplaint(mergeComplaint.id, parseInt(masterIdInput, 10));
            toast.success("Ticket successfully merged!");
            setMergeComplaint(null);
            setMasterIdInput("");
            setConfirmMergeOpen(false);
            loadData();
        } catch (error) {
            console.error(error);
            const msg = error.message || "Merge failed";
            toast.error(msg);
        } finally {
            setMerging(false);
            setConfirmMergeOpen(false);
        }
    };

    const handleMarkSpamClick = (comp) => {
        setSpamComplaint(comp);
        setConfirmSpamOpen(true);
    };

    const handleMarkSpamConfirm = async () => {
        if (!spamComplaint) return;
        setMarkingSpam(true);
        try {
            await complaintService.markAsSpam(spamComplaint.id);
            toast.success("Ticket marked as spam.");
            loadData();
        } catch (error) {
            console.error(error);
            toast.error(error.message || "Failed to mark as spam.");
        } finally {
            setMarkingSpam(false);
            setConfirmSpamOpen(false);
            setSpamComplaint(null);
        }
    };

    const handleUnmergeClick = (comp) => {
        setUnmergeComplaint(comp);
        setConfirmUnmergeOpen(true);
    };

    const handleUnmergeConfirm = async () => {
        setUnmerging(true);
        try {
            await adminService.unmergeComplaint(unmergeComplaint.id);
            toast.success("Ticket successfully un-merged!");
            setUnmergeComplaint(null);
            setConfirmUnmergeOpen(false);
            loadData();
        } catch (error) {
            console.error(error);
            toast.error(error.message || "Failed to un-merge.");
        } finally {
            setUnmerging(false);
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
                            <SelectItem value="Duplicate">Duplicate</SelectItem>
                            <SelectItem value="Rejected">Rejected</SelectItem>
                            <SelectItem value="Closed">Closed</SelectItem>
                            <SelectItem value="Spam">Spam</SelectItem>
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
                                        <TableHead className="w-[60px]">SL/No</TableHead>
                                        <TableHead className="w-[80px]">Ticket ID</TableHead>
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
                                            <TableCell className="font-mono text-xs text-muted-foreground/70">
                                                {index + 1}
                                            </TableCell>
                                            <TableCell className="font-mono font-bold text-xs text-muted-foreground">
                                                {comp.id}
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
                                                {comp.status === "Duplicate" &&
                                                    comp.resolutionNote && (
                                                        <span className="block text-[11px] font-bold text-orange-600 mt-1 truncate">
                                                            {(() => {
                                                                const match =
                                                                    comp.resolutionNote.match(
                                                                        /master ticket ([A-Z0-9-]+)/
                                                                    );
                                                                if (match) {
                                                                    const masterToken = match[1];
                                                                    const master = complaints.find(
                                                                        (c) =>
                                                                            c.token === masterToken
                                                                    );
                                                                    if (master) {
                                                                        return comp.resolutionNote.replace(
                                                                            masterToken,
                                                                            `#${master.id}`
                                                                        );
                                                                    }
                                                                }
                                                                return comp.resolutionNote;
                                                            })()}
                                                        </span>
                                                    )}
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
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            className="h-8 px-2 border border-transparent hover:border-primary/20 hover:bg-primary/5 text-primary text-xs font-bold gap-1.5 inline-flex items-center"
                                                        >
                                                            <Settings className="h-3.5 w-3.5" />
                                                            <span>Actions</span>
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent
                                                        align="end"
                                                        className="w-48"
                                                    >
                                                        <DropdownMenuLabel>
                                                            Actions
                                                        </DropdownMenuLabel>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem
                                                            onClick={() => handleViewDetails(comp)}
                                                            className="cursor-pointer"
                                                        >
                                                            <Eye className="w-4 h-4 mr-2 text-primary" />{" "}
                                                            View Details
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                comp.status === "Duplicate"
                                                                    ? handleUnmergeClick(comp)
                                                                    : setSelectedComplaint(comp)
                                                            }
                                                            className="cursor-pointer"
                                                        >
                                                            <UserPlus className="w-4 h-4 mr-2 text-primary" />{" "}
                                                            {comp.status === "Duplicate"
                                                                ? "Un-Merge"
                                                                : "Assign/Reassign"}
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => setMergeComplaint(comp)}
                                                            className="cursor-pointer"
                                                        >
                                                            <GitMerge className="w-4 h-4 mr-2 text-orange-600" />{" "}
                                                            Merge
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            disabled={markingSpam}
                                                            onClick={() =>
                                                                handleMarkSpamClick(comp)
                                                            }
                                                            className="cursor-pointer text-red-600 focus:text-red-600 focus:bg-red-500/10"
                                                        >
                                                            <ShieldAlert className="w-4 h-4 mr-2" />{" "}
                                                            Mark as Spam
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
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
                            Select an operational field officer to dispatch for this ticket.
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
                                        {(() => {
                                            const availableOfficers = officers.filter(
                                                (o) =>
                                                    o.id !== selectedComplaint.assignedOfficerId &&
                                                    o.id !== selectedComplaint.assigned_officer_id
                                            );

                                            if (availableOfficers.length === 0) {
                                                return (
                                                    <SelectItem value="none" disabled>
                                                        No officers available
                                                    </SelectItem>
                                                );
                                            }

                                            const groupedOfficers = availableOfficers.reduce(
                                                (acc, off) => {
                                                    const dept =
                                                        off.department || "Unassigned Department";
                                                    if (!acc[dept]) acc[dept] = [];
                                                    acc[dept].push(off);
                                                    return acc;
                                                },
                                                {}
                                            );

                                            return Object.entries(groupedOfficers).map(
                                                ([dept, deptOfficers]) => (
                                                    <SelectGroup key={dept}>
                                                        <SelectLabel className="text-primary bg-muted/50">
                                                            {dept}
                                                        </SelectLabel>
                                                        {deptOfficers.map((off) => {
                                                            return (
                                                                <SelectItem
                                                                    key={off.id}
                                                                    value={off.id}
                                                                >
                                                                    {off.name} (Badge: {off.badgeId}
                                                                    )
                                                                </SelectItem>
                                                            );
                                                        })}
                                                    </SelectGroup>
                                                )
                                            );
                                        })()}
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
                open={!!mergeComplaint}
                onOpenChange={(open) => !open && setMergeComplaint(null)}
            >
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Merge Complaint</DialogTitle>
                        <DialogDescription>
                            Are you sure you want to merge this complaint (ID: {mergeComplaint?.id}
                            )? Please enter the ID of the Master Ticket to merge it into.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                        <Input
                            type="number"
                            placeholder="Master Ticket ID (e.g. 42)"
                            value={masterIdInput}
                            onChange={(e) => setMasterIdInput(e.target.value)}
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setMergeComplaint(null)}>
                            Cancel
                        </Button>
                        <Button onClick={handleOpenConfirm} disabled={!masterIdInput}>
                            Confirm Merge
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <ConfirmationModal
                isOpen={confirmMergeOpen}
                onClose={() => setConfirmMergeOpen(false)}
                onConfirm={handleMergeConfirm}
                title="Confirm Duplicate Merge"
                description={`Are you absolutely sure you want to merge Ticket ID: ${mergeComplaint?.id} into Master Ticket ID: ${masterIdInput}? This ticket will become a duplicate.`}
                confirmText="Yes, Merge it"
                variant="destructive"
                isLoading={merging}
            />

            <ConfirmationModal
                isOpen={confirmUnmergeOpen}
                onClose={() => setConfirmUnmergeOpen(false)}
                onConfirm={handleUnmergeConfirm}
                title="Confirm Un-Merge"
                description={`Are you sure you want to un-merge Ticket ID: ${unmergeComplaint?.id} from its master? It will be restored to Submitted state.`}
                confirmText="Yes, Un-Merge"
                variant="destructive"
                isLoading={unmerging}
            />

            <ConfirmationModal
                isOpen={confirmSpamOpen}
                onClose={() => setConfirmSpamOpen(false)}
                onConfirm={handleMarkSpamConfirm}
                title="Confirm Mark as Spam"
                description={`Are you sure you want to mark Ticket ID: ${spamComplaint?.id} as spam? This action might flag the user.`}
                confirmText="Yes, Mark Spam"
                variant="destructive"
                isLoading={markingSpam}
            />

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
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-start">
                                <div className="flex flex-col gap-4 h-full justify-between">
                                    <div className="p-4 rounded-xl bg-muted/50 border text-xs space-y-3 shrink-0">
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
                                        <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground shrink-0">
                                            Description
                                        </h4>
                                        <p className="text-sm leading-relaxed text-foreground bg-muted/30 p-4 rounded-lg border flex-1 flex flex-col justify-center">
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

                                    {viewingComplaint?.status === "Duplicate" ? (
                                        <Card className="flex-1 border shadow-sm bg-orange-500/10 flex flex-col justify-center p-5">
                                            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                                <div className="space-y-1">
                                                    <span className="text-xs font-bold uppercase tracking-wider text-orange-600 flex items-center gap-1.5">
                                                        <GitMerge className="w-4 h-4 text-orange-600" />
                                                        <span>Merged Ticket Information</span>
                                                    </span>
                                                    <p className="text-xs text-muted-foreground">
                                                        This ticket has been marked as a duplicate.
                                                    </p>
                                                    {viewingComplaint?.resolutionNote && (
                                                        <p className="text-xs italic font-semibold text-foreground/80 mt-1.5 border-l-2 border-orange-500/50 pl-2">
                                                            {(() => {
                                                                const match =
                                                                    viewingComplaint.resolutionNote.match(
                                                                        /master ticket ([A-Z0-9-]+)/
                                                                    );
                                                                if (match) {
                                                                    const masterToken = match[1];
                                                                    const master = complaints.find(
                                                                        (c) =>
                                                                            c.token === masterToken
                                                                    );
                                                                    if (master) {
                                                                        return viewingComplaint.resolutionNote.replace(
                                                                            masterToken,
                                                                            `#${master.id}`
                                                                        );
                                                                    }
                                                                }
                                                                return viewingComplaint.resolutionNote;
                                                            })()}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </Card>
                                    ) : (
                                        <Card className="flex-1 border shadow-sm bg-muted/20 flex flex-col justify-center p-5">
                                            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                                <div className="space-y-1">
                                                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                                                        <FileCheck className="w-4 h-4 text-primary" />
                                                        <span>
                                                            Evidence Uploaded by Field Officer
                                                        </span>
                                                    </span>
                                                    <p className="text-xs text-muted-foreground">
                                                        Resolution verification proof submitted by
                                                        field crew
                                                    </p>
                                                    {viewingComplaint?.resolutionNote && (
                                                        <p className="text-xs italic text-foreground/80 mt-1.5 border-l-2 border-primary/50 pl-2">
                                                            {(() => {
                                                                const match =
                                                                    viewingComplaint.resolutionNote.match(
                                                                        /master ticket ([A-Z0-9-]+)/
                                                                    );
                                                                if (match) {
                                                                    const masterToken = match[1];
                                                                    const master = complaints.find(
                                                                        (c) =>
                                                                            c.token === masterToken
                                                                    );
                                                                    if (master) {
                                                                        return viewingComplaint.resolutionNote.replace(
                                                                            masterToken,
                                                                            `#${master.id}`
                                                                        );
                                                                    }
                                                                }
                                                                return viewingComplaint.resolutionNote;
                                                            })()}
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
                                                            {
                                                                viewingComplaint.resolutionPhotos
                                                                    .length
                                                            }
                                                            )
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
                                    )}
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
