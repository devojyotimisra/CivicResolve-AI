import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Phone, Mail, Lock } from "lucide-react";
import { toast } from "sonner";

export const OfficerProfile = () => {
    const { user, updateProfile, updatePassword } = useAuth();
    const [formData, setFormData] = useState({
        phone: user?.phone || "",
    });
    const [loading, setLoading] = useState(false);
    const [passLoading, setPassLoading] = useState(false);
    const [passForm, setPassForm] = useState({ current: "", newPass: "" });

    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await updateProfile({ phone: formData.phone });
        } catch {
            // Errors handled by context toast
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordUpdate = async (e) => {
        e.preventDefault();
        if (!passForm.current || !passForm.newPass) {
            toast.error("Both fields are required.");
            return;
        }
        if (
            passForm.newPass.length < 8 ||
            !/\d/.test(passForm.newPass) ||
            !/[!@#$%^&*(),.?":{}|<>]/.test(passForm.newPass)
        ) {
            toast.error(
                "Password must be at least 8 characters long and contain a number and a special character."
            );
            return;
        }
        setPassLoading(true);
        try {
            await updatePassword(passForm.current, passForm.newPass);
            setPassForm({ current: "", newPass: "" });
        } catch {
            // Errors handled by context toast
        } finally {
            setPassLoading(false);
        }
    };

    return (
        <div className="space-y-8 pb-10 max-w-3xl mx-auto">
            <div className="border-b pb-4">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                    Field Officer Credentials
                </h1>
                <p className="text-xs sm:text-sm text-muted-foreground">
                    View your credentials and update your security password.
                </p>
            </div>

            <Card className="border shadow-xl overflow-hidden">
                <div className="bg-muted/40 p-6 border-b flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
                    <Avatar className="w-24 h-24 ring-2 ring-primary/20 shadow-md">
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
                                Badge: {user?.badgeId || ""}
                            </Badge>
                        </div>
                        <h2 className="text-2xl font-extrabold text-foreground">{user?.name}</h2>
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
                        <form onSubmit={handleProfileUpdate} className="space-y-4 w-full">
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
                                            value={formData.phone}
                                            onChange={(e) =>
                                                setFormData({ ...formData, phone: e.target.value })
                                            }
                                            required
                                            className="pl-9"
                                        />
                                    </div>
                                </div>
                            </div>
                            <Button
                                type="submit"
                                variant="outline"
                                className="w-full sm:w-auto font-semibold text-xs mt-2"
                                disabled={loading}
                            >
                                {loading ? "Updating..." : "Update Contact Details"}
                            </Button>
                        </form>
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
                                    value={passForm.current}
                                    onChange={(e) =>
                                        setPassForm({ ...passForm, current: e.target.value })
                                    }
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="new-pass" className="text-xs">
                                    New Password
                                </Label>
                                <Input
                                    id="new-pass"
                                    type="password"
                                    placeholder="••••••••"
                                    value={passForm.newPass}
                                    onChange={(e) =>
                                        setPassForm({ ...passForm, newPass: e.target.value })
                                    }
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
