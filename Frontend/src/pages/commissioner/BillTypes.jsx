import { useState, useEffect } from "react";
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
import { Tags, Plus, Pencil, Trash2, Search } from "lucide-react";
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
    const [searchQuery, setSearchQuery] = useState("");

    const filtered = billTypes.filter((type) => {
        const query = searchQuery.toLowerCase();
        return Object.values(type).some(
            (val) =>
                val !== null && val !== undefined && val.toString().toLowerCase().includes(query)
        );
    });

    const load = async () => {
        setLoading(true);
        try {
            const data = await billService.getBillTypes();
            setBillTypes(data);
        } catch (error) {
            console.error(error);
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
            await billService.saveBillType(editing ? { ...form, id: editing.id } : form);
            toast.success(
                editing ? `Bill Type "${form.name}" updated!` : `Bill Type "${form.name}" created!`
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
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <Tags className="w-6 h-6 text-primary" /> Bill Types
                    </h1>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                        Manage the categories of bills that can be generated for citizens.
                    </p>
                </div>
                <Button onClick={openNew} className="font-bold shadow-md shrink-0">
                    <Plus className="w-4 h-4 mr-2" /> Add Bill Type
                </Button>
            </div>

            <div className="relative w-full">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search bill types..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 w-full text-xs h-9 sm:placeholder:text-sm placeholder:text-xs"
                />
            </div>

            {loading ? (
                <div className="p-12 text-center text-muted-foreground text-sm">
                    Loading bill types...
                </div>
            ) : filtered.length === 0 ? (
                <EmptyState
                    title="No Bill Types"
                    description={
                        billTypes.length === 0
                            ? "No bill types defined yet."
                            : "No bill types match your search."
                    }
                    icon={Tags}
                />
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filtered.map((type) => (
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
                            {editing ? "Edit Bill Type" : "New Bill Type"}
                        </DialogTitle>
                        <DialogDescription className="text-xs">
                            {editing ? "Update this bill type's name." : "Define a new bill type."}
                        </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleSave} className="space-y-4 py-2">
                        <div className="space-y-1">
                            <Label className="text-xs font-semibold">Bill Type Name *</Label>
                            <Input
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                                placeholder="e.g. Property Tax"
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
