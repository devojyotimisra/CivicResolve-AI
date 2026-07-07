import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Phone, Mail, Lock } from "lucide-react";
import { toast } from "sonner";

export const OfficerProfile = () => {
  const { user } = useAuth();
  const [passLoading, setPassLoading] = useState(false);

  const handlePasswordUpdate = (e) => {
    e.preventDefault();
    setPassLoading(true);
    setTimeout(() => {
      setPassLoading(false);
      toast.success("Security password updated successfully!");
    }, 600);
  };

  return (
    <div className="space-y-8 pb-10 max-w-3xl mx-auto">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Field Officer Credentials
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Field Officer profile.
        </p>
      </div>

      <Card className="border shadow-xl overflow-hidden">
        <div className="bg-muted/40 p-6 border-b flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
          <Avatar className="w-24 h-24 ring-2 ring-primary/20 shadow-md">
            <AvatarImage src={user?.avatar} alt={user?.name} />
            <AvatarFallback className="bg-primary/20 text-primary text-2xl font-bold">
              {user?.name?.charAt(0) || "O"}
            </AvatarFallback>
          </Avatar>

          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
              <Badge
                variant="default"
                className="bg-primary/15 text-primary border border-primary/30 font-bold text-xs px-2.5 py-0.5 rounded-md shadow-sm"
              >
                Badge: {user?.badgeId || "OFF-104"}
              </Badge>
            </div>
            <h2 className="text-2xl font-extrabold text-foreground">
              {user?.name}
            </h2>
            <p className="text-xs text-muted-foreground font-medium">
              Department:{" "}
              <strong className="text-foreground">{user?.department}</strong>
            </p>
          </div>
        </div>

        <CardContent className="p-6 space-y-8">
          <div className="space-y-3 text-xs">
            <h4 className="font-bold text-foreground uppercase tracking-wider">
              Contact Details
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground/50" />
                  <Input
                    value={user?.email || ""}
                    disabled
                    className="pl-9 bg-muted/50 text-muted-foreground cursor-not-allowed border-dashed"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Phone Number
                </Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground/50" />
                  <Input
                    value={user?.phone || "+91 98410 11223"}
                    disabled
                    className="pl-9 bg-muted/50 text-muted-foreground cursor-not-allowed border-dashed"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t space-y-4">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary" />
              <h4 className="font-bold text-foreground uppercase tracking-wider text-xs">
                Password
              </h4>
            </div>
            <form onSubmit={handlePasswordUpdate} className="space-y-4 w-full">
              <div className="space-y-2">
                <Label htmlFor="curr-pass" className="text-xs">
                  Current Password
                </Label>
                <Input
                  id="curr-pass"
                  type="password"
                  placeholder="••••••••"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new-pass" className="text-xs">
                  New Security Password
                </Label>
                <Input
                  id="new-pass"
                  type="password"
                  placeholder="••••••••"
                  required
                />
              </div>
              <Button
                type="submit"
                variant="outline"
                className="w-full sm:w-auto font-semibold text-xs mt-2"
                disabled={passLoading}
              >
                {passLoading ? "Updating..." : "Update Password"}
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
