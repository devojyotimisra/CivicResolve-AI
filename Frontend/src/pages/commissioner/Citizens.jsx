import React, { useState, useEffect } from "react";
import { adminService } from "@/services/adminService";
import { EmptyState } from "@/components/common/EmptyState";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Users, Search, Mail, Phone } from "lucide-react";
import { toast } from "sonner";

export const CommissionerCitizens = () => {
  const [citizens, setCitizens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await adminService.getCitizens();
      setCitizens(data);
    } catch (err) {
      toast.error("Failed to load citizen directory");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = citizens.filter(
    (c) =>
      c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.pincode?.includes(searchQuery) ||
      c.address?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="space-y-6 pb-10">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Users className="w-6 h-6 text-primary" /> Citizen Directory
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Full registry of enrolled citizens across all municipal zones.
          Read-only executive view.
        </p>
      </div>

      <Card className="bg-card/80 border shadow-sm">
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, email, address or pincode..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 text-xs h-9"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="border shadow-md">
        <CardContent className="p-0">
          {loading ? (
            <div className="p-12 text-center text-muted-foreground text-sm">
              Loading citizen registry...
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              title="No Citizens Found"
              description={
                citizens.length === 0
                  ? "No citizens are registered in the system."
                  : "No citizens match your search criteria."
              }
              icon={Users}
              inCard
            />
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Citizen</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Address</TableHead>
                    <TableHead>Pincode</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((c) => (
                    <TableRow key={c.id} className="hover:bg-muted/50">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={c.avatar} alt={c.name} />
                            <AvatarFallback className="text-xs bg-primary/10 text-primary font-bold">
                              {c.name?.charAt(0) || "C"}
                            </AvatarFallback>
                          </Avatar>
                          <span className="font-semibold text-sm text-foreground">
                            {c.name}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-xs space-y-0.5">
                          <div className="flex items-center gap-1 text-muted-foreground">
                            <Mail className="w-3 h-3" />
                            {c.email}
                          </div>
                          {c.phone && (
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <Phone className="w-3 h-3" />
                              {c.phone}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground max-w-[200px] truncate">
                        {c.address || "—"}
                      </TableCell>
                      <TableCell className="text-xs font-mono font-bold text-foreground">
                        {c.pincode || "—"}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            c.isActive === false
                              ? "bg-muted text-muted-foreground text-[10px]"
                              : "bg-emerald-500/10 text-emerald-600 border-emerald-500/30 text-[10px] font-bold"
                          }
                        >
                          {c.isActive === false ? "Inactive" : "Active"}
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
    </div>
  );
};
