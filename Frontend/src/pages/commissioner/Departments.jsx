import React, { useState, useEffect } from "react";
import { adminService } from "@/services/adminService";
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
import { Building2, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

const BLANK = { name: "" };

export const CommissionerDepartments = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(BLANK);
  const [saving, setSaving] = useState(false);
  const [deletingDept, setDeletingDept] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await adminService.getDepartments();
      setDepartments(data);
    } catch {
      toast.error("Failed to load departments");
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
  const openEdit = (dept) => {
    setEditing(dept);
    setForm({ name: dept.name });
    setDialogOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.name) {
      toast.error("Department name is required.");
      return;
    }
    setSaving(true);
    try {
      await adminService.saveDepartment(
        editing ? { ...form, id: editing.id } : form,
      );
      toast.success(
        editing
          ? `Department "${form.name}" updated!`
          : `Department "${form.name}" created!`,
      );
      setDialogOpen(false);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to save department");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingDept) return;
    setIsDeleting(true);
    try {
      await adminService.deleteDepartment(deletingDept.id);
      toast.success(`Department "${deletingDept.name}" deleted successfully!`);
      setDeletingDept(null);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to delete department");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Building2 className="w-6 h-6 text-primary" /> City Departments
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Manage the city departments responsible for resolving civic reports.
          </p>
        </div>
        <Button onClick={openNew} className="font-bold shadow-md shrink-0">
          <Plus className="w-4 h-4 mr-2" /> Add Department
        </Button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-muted-foreground text-sm">
          Loading departments...
        </div>
      ) : departments.length === 0 ? (
        <EmptyState
          title="No Departments"
          description="No departments defined yet."
          icon={Building2}
          actionLabel="Add First Department"
          onAction={openNew}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {departments.map((dept) => (
            <Card
              key={dept.id}
              className="border shadow-sm hover:shadow-md transition-all"
            >
              <CardContent className="p-5 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-sm text-foreground leading-snug">
                    {dept.name}
                  </h3>
                  <div className="flex shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-primary"
                      onClick={() => openEdit(dept)}
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-muted-foreground hover:text-destructive"
                      onClick={() => setDeletingDept(dept)}
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
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              {editing ? (
                <Pencil className="w-5 h-5" />
              ) : (
                <Plus className="w-5 h-5" />
              )}
              {editing ? "Edit Department" : "New Department"}
            </DialogTitle>
            <DialogDescription className="text-xs">
              {editing
                ? "Update this department's name."
                : "Define a new department."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSave} className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Department Name *</Label>
              <Input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Roads & Traffic"
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
                    ? "Update Department"
                    : "Create Department"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={!!deletingDept}
        onClose={() => setDeletingDept(null)}
        onConfirm={handleDelete}
        title="Delete Department?"
        description={`Are you sure you want to delete the "${deletingDept?.name}" department? This action cannot be undone.`}
        confirmText="Delete Department"
        isLoading={isDeleting}
        variant="destructive"
      />
    </div>
  );
};
