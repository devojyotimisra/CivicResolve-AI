import React, { useState, useEffect } from "react";
import { facilityService } from "@/services/facilityService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tags, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

const BLANK = { name: "" };

export const CommissionerFacilityTypes = () => {
  const [facilityTypes, setFacilityTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK);
  const [saving, setSaving] = useState(false);
  const [deletingType, setDeletingType] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await facilityService.getFacilityTypes();
      setFacilityTypes(data);
    } catch {
      toast.error("Failed to load facility types");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openNew = () => {
    setEditing(null);
    setForm(BLANK);
    setDialogOpen(true);
  };
  const openEdit = (type) => {
    setEditing(type);
    setForm({ name: type.name });
    setDialogOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name) {
      toast.error("Facility type name is required.");
      return;
    }
    setSaving(true);
    try {
      await facilityService.saveFacilityType(
        editing ? { ...form, id: editing.id } : form,
      );
      toast.success(
        editing
          ? `Facility Type "${form.name}" updated!`
          : `Facility Type "${form.name}" created!`,
      );
      setDialogOpen(false);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to save facility type");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingType) return;
    setIsDeleting(true);
    try {
      await facilityService.deleteFacilityType(deletingType.id);
      toast.error(`Facility Type "${deletingType.name}" deleted successfully!`);
      setDeletingType(null);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to delete facility type");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Tags className="w-6 h-6 text-primary" /> Facility Types
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Manage the categories of facilities that can be created.
          </p>
        </div>
        <Button onClick={openNew} className="font-bold shadow-md shrink-0">
          <Plus className="w-4 h-4 mr-2" /> Add Facility Type
        </Button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-muted-foreground text-sm">
          Loading facility types...
        </div>
      ) : facilityTypes.length === 0 ? (
        <EmptyState
          title="No Facility Types"
          description="No facility types defined yet."
          icon={Tags}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {facilityTypes.map((type) => (
            <Card
              key={type.id}
              className="border shadow-sm hover:shadow-md transition-all"
            >
              <CardContent className="p-5 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-sm text-foreground leading-snug">
                    {type.name}
                  </h3>
                  <div className="flex shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-primary"
                      onClick={() => openEdit(type)}
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-destructive"
                      onClick={() => setDeletingType(type)}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
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
          }
        }}
      >
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              {editing ? (
                <Pencil className="w-5 h-5" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              {editing ? "Edit Facility Type" : "New Facility Type"}
            </DialogTitle>
            <DialogDescription className="text-xs">
              {editing
                ? "Update this facility type's name."
                : "Define a new facility type."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSave} className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Facility Type Name *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Community Hall"
                className="text-xs"
                required
              />
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
                    ? "Update Facility Type"
                    : "Create Facility Type"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={!!deletingType}
        onClose={() => setDeletingType(null)}
        onConfirm={handleDelete}
        title="Delete Facility Type?"
        description={`Are you sure you want to delete the "${deletingType?.name}" facility type? This action cannot be undone.`}
        confirmText="Delete Facility Type"
        isLoading={isDeleting}
        variant="destructive"
      />
    </div>
  );
};
