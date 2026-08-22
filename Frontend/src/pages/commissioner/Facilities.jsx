import { useState, useEffect } from "react";
import { facilityService } from "@/services/facilityService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
    DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
    Plus,
    Pencil,
    ToggleLeft,
    ToggleRight,
    Users,
    Search,
    CalendarIcon,
    Trash2,
    MapPin,
} from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

const BLANK_FORM = {
    name: "",
    facilityType: "",
    address: "",
    pincode: "",
    pricePerDay: "",
    capacity: "",
    description: "",
    amenities: "",
};

export const CommissionerFacilities = () => {
    const [mainTab, setMainTab] = useState("facilities");
    const [facilities, setFacilities] = useState([]);
    const [facilityTypes, setFacilityTypes] = useState([]);
    const [allBookings, setAllBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [typeFilter, setTypeFilter] = useState("all");
    const [reservationQuery, setReservationQuery] = useState("");

    const [dialogOpen, setDialogOpen] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState(BLANK_FORM);
    const [saving, setSaving] = useState(false);
    const [toggling, setToggling] = useState(null);
    const [deletingFacility, setDeletingFacility] = useState(null);
    const [isDeletingFacility, setIsDeletingFacility] = useState(false);

    const load = async () => {
        setLoading(true);
        try {
            const [facData, bkgData, typeData] = await Promise.all([
                facilityService.getAllFacilities(),
                facilityService.getAllBookings(),
                facilityService.getFacilityTypes(),
            ]);
            setFacilities(facData);
            setAllBookings(bkgData);
            setFacilityTypes(typeData);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load municipal data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const filtered = facilities.filter((f) => {
        const matchesSearch =
            f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            f.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
            f.facilityType.toLowerCase().includes(searchQuery.toLowerCase());

        const matchesStatus =
            statusFilter === "all" ||
            (statusFilter === "active" && f.isActive) ||
            (statusFilter === "inactive" && !f.isActive);

        const matchesType = typeFilter === "all" || f.facilityType === typeFilter;

        return matchesSearch && matchesStatus && matchesType;
    });

    const searchedBookings = allBookings.filter((bkg) => {
        if (reservationQuery.trim() !== "") {
            const keywords = reservationQuery.toLowerCase().trim().split(/\s+/).filter(Boolean);
            return keywords.every((query) => {
                const matchRef = (bkg.bookingReference || "").toLowerCase().includes(query);
                const matchFac = (bkg.facilityName || "").toLowerCase().includes(query);
                const matchPurpose = (bkg.purpose || "").toLowerCase().includes(query);
                const matchAmount = (bkg.amountPaid || "").toString().includes(query);
                const matchDate = (bkg.bookedDate || "").includes(query);
                return matchRef || matchFac || matchPurpose || matchAmount || matchDate;
            });
        }
        return true;
    });

    const filteredBookings = searchedBookings;

    const openNew = () => {
        setEditing(null);
        setForm(BLANK_FORM);
        setDialogOpen(true);
    };

    const openEdit = (fac) => {
        setEditing(fac);
        setForm({
            name: fac.name || "",
            facilityType: fac.facilityType || "",
            address: fac.address || "",
            pincode: fac.pincode || "",
            pricePerDay: fac.pricePerDay || "",
            capacity: fac.capacity || "",
            description: fac.description || "",
            amenities: Array.isArray(fac.amenities)
                ? fac.amenities.join(", ")
                : fac.amenities || "",
        });
        setDialogOpen(true);
    };

    const handleToggle = async (fac) => {
        setToggling(fac.id);
        try {
            await facilityService.toggleFacilityStatus(fac.id, fac.isActive);
            if (fac.isActive) {
                toast.error(`"${fac.name}" is now Inactive.`);
            } else {
                toast.success(`"${fac.name}" is now Active.`);
            }
            load();
        } catch (error) {
            console.error(error);
            toast.error("Failed to update facility status");
        } finally {
            setToggling(null);
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        if (
            !form.name ||
            !form.address ||
            !form.pricePerDay ||
            !form.capacity ||
            !form.facilityType
        ) {
            toast.error("Please fill in all required fields.");
            return;
        }

        if (form.address.trim().length < 5) {
            toast.error("Address must be at least 5 characters long");
            return;
        }
        setSaving(true);
        try {
            const payload = {
                ...form,
                amenities:
                    form.amenities && typeof form.amenities === "string"
                        ? form.amenities
                              .split(",")
                              .map((a) => a.trim())
                              .filter(Boolean)
                        : Array.isArray(form.amenities)
                          ? form.amenities
                          : [],
            };
            if (editing) {
                payload.id = editing.id;
            }
            await facilityService.saveFacility(payload);
            toast.success(
                editing
                    ? `Facility "${form.name}" updated successfully!`
                    : `Facility "${form.name}" created successfully!`
            );
            setDialogOpen(false);
            setEditing(null);
            setForm(BLANK_FORM);
            load();
        } catch (err) {
            toast.error(err.message || "Failed to save facility");
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteFacility = async () => {
        if (!deletingFacility) return;
        setIsDeletingFacility(true);
        try {
            await facilityService.deleteFacility(deletingFacility.id);
            toast.success(`Facility "${deletingFacility.name}" deleted!`);
            setDeletingFacility(null);
            load();
        } catch (err) {
            toast.error(err.message || "Failed to delete facility");
        } finally {
            setIsDeletingFacility(false);
        }
    };

    return (
        <div className="space-y-6 pb-10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <Building2 className="w-6 h-6 text-primary" /> Manage Municipal Facilities
                    </h1>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                        Control all civic venues — toggle availability and add new municipal
                        locations, and manage reservations.
                    </p>
                </div>
                <div className="flex gap-2 shrink-0 flex-wrap sm:flex-nowrap">
                    <Button
                        variant={mainTab === "facilities" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMainTab("facilities")}
                        className="font-semibold text-xs"
                    >
                        <Building2 className="mr-1.5 h-4 w-4" /> Manage Venues
                    </Button>
                    <Button
                        variant={mainTab === "bookings" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMainTab("bookings")}
                        className="font-semibold text-xs"
                    >
                        <CalendarIcon className="mr-1.5 h-4 w-4" /> All Reservations
                    </Button>
                </div>
            </div>

            {mainTab === "facilities" ? (
                <>
                    <div className="flex flex-col lg:flex-row gap-4 items-stretch">
                        <Card className="bg-card/80 border shadow-sm flex-1">
                            <CardContent className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                                <div className="relative">
                                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        placeholder="Search facilities by name, type or address..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="pl-9 text-xs h-9"
                                    />
                                </div>

                                <Select value={statusFilter} onValueChange={setStatusFilter}>
                                    <SelectTrigger className="text-xs h-9">
                                        <SelectValue placeholder="Filter by Status" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="all">All Statuses</SelectItem>
                                        <SelectItem value="active">Active</SelectItem>
                                        <SelectItem value="inactive">Inactive</SelectItem>
                                    </SelectContent>
                                </Select>

                                <Select value={typeFilter} onValueChange={setTypeFilter}>
                                    <SelectTrigger className="text-xs h-9">
                                        <SelectValue placeholder="Filter by Type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="all">All Types</SelectItem>
                                        {facilityTypes.map((t) => (
                                            <SelectItem key={t.id} value={t.name}>
                                                {t.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </CardContent>
                        </Card>

                        <Card className="bg-card/80 border shadow-sm shrink-0 flex items-center">
                            <CardContent className="p-4 w-full">
                                <Button
                                    onClick={openNew}
                                    className="font-bold shadow-md h-9 w-full"
                                >
                                    <Plus className="w-4 h-4 mr-2" /> Add New Facility
                                </Button>
                            </CardContent>
                        </Card>
                    </div>

                    {loading ? (
                        <div className="p-12 text-center text-muted-foreground text-sm">
                            Loading municipal facilities...
                        </div>
                    ) : filtered.length === 0 ? (
                        <EmptyState
                            title="No Facilities Found"
                            description={
                                facilities.length === 0
                                    ? "No civic facilities found."
                                    : "No facilities match your selected filters."
                            }
                            icon={Building2}
                        />
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {filtered.map((fac) => (
                                <Card
                                    key={fac.id}
                                    className="flex flex-col justify-between overflow-hidden border shadow-md hover:shadow-xl hover:border-primary/50 transition-all duration-300 bg-card"
                                >
                                    <div>
                                        <CardHeader className="pb-3 pt-4 border-b bg-muted/20">
                                            <div className="flex items-center justify-between gap-2 mb-2">
                                                <Badge
                                                    variant="outline"
                                                    className="text-[10px] font-semibold text-primary border-primary/30 bg-primary/5"
                                                >
                                                    {fac.facilityType}
                                                </Badge>
                                                <Badge
                                                    className={
                                                        fac.isActive
                                                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 font-bold text-[10px] shrink-0"
                                                            : "bg-destructive/15 text-destructive border-destructive/30 font-bold text-[10px] shrink-0"
                                                    }
                                                >
                                                    {fac.isActive ? "Active" : "Inactive"}
                                                </Badge>
                                            </div>
                                            <CardTitle className="text-lg font-bold leading-tight text-foreground">
                                                {fac.name}
                                            </CardTitle>
                                            <CardDescription className="text-xs flex items-center gap-1.5 text-muted-foreground pt-1">
                                                <MapPin className="w-3.5 h-3.5 shrink-0 text-primary" />
                                                <span className="truncate">
                                                    {fac.address}
                                                    {fac.pincode ? ` - ${fac.pincode}` : ""}
                                                </span>
                                            </CardDescription>
                                        </CardHeader>

                                        <CardContent className="space-y-4 pt-4 pb-4">
                                            {fac.description && (
                                                <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                                                    {fac.description}
                                                </p>
                                            )}

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
                                                            ₹
                                                            {fac.pricePerDay?.toLocaleString(
                                                                "en-IN"
                                                            )}
                                                            /day
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            {fac.amenities && fac.amenities.length > 0 && (
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
                                            )}
                                        </CardContent>
                                    </div>

                                    <CardContent className="p-4 pt-0 mt-auto">
                                        <div className="flex items-center gap-2 pt-3 border-t">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => openEdit(fac)}
                                                className="flex-1 font-semibold text-xs border-primary/30 text-primary hover:bg-primary/10"
                                            >
                                                <Pencil className="w-3.5 h-3.5 mr-1.5" /> Edit
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => handleToggle(fac)}
                                                disabled={toggling === fac.id}
                                                className={`flex-1 font-semibold text-xs ${fac.isActive ? "text-destructive border-destructive/30 hover:bg-destructive/10" : "text-emerald-600 border-emerald-500/30 hover:bg-emerald-500/10"}`}
                                            >
                                                {fac.isActive ? (
                                                    <ToggleLeft className="w-3.5 h-3.5 mr-1.5" />
                                                ) : (
                                                    <ToggleRight className="w-3.5 h-3.5 mr-1.5" />
                                                )}
                                                {toggling === fac.id
                                                    ? "..."
                                                    : fac.isActive
                                                      ? "Deactivate"
                                                      : "Activate"}
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setDeletingFacility(fac)}
                                                className="px-2.5 font-semibold text-xs border-destructive/30 text-destructive hover:bg-destructive/10"
                                                title="Delete Facility"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                            </Button>
                                        </div>
                                    </CardContent>
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
                                placeholder="Search by reference code, venue name, date, purpose, or amount..."
                                value={reservationQuery}
                                onChange={(e) => setReservationQuery(e.target.value)}
                                className="pl-9 h-9 text-xs sm:text-sm bg-card w-full"
                            />
                        </div>
                    </div>

                    <Card className="border shadow-md">
                        <CardContent className="p-0">
                            {loading ? (
                                <div className="p-12 text-center text-muted-foreground text-sm">
                                    Loading reservations...
                                </div>
                            ) : filteredBookings.length === 0 ? (
                                <EmptyState
                                    title="No Reservations Found"
                                    description={
                                        allBookings.length === 0
                                            ? "There are no reservations for municipal facilities yet."
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
                                                <TableHead>Citizen</TableHead>
                                                <TableHead>Venue Name</TableHead>
                                                <TableHead>Reserved Date</TableHead>
                                                <TableHead>Purpose</TableHead>
                                                <TableHead>Amount Paid</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {filteredBookings.map((bkg) => (
                                                <TableRow
                                                    key={bkg.id}
                                                    className="hover:bg-muted/50"
                                                >
                                                    <TableCell className="font-mono font-bold text-xs text-primary">
                                                        {bkg.bookingReference}
                                                    </TableCell>
                                                    <TableCell className="text-sm font-semibold">
                                                        {bkg.citizenName || "—"}
                                                    </TableCell>
                                                    <TableCell className="font-bold text-sm max-w-[200px] truncate">
                                                        {bkg.facilityName}
                                                    </TableCell>
                                                    <TableCell className="font-semibold text-xs text-foreground">
                                                        {new Date(
                                                            bkg.bookedDate
                                                        ).toLocaleDateString()}
                                                    </TableCell>
                                                    <TableCell className="text-xs text-muted-foreground max-w-[180px] truncate">
                                                        {bkg.purpose}
                                                    </TableCell>
                                                    <TableCell className="font-extrabold text-sm text-primary">
                                                        ₹{bkg.amountPaid.toLocaleString("en-IN")}
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
                open={dialogOpen}
                onOpenChange={(o) => {
                    if (!o) {
                        setDialogOpen(false);
                        setEditing(null);
                        setForm(BLANK_FORM);
                    }
                }}
            >
                <DialogContent
                    onOpenAutoFocus={(e) => e.preventDefault()}
                    className="sm:max-w-lg max-h-[90vh] overflow-y-auto"
                >
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-primary">
                            {editing ? (
                                <Pencil className="w-5 h-5" />
                            ) : (
                                <Plus className="w-5 h-5" />
                            )}
                            {editing ? "Edit Municipal Facility" : "Add New Municipal Facility"}
                        </DialogTitle>
                        <DialogDescription className="text-xs">
                            {editing
                                ? "Update the details and amenities for this municipal venue."
                                : "Fill in the details to register a new civic venue in the system."}
                        </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleSave} className="space-y-4 py-2">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div className="sm:col-span-2 space-y-1">
                                <Label className="text-xs font-semibold">Facility Name *</Label>
                                <Input
                                    value={form.name}
                                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    placeholder="e.g. Gandhi Community Hall"
                                    className="text-xs"
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs font-semibold">Type *</Label>
                                <Select
                                    value={form.facilityType}
                                    onValueChange={(val) => setForm({ ...form, facilityType: val })}
                                    disabled={facilityTypes.length === 0}
                                >
                                    <SelectTrigger className="w-full h-9 text-xs">
                                        <SelectValue
                                            placeholder={
                                                facilityTypes.length === 0
                                                    ? "No facility type available"
                                                    : "Select Type"
                                            }
                                        />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {facilityTypes.map((t) => (
                                            <SelectItem key={t.id} value={t.name}>
                                                {t.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs font-semibold">Capacity *</Label>
                                <Input
                                    type="number"
                                    value={form.capacity}
                                    onChange={(e) => setForm({ ...form, capacity: e.target.value })}
                                    placeholder="e.g. 500"
                                    className="text-xs"
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs font-semibold">Price Per Day (₹) *</Label>
                                <Input
                                    type="number"
                                    value={form.pricePerDay}
                                    onChange={(e) =>
                                        setForm({ ...form, pricePerDay: e.target.value })
                                    }
                                    placeholder="e.g. 8500"
                                    className="text-xs"
                                    required
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs font-semibold">Pincode</Label>
                                <Input
                                    value={form.pincode}
                                    onChange={(e) => setForm({ ...form, pincode: e.target.value })}
                                    placeholder="e.g. 600001"
                                    className="text-xs"
                                />
                            </div>
                            <div className="sm:col-span-2 space-y-1">
                                <Label className="text-xs font-semibold">Address *</Label>
                                <Input
                                    value={form.address}
                                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                                    placeholder="Full street address..."
                                    className="text-xs"
                                    required
                                />
                            </div>
                            <div className="sm:col-span-2 space-y-1">
                                <Label className="text-xs font-semibold">Description</Label>
                                <Textarea
                                    value={form.description}
                                    onChange={(e) =>
                                        setForm({ ...form, description: e.target.value })
                                    }
                                    placeholder="Brief description of the venue and its features..."
                                    className="text-xs min-h-[60px]"
                                />
                            </div>
                            <div className="sm:col-span-2 space-y-1">
                                <Label className="text-xs font-semibold">
                                    Amenities (comma-separated)
                                </Label>
                                <Input
                                    value={form.amenities}
                                    onChange={(e) =>
                                        setForm({ ...form, amenities: e.target.value })
                                    }
                                    placeholder="e.g. Air Conditioning, Parking, Sound System"
                                    className="text-xs"
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => {
                                    setDialogOpen(false);
                                    setEditing(null);
                                    setForm(BLANK_FORM);
                                }}
                            >
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                disabled={saving}
                                className="font-bold bg-primary hover:bg-primary/90 text-primary-foreground"
                            >
                                {saving
                                    ? "Saving..."
                                    : editing
                                      ? "Update Facility"
                                      : "Create Facility"}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            <ConfirmationModal
                isOpen={!!deletingFacility}
                onClose={() => setDeletingFacility(null)}
                onConfirm={handleDeleteFacility}
                title="Delete Municipal Facility?"
                description={`Are you sure you want to permanently delete "${deletingFacility?.name}"? All related data and future reservation records for this venue will be affected.`}
                confirmText="Delete Facility"
                isLoading={isDeletingFacility}
                variant="destructive"
            />
        </div>
    );
};
