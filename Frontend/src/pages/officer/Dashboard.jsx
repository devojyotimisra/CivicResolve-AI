import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { complaintService } from "@/services/complaintService";
import { StatsCard } from "@/components/common/StatsCard";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PhotoViewerModal } from "@/components/common/PhotoViewerModal";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
    CheckSquare,
    CheckCircle2,
    MapPin,
    Clock,
    Search,
    Camera,
    FileCheck,
    EyeOff,
    Upload,
} from "lucide-react";
import { toast } from "sonner";

export const OfficerDashboard = () => {
    const { user } = useAuth();
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [viewingImage, setViewingImage] = useState(null);
    const [resolutionPhoto, setResolutionPhoto] = useState("");
    const [resolutionFile, setResolutionFile] = useState(null);
    const [resolutionNote, setResolutionNote] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [showResolveForm, setShowResolveForm] = useState(false);
    const [ticketDrafts, setTicketDrafts] = useState({});

    useEffect(() => {
        const loadTickets = async () => {
            if (!user) return;
            setLoading(true);
            try {
                const data = await complaintService.getOfficerComplaints(user.id);
                setTickets(data);
                if (selectedTicket) {
                    const updatedSelected = data.find((t) => t.id === selectedTicket.id);
                    if (updatedSelected) setSelectedTicket(updatedSelected);
                }
            } catch (error) {
                console.error(error);
                toast.error("Failed to load assigned field tickets");
            } finally {
                setLoading(false);
            }
        };
        loadTickets();
    }, [user]);

    const openModal = (ticket) => {
        setSelectedTicket(ticket);
        const draft = ticketDrafts[ticket.id] || {};
        const photoVal = draft.photo || "";
        const fileVal = draft.file || null;
        const noteVal = draft.note !== undefined ? draft.note : "";
        setResolutionPhoto(photoVal);
        setResolutionFile(fileVal);
        setResolutionNote(noteVal);
        setShowResolveForm(
            ticket.status === "In Progress" ||
                !!photoVal ||
                (draft.note !== undefined && draft.note !== "")
        );
    };

    const handleStatusChange = async (ticketId, nextStatus, noteMsg) => {
        try {
            const updated = await complaintService.updateComplaintStatus(
                ticketId,
                nextStatus,
                noteMsg || `Officer status updated to ${nextStatus} via field modal.`
            );
            toast.success(`Ticket status advanced to: ${nextStatus}!`);
            setTickets((prev) =>
                prev.map((t) => (t.id === ticketId ? { ...t, ...updated, status: nextStatus } : t))
            );
            if (selectedTicket && selectedTicket.id === ticketId) {
                setSelectedTicket({ ...selectedTicket, ...updated, status: nextStatus });
                if (nextStatus === "In Progress") setShowResolveForm(true);
            }
        } catch (error) {
            console.error(error);
            toast.error("Failed to update status");
        }
    };

    const handlePhotoUpload = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            setResolutionFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setResolutionPhoto(reader.result);
                if (selectedTicket) {
                    setTicketDrafts((prev) => ({
                        ...prev,
                        [selectedTicket.id]: {
                            ...prev[selectedTicket.id],
                            photo: reader.result,
                            file: file,
                        },
                    }));
                }
            };
            reader.readAsDataURL(file);
        }
    };

    const handleNoteChange = (val) => {
        setResolutionNote(val);
        if (selectedTicket) {
            setTicketDrafts((prev) => ({
                ...prev,
                [selectedTicket.id]: {
                    ...prev[selectedTicket.id],
                    note: val,
                },
            }));
        }
    };

    const handleRemovePhoto = () => {
        setResolutionPhoto("");
        setResolutionFile(null);
        if (selectedTicket) {
            setTicketDrafts((prev) => ({
                ...prev,
                [selectedTicket.id]: {
                    ...prev[selectedTicket.id],
                    photo: "",
                    file: null,
                },
            }));
        }
    };

    const handleResolveSubmit = async (e) => {
        e.preventDefault();
        if (!selectedTicket) return;
        if (!resolutionFile || !resolutionNote.trim()) {
            toast.error(
                "Please provide both photographic proof and an engineering resolution note."
            );
            return;
        }
        setSubmitting(true);
        try {
            const updated = await complaintService.updateComplaintStatus(
                selectedTicket.id,
                "Resolved",
                `Resolved by Officer ${user?.name || "Field Officer"}: ${resolutionNote.trim()}`,
                user?.id,
                resolutionFile,
                resolutionNote.trim()
            );
            toast.success("Ticket successfully marked as RESOLVED! Proof uploaded.");
            setTickets((prev) =>
                prev.map((t) =>
                    t.id === selectedTicket.id
                        ? {
                              ...t,
                              ...updated,
                              status: "Resolved",
                              resolutionPhotos: updated.resolutionPhotos || [],
                              resolutionNote: resolutionNote.trim(),
                          }
                        : t
                )
            );
            setSelectedTicket({
                ...selectedTicket,
                ...updated,
                status: "Resolved",
                resolutionPhotos: updated.resolutionPhotos || [],
                resolutionNote: resolutionNote.trim(),
            });
            setShowResolveForm(false);
            setTicketDrafts((prev) => {
                const next = { ...prev };
                delete next[selectedTicket.id];
                return next;
            });
        } catch (error) {
            console.error(error);
            toast.error("Resolution submission failed");
        } finally {
            setSubmitting(false);
        }
    };

    const filteredTickets = tickets.filter((t) => {
        const query = searchQuery.toLowerCase();
        return (
            t.title?.toLowerCase().includes(query) ||
            t.token?.toLowerCase().includes(query) ||
            t.location?.toLowerCase().includes(query) ||
            t.status?.toLowerCase().includes(query) ||
            t.department?.toLowerCase().includes(query)
        );
    });

    const activeTickets = filteredTickets.filter(
        (t) => t.status !== "Resolved" && t.status !== "Closed"
    );
    const resolvedTickets = filteredTickets.filter(
        (t) => t.status === "Resolved" || t.status === "Closed"
    );
    const totalResolvedCount = tickets.filter(
        (t) => t.status === "Resolved" || t.status === "Closed"
    ).length;

    return (
        <div className="space-y-8 pb-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-muted/40 border shadow-sm">
                <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
                    Field Officer Dashboard: {user?.name}
                </h1>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <StatsCard
                    title="Active Assigned Tickets"
                    value={
                        tickets.filter((t) => t.status !== "Resolved" && t.status !== "Closed")
                            .length
                    }
                    icon={CheckSquare}
                    description="Pending field inspection & resolution"
                    color="primary"
                />
                <StatsCard
                    title="Total Tickets Resolved"
                    value={totalResolvedCount}
                    icon={CheckCircle2}
                    description="Verified with photographic proof"
                    color="primary"
                />
            </div>

            <Card className="bg-card/80 border shadow-sm">
                <CardContent className="p-4">
                    <div className="relative">
                        <Search className="absolute left-3.5 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Unified Search: filter by token, hazard title, location, or status..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 h-10 text-xs sm:text-sm bg-background/50"
                        />
                    </div>
                </CardContent>
            </Card>

            <Tabs defaultValue="assigned" className="space-y-6">
                <TabsList className="grid w-full sm:w-[420px] grid-cols-2 h-11 p-1 bg-muted/60 border rounded-xl">
                    <TabsTrigger
                        value="assigned"
                        className="font-bold text-xs sm:text-sm rounded-lg data-[state=active]:shadow-md"
                    >
                        Assigned Tickets ({activeTickets.length})
                    </TabsTrigger>
                    <TabsTrigger
                        value="resolved"
                        className="font-bold text-xs sm:text-sm rounded-lg data-[state=active]:shadow-md"
                    >
                        Resolved Tickets ({resolvedTickets.length})
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="assigned" className="space-y-4">
                    <Card className="border shadow-md">
                        <CardHeader className="pb-4">
                            <CardTitle className="text-lg">Assigned Field Tickets</CardTitle>
                            <CardDescription className="text-xs">
                                Active maintenance tickets requiring field inspection. Click the eye
                                icon to view details and update live status.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-5">
                            {loading ? (
                                <div className="p-12 text-center text-muted-foreground text-sm">
                                    Loading assigned tickets...
                                </div>
                            ) : activeTickets.length === 0 ? (
                                <EmptyState
                                    title="No Active Field Tickets"
                                    description={
                                        searchQuery
                                            ? "No active tickets match your search criteria."
                                            : "You have cleared all assigned maintenance tickets! Excellent job."
                                    }
                                />
                            ) : (
                                <div className="overflow-x-auto">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead className="w-[50px]">#</TableHead>
                                                <TableHead>Hazard Summary</TableHead>
                                                <TableHead>Location</TableHead>
                                                <TableHead className="w-[200px]">
                                                    Current Status
                                                </TableHead>
                                                <TableHead className="text-right w-[140px]">
                                                    View Details
                                                </TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {activeTickets.map((t, index) => (
                                                <TableRow key={t.id} className="hover:bg-muted/50">
                                                    <TableCell className="font-mono font-bold text-xs text-muted-foreground">
                                                        {index + 1}
                                                    </TableCell>
                                                    <TableCell className="font-medium text-sm max-w-[280px] xl:max-w-[360px] truncate">
                                                        {t.title}
                                                        <span className="block text-[11px] text-muted-foreground truncate font-normal">
                                                            {t.department}
                                                        </span>
                                                    </TableCell>
                                                    <TableCell className="text-xs text-muted-foreground max-w-[280px] xl:max-w-[400px] truncate">
                                                        {t.location}
                                                    </TableCell>
                                                    <TableCell>
                                                        <StatusBadge status={t.status} />
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <Button
                                                            variant="default"
                                                            size="icon"
                                                            onClick={() => openModal(t)}
                                                            title="View Details & Live Status"
                                                            className="w-24 font-semibold shadow-lg"
                                                        >
                                                            View
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
                </TabsContent>

                <TabsContent value="resolved" className="space-y-4">
                    <Card className="border shadow-md">
                        <CardHeader className="pb-4">
                            <CardTitle className="text-lg">Resolved & Closed Tickets</CardTitle>
                            <CardDescription className="text-xs">
                                History of tickets completed by field crews with photographic proof.
                                Click the eye icon to view timeline.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="p-5">
                            {loading ? (
                                <div className="p-12 text-center text-muted-foreground text-sm">
                                    Loading resolved tickets...
                                </div>
                            ) : resolvedTickets.length === 0 ? (
                                <EmptyState
                                    title="No Resolved Tickets"
                                    description={
                                        searchQuery
                                            ? "No resolved tickets match your search criteria."
                                            : "No resolved tickets found in your history yet."
                                    }
                                />
                            ) : (
                                <div className="overflow-x-auto">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead className="w-[50px]">#</TableHead>
                                                <TableHead>Hazard Summary</TableHead>
                                                <TableHead>Location</TableHead>
                                                <TableHead className="w-[160px]">
                                                    Final Status
                                                </TableHead>
                                                <TableHead className="text-right w-[120px]">
                                                    View Details
                                                </TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {resolvedTickets.map((t, index) => (
                                                <TableRow key={t.id} className="hover:bg-muted/50">
                                                    <TableCell className="font-mono font-bold text-xs text-muted-foreground">
                                                        {index + 1}
                                                    </TableCell>
                                                    <TableCell className="font-medium text-sm max-w-[320px] xl:max-w-[450px] truncate">
                                                        {t.title}
                                                        <span className="block text-[11px] text-muted-foreground truncate font-normal">
                                                            {t.department}
                                                        </span>
                                                    </TableCell>
                                                    <TableCell className="text-xs text-muted-foreground max-w-[280px] xl:max-w-[400px] truncate">
                                                        {t.location}
                                                    </TableCell>
                                                    <TableCell>
                                                        <StatusBadge status={t.status} />
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <Button
                                                            variant="default"
                                                            size="icon"
                                                            onClick={() => openModal(t)}
                                                            title="View Timeline & Resolution Proof"
                                                            className="w-24 font-semibold shadow-lg"
                                                        >
                                                            View
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
                </TabsContent>
            </Tabs>

            <Dialog
                open={!!selectedTicket}
                onOpenChange={(open) => {
                    if (!open && !viewingImage) setSelectedTicket(null);
                }}
            >
                <DialogContent
                    onOpenAutoFocus={(e) => e.preventDefault()}
                    className="max-w-4xl border-2 border-primary/20 shadow-2xl bg-card/95 backdrop-blur-xl p-0 overflow-hidden"
                >
                    {selectedTicket && (
                        <div className="max-h-[85vh] overflow-y-auto p-6 flex flex-col gap-6">
                            <DialogHeader className="border-b pb-4 space-y-2">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-muted-foreground">
                                            Submitted on{" "}
                                            {selectedTicket.createdAt &&
                                                new Date(
                                                    selectedTicket.createdAt
                                                ).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <StatusBadge
                                            status={selectedTicket.status}
                                            className="text-xs py-0.5 px-2.5"
                                        />
                                    </div>
                                </div>
                                <DialogTitle className="text-xl sm:text-2xl font-extrabold text-foreground text-left leading-tight">
                                    {selectedTicket.title}
                                </DialogTitle>
                            </DialogHeader>

                            <div className="flex flex-col gap-6 w-full">
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
                                                        {selectedTicket.location}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="flex justify-between pt-2 border-t text-[11px] text-muted-foreground">
                                                <span>
                                                    Department:{" "}
                                                    <strong className="text-foreground">
                                                        {selectedTicket.department}
                                                    </strong>
                                                </span>
                                            </div>
                                        </div>

                                        <div className="space-y-1.5 flex-1 flex flex-col">
                                            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                                Description
                                            </h4>
                                            <p className="text-sm leading-relaxed text-foreground bg-muted/30 p-4 rounded-lg border flex-1">
                                                {selectedTicket.description}
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
                                                        Original hazard evidence submitted by
                                                        reporter
                                                    </p>
                                                </div>
                                                {selectedTicket?.submittedPhotos?.length > 0 ? (
                                                    <div className="flex flex-wrap gap-2 justify-end w-full sm:w-auto">
                                                        <Button
                                                            type="button"
                                                            size="sm"
                                                            className="h-10 px-4 font-bold shadow-sm"
                                                            onClick={() =>
                                                                setViewingImage({
                                                                    photos: selectedTicket.submittedPhotos,
                                                                    initialIndex: 0,
                                                                    title: "Evidence Gallery",
                                                                })
                                                            }
                                                        >
                                                            <Camera className="w-4 h-4 mr-2" />
                                                            View (
                                                            {selectedTicket.submittedPhotos.length})
                                                        </Button>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                                                        <EyeOff className="w-4 h-4" />
                                                        <span>Not Uploaded</span>
                                                    </div>
                                                )}
                                            </div>
                                        </Card>

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
                                                    {selectedTicket.resolutionNote && (
                                                        <p className="text-xs italic text-foreground/80 mt-1.5 border-l-2 border-primary/50 pl-2">
                                                            {selectedTicket.resolutionNote}
                                                        </p>
                                                    )}
                                                </div>
                                                {selectedTicket?.resolutionPhotos?.length > 0 ? (
                                                    <Button
                                                        type="button"
                                                        size="lg"
                                                        className="w-full sm:w-auto h-12 px-8 font-bold shrink-0 shadow-lg"
                                                        onClick={() =>
                                                            setViewingImage({
                                                                photos: selectedTicket.resolutionPhotos,
                                                                initialIndex: 0,
                                                                title: "Evidence Uploaded by Field Officer",
                                                            })
                                                        }
                                                    >
                                                        View (
                                                        {selectedTicket.resolutionPhotos.length})
                                                    </Button>
                                                ) : (
                                                    <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                                                        <EyeOff className="w-4 h-4" />
                                                        <span>Not Uploaded</span>
                                                    </div>
                                                )}
                                            </div>
                                        </Card>
                                    </div>
                                </div>

                                <div className="w-full space-y-4 pt-4 border-t">
                                    {selectedTicket.status !== "Resolved" &&
                                    selectedTicket.status !== "Closed" ? (
                                        <div className="space-y-3 w-full">
                                            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                                                <Clock className="w-4 h-4 text-primary" />
                                                <span>Advance Live Status</span>
                                            </h4>
                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full">
                                                <Button
                                                    variant={
                                                        selectedTicket.status === "Assigned"
                                                            ? "default"
                                                            : "outline"
                                                    }
                                                    size="sm"
                                                    disabled={selectedTicket.status !== "Assigned"}
                                                    onClick={() =>
                                                        handleStatusChange(
                                                            selectedTicket.id,
                                                            "En Route",
                                                            "Officer dispatched and en route to site."
                                                        )
                                                    }
                                                    className="text-xs sm:text-sm font-bold h-11 shadow-sm"
                                                >
                                                    1. En Route
                                                </Button>
                                                <Button
                                                    variant={
                                                        selectedTicket.status === "En Route"
                                                            ? "default"
                                                            : "outline"
                                                    }
                                                    size="sm"
                                                    disabled={selectedTicket.status !== "En Route"}
                                                    onClick={() =>
                                                        handleStatusChange(
                                                            selectedTicket.id,
                                                            "On Site",
                                                            "Officer arrived on site. Inspection underway."
                                                        )
                                                    }
                                                    className="text-xs sm:text-sm font-bold h-11 shadow-sm"
                                                >
                                                    2. On Site
                                                </Button>
                                                <Button
                                                    variant={
                                                        selectedTicket.status === "On Site"
                                                            ? "default"
                                                            : "outline"
                                                    }
                                                    size="sm"
                                                    disabled={selectedTicket.status !== "On Site"}
                                                    onClick={() =>
                                                        handleStatusChange(
                                                            selectedTicket.id,
                                                            "In Progress",
                                                            "Maintenance work commenced on site."
                                                        )
                                                    }
                                                    className="text-xs sm:text-sm font-bold h-11 shadow-sm"
                                                >
                                                    3. In Progress
                                                </Button>
                                                <Button
                                                    variant={
                                                        showResolveForm ||
                                                        selectedTicket.status === "Resolved"
                                                            ? "default"
                                                            : "outline"
                                                    }
                                                    size="sm"
                                                    disabled={
                                                        selectedTicket.status !== "In Progress"
                                                    }
                                                    onClick={() => setShowResolveForm(true)}
                                                    className="text-xs sm:text-sm font-bold h-11 bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    4. Resolve
                                                </Button>
                                            </div>

                                            {(showResolveForm ||
                                                selectedTicket.status === "In Progress") && (
                                                <Card className="border-2 border-primary/30 shadow-lg bg-card mt-4 w-full">
                                                    <CardHeader className="pb-3 border-b bg-muted/30">
                                                        <CardTitle className="text-base flex items-center gap-2 text-foreground">
                                                            <FileCheck className="w-4 h-4 text-primary" />
                                                            <span>
                                                                Submit Resolution Proof & Note
                                                            </span>
                                                        </CardTitle>
                                                        <CardDescription className="text-xs">
                                                            Required to verify fulfillment and
                                                            notify citizen.
                                                        </CardDescription>
                                                    </CardHeader>
                                                    <CardContent className="pt-4">
                                                        <form
                                                            onSubmit={handleResolveSubmit}
                                                            className="space-y-4"
                                                        >
                                                            <div className="space-y-3">
                                                                <Label className="text-xs font-semibold">
                                                                    Upload Resolution Photo
                                                                </Label>
                                                                {!resolutionPhoto ? (
                                                                    <label
                                                                        htmlFor="modal-res-photo"
                                                                        className="flex flex-col items-center justify-center gap-2 p-6 border-2 border-dashed rounded-lg border-muted-foreground/25 hover:border-primary/50 bg-muted/20 hover:bg-muted/40 transition-colors cursor-pointer text-center"
                                                                    >
                                                                        <div className="p-3 rounded-full bg-background shadow-sm border">
                                                                            <Upload className="w-6 h-6 text-muted-foreground" />
                                                                        </div>
                                                                        <div>
                                                                            <span className="text-sm font-semibold text-foreground">
                                                                                Click to upload
                                                                                evidence
                                                                            </span>
                                                                            <p className="text-xs text-muted-foreground mt-0.5">
                                                                                PNG, JPG, MP4, WEBP
                                                                                up to 20MB
                                                                            </p>
                                                                        </div>
                                                                        <input
                                                                            id="modal-res-photo"
                                                                            type="file"
                                                                            accept="image/*,video/*"
                                                                            className="hidden"
                                                                            onChange={
                                                                                handlePhotoUpload
                                                                            }
                                                                        />
                                                                    </label>
                                                                ) : (
                                                                    <div className="relative w-full max-h-56 overflow-hidden rounded-lg border bg-muted">
                                                                        <div
                                                                            className="w-full h-56 cursor-pointer group relative"
                                                                            onClick={() =>
                                                                                setViewingImage({
                                                                                    photos: [
                                                                                        resolutionPhoto,
                                                                                    ],
                                                                                    initialIndex: 0,
                                                                                    title: "Uploaded Resolution Preview",
                                                                                })
                                                                            }
                                                                        >
                                                                            {resolutionPhoto.startsWith(
                                                                                "data:video"
                                                                            ) ? (
                                                                                <video
                                                                                    src={
                                                                                        resolutionPhoto
                                                                                    }
                                                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                                                                />
                                                                            ) : (
                                                                                <img
                                                                                    src={
                                                                                        resolutionPhoto
                                                                                    }
                                                                                    alt="Uploaded evidence preview"
                                                                                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                                                                                />
                                                                            )}
                                                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold">
                                                                                Click to View Full
                                                                                Image
                                                                            </div>
                                                                        </div>
                                                                        <Button
                                                                            type="button"
                                                                            variant="destructive"
                                                                            size="sm"
                                                                            className="absolute top-2 right-2 text-xs h-7 px-3 shadow"
                                                                            onClick={(e) => {
                                                                                e.stopPropagation();
                                                                                handleRemovePhoto();
                                                                            }}
                                                                        >
                                                                            Remove Photo
                                                                        </Button>
                                                                    </div>
                                                                )}
                                                            </div>

                                                            <div className="space-y-2">
                                                                <Label
                                                                    htmlFor="modal-res-note"
                                                                    className="text-xs font-semibold"
                                                                >
                                                                    Engineering Resolution Summary
                                                                    Note
                                                                </Label>
                                                                <Textarea
                                                                    id="modal-res-note"
                                                                    rows={3}
                                                                    placeholder="Detail the repairs completed and verification steps..."
                                                                    value={resolutionNote}
                                                                    onChange={(e) =>
                                                                        handleNoteChange(
                                                                            e.target.value
                                                                        )
                                                                    }
                                                                    required
                                                                    className="text-xs"
                                                                />
                                                            </div>

                                                            <div className="flex justify-end gap-2 pt-1">
                                                                <Button
                                                                    type="submit"
                                                                    size="sm"
                                                                    className="font-bold bg-primary hover:bg-primary/90 text-primary-foreground"
                                                                    disabled={submitting}
                                                                >
                                                                    {submitting
                                                                        ? "Submitting..."
                                                                        : "Mark as RESOLVED"}
                                                                </Button>
                                                            </div>
                                                        </form>
                                                    </CardContent>
                                                </Card>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="space-y-3 p-5 rounded-xl bg-muted/40 border text-xs w-full">
                                            <div className="flex items-center justify-between border-b pb-2">
                                                <div className="flex items-center gap-1.5 font-bold text-foreground text-sm">
                                                    <FileCheck className="w-4 h-4 text-primary" />
                                                    <span>Resolution Status & Summary</span>
                                                </div>
                                                <StatusBadge status={selectedTicket.status} />
                                            </div>
                                            {selectedTicket.resolutionNote && (
                                                <p className="text-muted-foreground italic bg-background p-4 rounded-lg border text-sm leading-relaxed">
                                                    "{selectedTicket.resolutionNote}"
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
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
