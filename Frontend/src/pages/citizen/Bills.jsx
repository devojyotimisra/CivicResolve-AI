import { useState, useEffect } from "react";
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
import { Receipt, CreditCard, Printer, Clock, Search } from "lucide-react";
import { toast } from "sonner";

export const CitizenBills = () => {
    const { user } = useAuth();
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedBill, setSelectedBill] = useState(null);
    const [paying, setPaying] = useState(false);
    const [receiptBill, setReceiptBill] = useState(null);
    const [cardName, setCardName] = useState("");
    const [cardNumber, setCardNumber] = useState("");
    const [cardExpiry, setCardExpiry] = useState("");
    const [cardCvv, setCardCvv] = useState("");

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

    const validatePayment = () => {
        if (!cardName.trim()) {
            toast.error("Please enter the cardholder name.");
            return false;
        }
        const cleanCardNumber = cardNumber.replace(/\s+/g, "");
        if (!/^\d{16}$/.test(cleanCardNumber)) {
            toast.error("Please enter a valid 16-digit card number.");
            return false;
        }
        if (!cardExpiry) {
            toast.error("Please select an expiry date.");
            return false;
        }
        const today = new Date();
        const [expYear, expMonth] = cardExpiry.split("-").map(Number);
        if (
            expYear < today.getFullYear() ||
            (expYear === today.getFullYear() && expMonth < today.getMonth() + 1)
        ) {
            toast.error("Card expiry date cannot be in the past.");
            return false;
        }
        if (!/^\d{3,4}$/.test(cardCvv)) {
            toast.error("Please enter a valid 3 or 4 digit CVV.");
            return false;
        }
        return true;
    };

    const handlePayConfirm = async () => {
        if (!selectedBill) return;
        if (!validatePayment()) return;
        setPaying(true);
        try {
            const receipt = await billService.payBill(selectedBill.id);
            toast.success(`Payment of ₹${selectedBill.amount} successful! Receipt generated.`);
            setReceiptBill({
                ...selectedBill,
                paidAt: receipt.paidAt || new Date().toISOString(),
                paymentRef: receipt.transactionId || receipt.transaction_id,
            });
            setSelectedBill(null);
            setCardName("");
            setCardNumber("");
            setCardExpiry("");
            setCardCvv("");
            loadBills();
        } catch (err) {
            toast.error(err.message || "Payment processing failed");
        } finally {
            setPaying(false);
        }
    };

    const handleDownload = (billToDownload) => {
        const targetBill = billToDownload?.id ? billToDownload : receiptBill;
        if (!targetBill) return;
        const printWindow = window.open("", "", "height=600,width=800");
        if (!printWindow) {
            toast.error("Please allow popups to download the receipt.");
            return;
        }
        printWindow.document.write(`
      <html>
        <head>
          <title>Receipt - ${targetBill.billNumber}</title>
          <style>
            body { font-family: 'Inter', system-ui, -apple-system, sans-serif; padding: 40px; color: #111; line-height: 1.5; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #2563eb; padding-bottom: 15px; }
            h2 { color: #2563eb; margin: 0 0 5px 0; font-size: 24px; }
            .subtitle { color: #64748b; font-size: 14px; }
            .section-title { font-size: 16px; font-weight: bold; color: #334155; margin-top: 25px; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
            .field { display: flex; flex-direction: column; }
            .label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
            .val { font-size: 14px; font-weight: 600; color: #0f172a; }
            .val.mono { font-family: monospace; }
            .total-box { margin-top: 30px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; text-align: right; }
            .total-label { font-size: 14px; color: #64748b; }
            .total-val { font-size: 24px; font-weight: bold; color: #2563eb; margin-left: 15px; }
            .footer { margin-top: 40px; text-align: center; font-size: 12px; color: #94a3b8; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>Municipal Tax Receipt</h2>
            <div class="subtitle">Official Payment Acknowledgement</div>
            <div style="font-size: 12px; color: #64748b; margin-top: 8px;">123 Civic Center, Municipal Headquarters, City District - 400001</div>
          </div>
          
          <div class="section-title">Citizen Details</div>
          <div class="grid">
            <div class="field"><span class="label">Name</span><span class="val">${targetBill.citizenName || user?.name || "Citizen"}</span></div>
            <div class="field"><span class="label">Email</span><span class="val">${user?.email || "N/A"}</span></div>
            <div class="field"><span class="label">Phone</span><span class="val">${user?.phone || "N/A"}</span></div>
            <div class="field"><span class="label">Address</span><span class="val">${user?.address || "N/A"}${user?.pincode ? ", " + user.pincode : ""}</span></div>
          </div>

          <div class="section-title">Payment Details</div>
          <div class="grid">
            <div class="field"><span class="label">Transaction Ref</span><span class="val mono">${targetBill.paymentRef || "TXN-N/A"}</span></div>
            <div class="field"><span class="label">Bill Number</span><span class="val mono">${targetBill.billNumber}</span></div>
            <div class="field"><span class="label">Bill Type</span><span class="val">${targetBill.billType}</span></div>
            <div class="field"><span class="label">Bill Note / Period</span><span class="val">${targetBill.period || "-"}</span></div>
            <div class="field"><span class="label">Paid Date</span><span class="val">${new Date(targetBill.paidAt || Date.now()).toLocaleString("en-IN", { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span></div>
          </div>
          
          <div class="total-box">
            <span class="total-label">Total Amount Paid</span>
            <span class="total-val">₹${targetBill.amount?.toLocaleString("en-IN")}</span>
          </div>

          <div class="footer">
            This is a computer-generated document. No signature is required.
          </div>
          
          <script>
            window.onload = () => {
              window.print();
              setTimeout(() => window.close(), 500);
            }
          </script>
        </body>
      </html>
    `);
        printWindow.document.close();
        toast.success("Receipt generated successfully!");
        setReceiptBill(null);
    };

    const searchedBills = bills.filter((b) => {
        if (searchQuery.trim() !== "") {
            const keywords = searchQuery.toLowerCase().trim().split(/\s+/).filter(Boolean);
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
                        View and settle bills online, and download tax payment receipts.
                    </p>
                </div>
                <div className="p-3 rounded-xl bg-muted/40 border text-foreground text-xs font-semibold flex items-center gap-2">
                    <Clock className="w-4 h-4 shrink-0" />
                    <span>
                        Total Pending Dues:{" "}
                        <strong className="text-sm">₹{pendingTotal.toLocaleString("en-IN")}</strong>
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
                        Pending Dues ({searchedBills.filter((b) => b.status === "Pending").length})
                    </Button>
                    <Button
                        variant={filter === "paid" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setFilter("paid")}
                        className="text-xs font-semibold"
                    >
                        Paid Receipts ({searchedBills.filter((b) => b.status === "Paid").length})
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
                                                        onClick={() => handleDownload(bill)}
                                                        className="h-8 text-xs font-semibold text-primary border-primary/30"
                                                    >
                                                        <Printer className="w-3.5 h-3.5 mr-1" />{" "}
                                                        Print
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

            <Dialog
                open={!!selectedBill}
                onOpenChange={(open) => !open && !paying && setSelectedBill(null)}
            >
                <DialogContent
                    className="sm:max-w-md border"
                    onOpenAutoFocus={(e) => e.preventDefault()}
                >
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-xl font-bold">
                            <CreditCard className="w-5 h-5 text-primary" />
                            Secure Payment Gateway
                        </DialogTitle>
                        <DialogDescription className="text-xs">
                            Complete your payment for {selectedBill?.billType} (
                            {selectedBill?.billNumber}).
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-2">
                        <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-between">
                            <span className="text-sm font-semibold text-primary/80">
                                Total Amount Due
                            </span>
                            <span className="text-2xl font-extrabold text-primary">
                                ₹{selectedBill?.amount?.toLocaleString("en-IN")}
                            </span>
                        </div>

                        <div className="space-y-3">
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold">Cardholder Name</label>
                                <Input
                                    value={cardName}
                                    onChange={(e) => setCardName(e.target.value)}
                                    placeholder="John Doe"
                                    className="text-xs h-9"
                                />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-semibold">Card Number</label>
                                <Input
                                    value={cardNumber}
                                    onChange={(e) => setCardNumber(e.target.value)}
                                    placeholder="0000 0000 0000 0000"
                                    maxLength={16}
                                    className="text-xs h-9 font-mono"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="space-y-1.5">
                                    <label className="text-xs font-semibold">Expiry Date</label>
                                    <Input
                                        type="month"
                                        value={cardExpiry}
                                        onChange={(e) => setCardExpiry(e.target.value)}
                                        min={new Date().toISOString().slice(0, 7)}
                                        className="text-xs h-9 font-mono uppercase"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-semibold">CVV</label>
                                    <Input
                                        type="password"
                                        value={cardCvv}
                                        onChange={(e) => setCardCvv(e.target.value)}
                                        placeholder="•••"
                                        maxLength={4}
                                        className="text-xs h-9 font-mono"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <DialogFooter className="gap-2 sm:gap-0 mt-2">
                        <Button
                            variant="outline"
                            onClick={() => setSelectedBill(null)}
                            disabled={paying}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handlePayConfirm}
                            disabled={paying}
                            className="bg-primary hover:bg-primary/90 font-bold"
                        >
                            {paying
                                ? "Processing..."
                                : `Pay ₹${selectedBill?.amount?.toLocaleString("en-IN")}`}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};
