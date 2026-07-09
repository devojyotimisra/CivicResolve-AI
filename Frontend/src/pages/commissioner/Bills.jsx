import React, { useState, useEffect } from "react";
import { billService } from "@/services/billService";
import { authService } from "@/services/authService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Label } from "@/components/ui/label";
import { Receipt, Plus, Search, Send } from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

const BLANK = {
  userId: "",
  citizenName: "",
  billType: "Property Tax",
  amount: "",
  dueDate: "",
  period: "",
};

export const CommissionerBills = () => {
  const [bills, setBills] = useState([]);
  const [citizens, setCitizens] = useState([]);
  const [billTypes, setBillTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(BLANK);
  const [saving, setSaving] = useState(false);
  const [confirmGenerate, setConfirmGenerate] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [billData, users, types] = await Promise.all([
        billService.getAllBills(),
        Promise.resolve(authService.getUsers()),
        billService.getBillTypes(),
      ]);
      setBills(billData);
      setCitizens(users.filter((u) => u.role === "citizen"));
      setBillTypes(types);
    } catch {
      toast.error("Failed to load billing records");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCitizenChange = (id) => {
    const c = citizens.find((u) => u.id === id);
    setForm({ ...form, userId: id, citizenName: c?.name || "" });
  };

  const initGenerate = (e) => {
    e.preventDefault();
    if (!form.userId || !form.billType || !form.amount || !form.dueDate) {
      toast.error("Citizen, bill type, amount, and due date are required.");
      return;
    }
    setConfirmGenerate(true);
  };

  const handleGenerate = async () => {
    setSaving(true);
    try {
      await billService.generateBill(form);
      toast.success(`Bill generated for ${form.citizenName}!`);
      setDialogOpen(false);
      setConfirmGenerate(false);
      setForm(BLANK);
      load();
    } catch (err) {
      toast.error(err.message || "Failed to generate bill");
    } finally {
      setSaving(false);
    }
  };

  const filtered = bills.filter((b) => {
    const matchSearch =
      b.billNumber?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.citizenName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.billType?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchStatus = statusFilter === "all" || b.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Receipt className="w-6 h-6 text-primary" /> Generate & Manage Bills
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Issue utility and tax bills to citizens. View all billing records
            city-wide.
          </p>
        </div>
        <Button
          onClick={() => {
            setForm(BLANK);
            setDialogOpen(true);
          }}
          className="font-bold shadow-md shrink-0"
        >
          <Plus className="w-4 h-4 mr-2" /> Generate New Bill
        </Button>
      </div>

      <Card className="bg-card/80 border shadow-sm">
        <CardContent className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="relative md:col-span-2">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by bill no., citizen, or type..."
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
              <SelectItem value="Pending">Pending</SelectItem>
              <SelectItem value="Paid">Paid</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card className="border shadow-md">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 text-center text-muted-foreground text-sm">
              Loading billing records...
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              title="No Bills Found"
              description={
                bills.length === 0
                  ? "No bills have been generated yet."
                  : "No bills match your filter criteria."
              }
              icon={Receipt}
              inCard
            />
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bill Number</TableHead>
                    <TableHead>Citizen</TableHead>
                    <TableHead>Bill Type</TableHead>
                    <TableHead>Bill Note</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((b) => (
                    <TableRow key={b.id} className="hover:bg-muted/50">
                      <TableCell className="font-mono font-bold text-xs text-primary">
                        {b.billNumber}
                      </TableCell>
                      <TableCell className="text-sm font-semibold">
                        {b.citizenName || "—"}
                      </TableCell>
                      <TableCell className="font-semibold text-sm">
                        {b.billType}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {b.period}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(b.dueDate).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="font-extrabold text-sm text-foreground">
                        ₹{b.amount.toLocaleString("en-IN")}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            b.status === "Paid"
                              ? "bg-primary/10 text-primary border-primary/20 font-bold"
                              : "bg-muted/40 text-muted-foreground border font-bold"
                          }
                        >
                          {b.status === "Paid" ? "Paid" : "Pending"}
                        </Badge>
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
        open={dialogOpen}
        onOpenChange={(o) => {
          if (!o) {
            setDialogOpen(false);
            setForm(BLANK);
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-primary">
              <Receipt className="w-5 h-5" /> Generate New Bill
            </DialogTitle>
            <DialogDescription className="text-xs">
              Issue a utility or tax bill to a registered citizen.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={initGenerate} className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Select Citizen *</Label>
              <Select value={form.userId} onValueChange={handleCitizenChange}>
                <SelectTrigger className="text-xs">
                  <SelectValue placeholder="Choose registered citizen..." />
                </SelectTrigger>
                <SelectContent>
                  {citizens.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name} ({c.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Bill Type *</Label>
              <Select
                value={form.billType}
                onValueChange={(v) => setForm({ ...form, billType: v })}
              >
                <SelectTrigger className="text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {billTypes.map((t) => (
                    <SelectItem key={t.id} value={t.name}>
                      {t.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs font-semibold">Amount (₹) *</Label>
                <Input
                  type="number"
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: e.target.value })}
                  placeholder="e.g. 5000"
                  className="text-xs"
                  required
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs font-semibold">Due Date *</Label>
                <Input
                  type="date"
                  value={form.dueDate}
                  onChange={(e) =>
                    setForm({ ...form, dueDate: e.target.value })
                  }
                  className="text-xs"
                  required
                />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Billing Note</Label>
              <Input
                value={form.period}
                onChange={(e) => setForm({ ...form, period: e.target.value })}
                placeholder="e.g. Q2 2026 (July - Sept)"
                className="text-xs"
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
                {saving ? "Generating..." : "Generate Bill"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={confirmGenerate}
        onClose={() => setConfirmGenerate(false)}
        onConfirm={handleGenerate}
        title="Broadcast Bill?"
        description={`Are you sure you want to generate a ${form.billType} bill of ₹${form.amount} for ${form.citizenName}? This will instantly notify the citizen.`}
        confirmText="Generate & Broadcast"
        isLoading={saving}
        icon={Send}
      />
    </div>
  );
};
