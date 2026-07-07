import React, { useState, useEffect } from "react";
import { facilityService } from "@/services/facilityService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
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
  Building2,
  Plus,
  Pencil,
  ToggleLeft,
  ToggleRight,
  Users,
  BadgeDollarSign,
  Search,
} from "lucide-react";
import { toast } from "sonner";

const BLANK_FORM = {
  name: "",
  type: "Community Hall",
  address: "",
  pincode: "",
  pricePerDay: "",
  capacity: "",
  description: "",
  amenities: "",
};

export const CommissionerFacilities = () => {
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK_FORM);
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await facilityService.getAllFacilities();
      setFacilities(data);
    } catch (err) {
      toast.error("Failed to load municipal facilities");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const facilityTypes = Array.from(
    new Set(facilities.map((f) => f.type).filter(Boolean)),
  );

  const filtered = facilities.filter((f) => {
    const matchesSearch =
      f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.type.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && f.isActive) ||
      (statusFilter === "inactive" && !f.isActive);

    const matchesType = typeFilter === "all" || f.type === typeFilter;

    return matchesSearch && matchesStatus && matchesType;
  });

  const openNew = () => {
    setEditing(null);
    setForm(BLANK_FORM);
    setDialogOpen(true);
  };

  const openEdit = (fac) => {
    setEditing(fac);
    setForm({
      name: fac.name || "",
      type: fac.type || "Community Hall",
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
      await facilityService.toggleFacilityStatus(fac.id);
      toast.success(
        `"${fac.name}" is now ${fac.isActive ? "Inactive" : "Active"}.`,
      );
      load();
    } catch (err) {
      toast.error("Failed to update facility status");
    } finally {
      setToggling(null);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name || !form.address || !form.pricePerDay || !form.capacity) {
      toast.error("Please fill in all required fields.");
      return;
    }
    setSaving(true);
    try {
      const payload = {
        ...form,
        amenities: form.amenities
          ? form.amenities
              .split(",")
              .map((a) => a.trim())
              .filter(Boolean)
          : [],
      };
      if (editing) {
        payload.id = editing.id;
      }
      await facilityService.saveFacility(payload);
      toast.success(
        editing
          ? `Facility "${form.name}" updated successfully!`
          : `Facility "${form.name}" created successfully!`,
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

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Building2 className="w-6 h-6 text-primary" /> Manage Municipal
            Facilities
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Control all civic venues — toggle availability and add new municipal
            locations.
          </p>
        </div>
        <Button onClick={openNew} className="font-bold shadow-md shrink-0">
          <Plus className="w-4 h-4 mr-2" /> Add New Facility
        </Button>
      </div>

      <Card className="bg-card/80 border shadow-sm">
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
                <SelectItem key={t} value={t}>
                  {t}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

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
              className="border shadow-md hover:shadow-xl transition-all overflow-hidden flex flex-col justify-between bg-card"
            >
              <div>
                <CardHeader className="pb-3 border-b bg-muted/20">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <Badge
                        variant="outline"
                        className="mb-1.5 text-[10px] font-semibold text-primary border-primary/30 bg-primary/5"
                      >
                        {fac.type}
                      </Badge>
                      <CardTitle className="text-base font-bold leading-tight text-foreground">
                        {fac.name}
                      </CardTitle>
                    </div>
                    <Badge
                      className={
                        fac.isActive
                          ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 font-bold text-[10px] shrink-0"
                          : "bg-muted text-muted-foreground font-bold text-[10px] shrink-0"
                      }
                    >
                      {fac.isActive ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs text-muted-foreground pt-1 truncate">
                    {fac.address}
                  </CardDescription>
                </CardHeader>

                <CardContent className="p-4 space-y-4">
                  {fac.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                      {fac.description}
                    </p>
                  )}

                  <div className="grid grid-cols-2 gap-2 p-2.5 rounded-xl bg-muted/40 border text-xs">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <Users className="w-3.5 h-3.5 text-primary" />
                      <span className="font-semibold text-foreground">
                        {fac.capacity}
                      </span>{" "}
                      capacity
                    </div>
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <BadgeDollarSign className="w-3.5 h-3.5 text-primary" />
                      <span className="font-semibold text-foreground">
                        ₹{fac.pricePerDay?.toLocaleString()}
                      </span>
                      /day
                    </div>
                  </div>

                  {fac.amenities && fac.amenities.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-0.5">
                      {fac.amenities.slice(0, 4).map((am, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-primary/10 text-primary border border-primary/20"
                        >
                          {am}
                        </span>
                      ))}
                      {fac.amenities.length > 4 && (
                        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-primary/10 text-primary border border-primary/20">
                          +{fac.amenities.length - 4} more
                        </span>
                      )}
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
                </div>
              </CardContent>
            </Card>
          ))}
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
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              {editing ? (
                <Pencil className="w-5 h-5" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              {editing
                ? "Edit Municipal Facility"
                : "Add New Municipal Facility"}
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
                <select
                  value={form.type}
                  onChange={(e) => setForm({ ...form, type: e.target.value })}
                  className="w-full h-9 text-xs rounded-md border border-input bg-background px-3 py-1"
                >
                  <option>Community Hall</option>
                  <option>Park</option>
                  <option>Sports Arena</option>
                  <option>Library</option>
                </select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs font-semibold">Capacity *</Label>
                <Input
                  type="number"
                  value={form.capacity}
                  onChange={(e) =>
                    setForm({ ...form, capacity: e.target.value })
                  }
                  placeholder="e.g. 500"
                  className="text-xs"
                  required
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs font-semibold">
                  Price Per Day (₹) *
                </Label>
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
                  onChange={(e) =>
                    setForm({ ...form, pincode: e.target.value })
                  }
                  placeholder="e.g. 600001"
                  className="text-xs"
                />
              </div>
              <div className="sm:col-span-2 space-y-1">
                <Label className="text-xs font-semibold">Address *</Label>
                <Input
                  value={form.address}
                  onChange={(e) =>
                    setForm({ ...form, address: e.target.value })
                  }
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
    </div>
  );
};
