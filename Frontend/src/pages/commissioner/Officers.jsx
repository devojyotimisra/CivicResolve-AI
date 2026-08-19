import React, { useState, useEffect } from "react";
import { adminService } from "@/services/adminService";
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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Users,
  Search,
  CheckCircle2,
  Plus,
  Pencil,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

const BLANK_OFFICER = { name: "", email: "", badgeId: "", department: "" };

export const CommissionerOfficers = () => {
  const [officers, setOfficers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [deptFilter, setDeptFilter] = useState("all");

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK_OFFICER);
  const [saving, setSaving] = useState(false);
  const [confirmSave, setConfirmSave] = useState(false);
  const [deletingOfficer, setDeletingOfficer] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [offData, deptData] = await Promise.all([
        adminService.getOfficers(),
        adminService.getDepartments(),
      ]);
      setOfficers(offData);
      setDepartments(deptData);
    } catch {
      toast.error("Failed to load field crew directory");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openNew = () => {
    setEditing(null);
    setForm(BLANK_OFFICER);
    setDialogOpen(true);
  };
  const openEdit = (off) => {
    setEditing(off);
    setForm({
      name: off.name,
      email: off.email,
      badgeId: off.badgeId,
      department: off.department,
    });
    setDialogOpen(true);
  };

  const initSave = (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.badgeId || !form.department) {
      toast.error("All fields are required.");
      return;
    }
    const badgeRegex = /^OFF-\d{3}$/;
    if (!badgeRegex.test(form.badgeId.trim().toUpperCase())) {
      toast.error(
        "Badge ID must be in the exact format OFF-*** (OFF followed by 3 digits, e.g., OFF-101).",
      );
      return;
    }
    setForm((prev) => ({
      ...prev,
      badgeId: prev.badgeId.trim().toUpperCase(),
    }));
    setConfirmSave(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing) {
        await adminService.updateOfficer(editing.id, form);
        toast.success(`Officer "${form.name}" updated!`);
      } else {
        await adminService.provisionOfficer(form);
        toast.success(`Officer "${form.name}" added!`);
      }
      setDialogOpen(false);
      setConfirmSave(false);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to save officer");
      setConfirmSave(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingOfficer) return;
    setIsDeleting(true);
    try {
      await adminService.deleteOfficer(deletingOfficer.id);
      toast.success(`Officer "${deletingOfficer.name}" deleted!`);
      setDeletingOfficer(null);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to delete officer");
    } finally {
      setIsDeleting(false);
    }
  };

  const filtered = officers.filter((off) => {
    const matchesSearch =
      off.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      off.badgeId.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = deptFilter === "all" || off.department === deptFilter;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Users className="w-6 h-6 text-primary" />
            <span>Field Officers</span>
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Executive oversight of all active engineering crews, badge IDs, and
            caseloads.
          </p>
        </div>
        <Button onClick={openNew} className="font-bold shadow-md shrink-0">
          <Plus className="w-4 h-4 mr-2" /> Add Field Officer
        </Button>
      </div>

      <Card className="bg-card/80 border shadow-sm">
        <CardContent className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="relative md:col-span-2">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by officer name or badge ID..."
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
        </CardContent>
      </Card>

      {loading ? (
        <div className="p-12 text-center text-muted-foreground text-sm">
          Loading field crew directory...
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No Field Officers Found"
          description={
            officers.length === 0
              ? "No municipal field engineering officers found in the directory."
              : "No field officers match your selected search or department criteria."
          }
          icon={Users}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((off) => (
            <Card
              key={off.id}
              className="border shadow-md hover:shadow-xl transition-all overflow-hidden flex flex-col justify-between group"
            >
              <div className="p-6 space-y-4 relative">
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-primary"
                    onClick={() => openEdit(off)}
                  >
                    <Pencil className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    onClick={() => setDeletingOfficer(off)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex items-center gap-4">
                  <Avatar className="w-16 h-16 ring-2 ring-primary/20">
                    <AvatarFallback className="bg-primary/10 text-primary font-bold text-lg">
                      {off.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="space-y-1">
                    <Badge className="bg-primary/10 text-primary border-primary/20 text-[10px] font-bold">
                      Badge: {off.badgeId}
                    </Badge>
                    <h3 className="text-base font-bold text-foreground leading-tight pr-6">
                      {off.name}
                    </h3>
                    <p className="text-xs text-muted-foreground truncate">
                      {off.email}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-2 p-3 rounded-lg bg-muted/40 border text-xs">
                  <div>
                    <span className="text-[10px] text-muted-foreground block">
                      Department
                    </span>
                    <span className="font-bold text-foreground">
                      {off.department}
                    </span>
                  </div>
                </div>
              </div>
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
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              {editing ? (
                <Pencil className="w-5 h-5" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              {editing ? "Edit Field Officer" : "Add New Field Officer"}
            </DialogTitle>
            <DialogDescription className="text-xs">
              {editing
                ? "Update details for this field officer."
                : "Register a new field officer to the municipal crew."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={initSave} className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Full Name *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. John Doe"
                className="text-xs"
                required
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Email Address *</Label>
              <Input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="john@example.com"
                className="text-xs"
                required
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Badge ID *</Label>
              <Input
                value={form.badgeId}
                onChange={(e) => setForm({ ...form, badgeId: e.target.value })}
                placeholder="e.g. OFF-101"
                className="text-xs font-mono"
                required
                disabled={!!editing}
              />
              {editing && (
                <p className="text-[10px] text-muted-foreground">
                  Badge ID cannot be changed once assigned.
                </p>
              )}
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Department *</Label>
              <Select
                value={form.department}
                onValueChange={(val) => setForm({ ...form, department: val })}
                required
                disabled={!departments || departments.length === 0}
              >
                <SelectTrigger className="text-xs">
                  <SelectValue 
                    placeholder={
                      !departments || departments.length === 0 
                        ? "No departments available" 
                        : "Select Department"
                    } 
                  />
                </SelectTrigger>
                <SelectContent>
                  {!departments || departments.length === 0 ? (
                    <SelectItem value="no-dept" disabled>
                      No departments available
                    </SelectItem>
                  ) : (
                    departments.map((d) => (
                      <SelectItem key={d.id} value={d.name}>
                        {d.name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogOpen(false)}
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
                    ? "Update Field Officer"
                    : "Add Field Officer"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={confirmSave}
        onClose={() => setConfirmSave(false)}
        onConfirm={handleSave}
        title={editing ? "Update Field Officer?" : "Add Field Officer?"}
        description={
          editing
            ? `Are you sure you want to save changes for ${form.name}?`
            : `Are you sure you want to provision ${form.name} as a new field officer in the ${form.department} department?`
        }
        confirmText={editing ? "Save Changes" : "Add Field Officer"}
        isLoading={saving}
        icon={editing ? Pencil : Plus}
      />

      <ConfirmationModal
        isOpen={!!deletingOfficer}
        onClose={() => setDeletingOfficer(null)}
        onConfirm={handleDelete}
        title="Delete Field Officer?"
        description={`Are you sure you want to permanently delete the field officer "${deletingOfficer?.name}"? This action cannot be undone and will revoke their access.`}
        confirmText="Delete Field Officer"
        isLoading={isDeleting}
        variant="destructive"
        icon={Trash2}
      />
    </div>
  );
};
