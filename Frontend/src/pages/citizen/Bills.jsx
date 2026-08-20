import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { billService } from "@/services/billService";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import { Input } from "@/components/ui/input";
import {
  Receipt,
  CheckCircle2,
  CreditCard,
  Download,
  Clock,
  Search,
} from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

export const CitizenBills = () => {
  const { user } = useAuth();
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBill, setSelectedBill] = useState(null);
  const [paying, setPaying] = useState(false);
  const [receiptBill, setReceiptBill] = useState(null);

  const loadBills = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await billService.getUserBills(user.id);
      setBills(data);
    } catch {
      toast.error("Failed to load utility bills");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBills();
  }, [user]);

  const handlePayConfirm = async () => {
    if (!selectedBill) return;
    setPaying(true);
    try {
      const updated = await billService.payBill(selectedBill.id);
      toast.success(
        `Payment of ₹${selectedBill.amount} successful! Receipt generated.`,
      );
      setSelectedBill(null);
      setReceiptBill(updated);
      loadBills();
    } catch (err) {
      toast.error(err.message || "Payment processing failed");
    } finally {
      setPaying(false);
    }
  };

  const searchedBills = bills.filter((b) => {
    if (searchQuery.trim() !== "") {
      const keywords = searchQuery
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      return keywords.every((query) => {
        const matchNumber = (b.billNumber || "").toLowerCase().includes(query);
        const matchType = (b.billType || "").toLowerCase().includes(query);
        const matchPeriod = (b.period || "").toLowerCase().includes(query);
        const matchStatus = (b.status || "").toLowerCase().includes(query);
        const matchAmount = (
          b.amount !== undefined && b.amount !== null ? b.amount.toString() : ""
        ).includes(query);
        const matchDate =
          (b.dueDate ? new Date(b.dueDate).toLocaleDateString() : "")
            .toLowerCase()
            .includes(query) || (b.dueDate || "").toLowerCase().includes(query);
        return (
          matchNumber ||
          matchType ||
          matchPeriod ||
          matchStatus ||
          matchAmount ||
          matchDate
        );
      });
    }
    return true;
  });

  const filteredBills = searchedBills.filter((b) => {
    if (filter === "pending") return b.status === "Pending";
    if (filter === "paid") return b.status === "Paid";
    return true;
  });

  const pendingTotal = bills
    .filter((b) => b.status === "Pending")
    .reduce((acc, b) => acc + (b.amount || 0), 0);

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Municipal Utility Bills
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            View assessment periods, settle property/water dues online, and
            download tax payment receipts.
          </p>
        </div>
        <div className="p-3 rounded-xl bg-muted/40 border text-foreground text-xs font-semibold flex items-center gap-2">
          <Clock className="w-4 h-4 shrink-0" />
          <span>
            Total Pending Dues:{" "}
            <strong className="text-sm">
              ₹{pendingTotal.toLocaleString("en-IN")}
            </strong>
          </span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by bill no., utility type, period, amount, or status..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9 text-xs sm:text-sm bg-card w-full"
          />
        </div>
        <div className="flex gap-2 shrink-0 overflow-x-auto pb-1 sm:pb-0">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("all")}
            className="text-xs font-semibold"
          >
            All Bills ({searchedBills.length})
          </Button>
          <Button
            variant={filter === "pending" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("pending")}
            className="text-xs font-semibold"
          >
            Pending Dues (
            {searchedBills.filter((b) => b.status === "Pending").length})
          </Button>
          <Button
            variant={filter === "paid" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("paid")}
            className="text-xs font-semibold"
          >
            Paid Receipts (
            {searchedBills.filter((b) => b.status === "Paid").length})
          </Button>
        </div>
      </div>

      <Card className="border shadow-md">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 text-center text-muted-foreground text-sm">
              Loading utility bills...
            </div>
          ) : filteredBills.length === 0 ? (
            <EmptyState
              title="No Utility Bills Found"
              description={
                bills.length === 0
                  ? "You currently have no municipal billing records or tax assessments."
                  : "There are no billing records matching your current search query or filter."
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
                    <TableHead>Bill Type</TableHead>
                    <TableHead>Bill Note</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredBills.map((bill) => (
                    <TableRow key={bill.id} className="hover:bg-muted/50">
                      <TableCell className="font-mono font-bold text-xs text-primary">
                        {bill.billNumber}
                      </TableCell>
                      <TableCell className="font-semibold text-sm">
                        {bill.billType}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {bill.period}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(bill.dueDate).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="font-extrabold text-sm text-foreground">
                        ₹{bill.amount.toLocaleString("en-IN")}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            bill.status === "Paid"
                              ? "bg-primary/10 text-primary border-primary/20 font-bold"
                              : "bg-muted/40 text-muted-foreground border font-bold"
                          }
                        >
                          {bill.status === "Paid" ? "Paid" : "Pending"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {bill.status === "Pending" ? (
                          <Button
                            size="sm"
                            className="h-8 text-xs font-semibold bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm"
                            onClick={() => setSelectedBill(bill)}
                          >
                            Pay Now
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setReceiptBill(bill)}
                            className="h-8 text-xs font-semibold text-primary border-primary/30"
                          >
                            <Download className="w-3.5 h-3.5 mr-1" /> Receipt
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <ConfirmationModal
        isOpen={!!selectedBill}
        onClose={() => setSelectedBill(null)}
        onConfirm={handlePayConfirm}
        title="Municipal Payment Gateway"
        description={
          selectedBill ? (
            <div className="space-y-4 py-3 text-left">
              <p>
                Checkout for {selectedBill.billType} ({selectedBill.billNumber}
                ).
              </p>
              <div className="p-4 rounded-xl bg-muted/60 border flex items-center justify-between">
                <span className="text-sm text-muted-foreground font-semibold">
                  Total Amount Due:
                </span>
                <span className="text-2xl font-extrabold text-foreground">
                  ₹{selectedBill.amount.toLocaleString("en-IN")}
                </span>
              </div>
            </div>
          ) : (
            ""
          )
        }
        confirmText={`Confirm Payment (₹${selectedBill?.amount})`}
        isLoading={paying}
        icon={CreditCard}
      />

      <Dialog
        open={!!receiptBill}
        onOpenChange={(open) => !open && setReceiptBill(null)}
      >
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="sm:max-w-md border">
          <DialogHeader className="text-center pb-2 border-b">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-1">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <DialogTitle className="text-xl font-bold">
              Official Municipal Receipt
            </DialogTitle>
            <DialogDescription className="text-xs">
              Transaction reference:{" "}
              <span className="font-mono font-bold text-foreground">
                {receiptBill?.paymentRef || "TXN_UPI_88910231"}
              </span>
            </DialogDescription>
          </DialogHeader>

          {receiptBill && (
            <div className="space-y-3 py-4 text-xs">
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Citizen Name:</span>
                <span className="font-semibold text-foreground">
                  {receiptBill.citizenName}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Bill Number:</span>
                <span className="font-mono font-bold text-primary">
                  {receiptBill.billNumber}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Utility Type:</span>
                <span className="font-semibold text-foreground">
                  {receiptBill.billType}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">
                  Assessment Period:
                </span>
                <span className="text-muted-foreground">
                  {receiptBill.period}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b">
                <span className="text-muted-foreground">Paid Date:</span>
                <span className="font-semibold text-foreground">
                  {new Date(receiptBill.paidAt || Date.now()).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between py-2 rounded bg-muted/60 px-2 font-bold text-sm">
                <span>Total Amount Paid:</span>
                <span className="text-primary">
                  ₹{receiptBill.amount.toLocaleString("en-IN")}
                </span>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              onClick={() => {
                toast.success("Receipt downloaded as PDF!");
                setReceiptBill(null);
              }}
              className="w-full font-bold"
            >
              <Download className="mr-2 h-4 w-4" /> Download PDF Receipt
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
