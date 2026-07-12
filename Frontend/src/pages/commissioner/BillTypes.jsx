import React, { useState, useEffect } from "react";
import { billService } from "@/services/billService";
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

export const CommissionerBillTypes = () => {
  const [billTypes, setBillTypes] = useState([]);
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
      const data = await billService.getBillTypes();
      setBillTypes(data);
    } catch {
      toast.error("Failed to load bill types");
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
      toast.error("Bill type name is required.");
      return;
    }
    setSaving(true);
    try {
      await billService.saveBillType(
        editing ? { ...form, id: editing.id } : form,
      );
      toast.success(
        editing
          ? `Bill Type "${form.name}" updated!`
          : `Bill Type "${form.name}" created!`,
      );
      setDialogOpen(false);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to save bill type");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingType) return;
    setIsDeleting(true);
    try {
      await billService.deleteBillType(deletingType.id);
      toast.success(`Bill Type "${deletingType.name}" deleted successfully!`);
      setDeletingType(null);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to delete bill type");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Tags className="w-6 h-6 text-primary" /> Bill Types
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage the categories of bills that can be generated for citizens.
          </p>
        </div>
        <Button onClick={openNew} className="shrink-0 rounded-lg px-4 shadow-sm hover:shadow-md transition-all">
          <Plus className="w-4 h-4 mr-2" /> Add Bill Type
        </Button>
      </div>

      {loading ? (
        <div className="rounded-lg border bg-muted/20 p-12 text-center text-sm text-muted-foreground">
          Loading bill types...
        </div>
      ) : billTypes.length === 0 ? (
        <EmptyState
          title="No Bill Types"
          description="No bill types defined yet."
          icon={Tags}
          actionLabel="Add First Bill Type"
          onAction={openNew}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {billTypes.map((type) => (
            <Card
              key={type.id}
              className="rounded-xl border border-border bg-card shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
              <CardContent className="space-y-4 p-5">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-base font-semibold text-foreground leading-tight">
                    {type.name}
                  </h3>
                  <div className="flex shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-md text-muted-foreground hover:bg-primary/10 hover:text-primary transition-colors"
                      onClick={() => openEdit(type)}
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
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
        <DialogContent className="sm:max-w-md rounded-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-lg font-semibold text-primary">
              {editing ? (
                <Pencil className="w-5 h-5" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              {editing ? "Edit Bill Type" : "New Bill Type"}
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground">
              {editing
                ? "Update this bill type's name."
                : "Define a new bill type."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSave} className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-sm font-medium">Bill Type Name *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Property Tax"
                className="rounded-lg text-sm"
                required
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                className="rounded-lg"
                onClick={() => setDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving}
                className="rounded-lg font-semibold bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {saving
                  ? "Saving..."
                  : editing
                    ? "Update Bill Type"
                    : "Create Bill Type"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={!!deletingType}
        onClose={() => setDeletingType(null)}
        onConfirm={handleDelete}
        title="Delete Bill Type?"
        description={`Are you sure you want to delete the "${deletingType?.name}" bill type? This action cannot be undone.`}
        confirmText="Delete Bill Type"
        isLoading={isDeleting}
        variant="destructive"
      />
    </div>
  );
};
