import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User, Lock, Save, SaveAll, KeyRound } from "lucide-react";
import { toast } from "sonner";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";

export const CitizenProfile = () => {
    const { user, updateProfile, updatePassword } = useAuth();
    const [formData, setFormData] = useState({
        name: user?.name || "",
        phone: user?.phone || "",
        address: user?.address || "",
        pincode: user?.pincode || "",
    });
    const [loading, setLoading] = useState(false);
    const [passLoading, setPassLoading] = useState(false);
    const [confirmUpdate, setConfirmUpdate] = useState(false);
    const [confirmPass, setConfirmPass] = useState(false);
    const [passForm, setPassForm] = useState({ current: "", newPass: "" });

    const handleSaveProfile = async () => {
        setLoading(true);
        try {
            await updateProfile(formData);
            setConfirmUpdate(false);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordUpdate = async () => {
        if (!passForm.current || !passForm.newPass) {
            toast.error("Both fields are required.");
            setConfirmPass(false);
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
            setConfirmPass(false);
            return;
        }
        setPassLoading(true);
        try {
            await updatePassword(passForm.current, passForm.newPass);
            setConfirmPass(false);
            setPassForm({ current: "", newPass: "" });
        } catch (error) {
            console.error(error);
            setConfirmPass(false);
        } finally {
            setPassLoading(false);
        }
    };

    const submitProfileForm = (e) => {
        e.preventDefault();
        setConfirmUpdate(true);
    };

    const submitPassForm = (e) => {
        e.preventDefault();
        setConfirmPass(true);
    };

    return (
        <div className="space-y-8 pb-10 max-w-4xl mx-auto">
            <div className="border-b pb-4">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                    My Citizen Profile & Security
                </h1>
                <p className="text-xs sm:text-sm text-muted-foreground">
                    Manage your contact credentials, residential address, and linked tracking
                    tokens.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-1 space-y-6 flex flex-col h-full">
                    <Card
                        className={`border shadow-md ${user?.isPasswordEmpty ? "flex-1 flex flex-col justify-center" : ""}`}
                    >
                        <CardContent
                            className={`pt-6 text-center space-y-4 ${user?.isPasswordEmpty ? "flex-1 flex flex-col justify-center" : ""}`}
                        >
                            <Avatar className="w-24 h-24 mx-auto ring-4 ring-primary/20">
                                <AvatarFallback className="bg-primary/20 text-primary text-2xl font-bold">
                                    {user?.name?.charAt(0) || "C"}
                                </AvatarFallback>
                            </Avatar>
                            <div>
                                <h3 className="text-lg font-bold text-foreground">{user?.name}</h3>
                                <p className="text-xs text-muted-foreground">{user?.email}</p>
                            </div>
                        </CardContent>
                    </Card>

                    {!user?.isPasswordEmpty && (
                        <Card className="border shadow-md">
                            <CardHeader className="pb-4 border-b">
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <Lock className="w-4 h-4 text-primary" />
                                    <span>Security</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-6">
                                <form onSubmit={submitPassForm} className="space-y-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="curr-pass">Current Password</Label>
                                        <Input
                                            id="curr-pass"
                                            type="password"
                                            placeholder="••••••••"
                                            value={passForm.current}
                                            onChange={(e) =>
                                                setPassForm({
                                                    ...passForm,
                                                    current: e.target.value,
                                                })
                                            }
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="new-pass">New Password</Label>
                                        <Input
                                            id="new-pass"
                                            type="password"
                                            placeholder="••••••••"
                                            value={passForm.newPass}
                                            onChange={(e) =>
                                                setPassForm({
                                                    ...passForm,
                                                    newPass: e.target.value,
                                                })
                                            }
                                            required
                                        />
                                    </div>
                                    <Button
                                        type="submit"
                                        variant="outline"
                                        className="w-full font-semibold text-xs mt-2"
                                        disabled={passLoading}
                                    >
                                        {passLoading ? "Updating..." : "Update Password"}
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    )}
                </div>

                <div className="md:col-span-2">
                    <Card className="border shadow-md h-full flex flex-col justify-between">
                        <CardHeader className="pb-4 border-b">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <User className="w-4 h-4 text-primary" />
                                <span>Personal Contact Details</span>
                            </CardTitle>
                            <CardDescription className="text-xs">
                                These details appear on your utility tax receipts and booking entry
                                permits.
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="pt-6 pb-6 flex-1 flex flex-col">
                            <form
                                id="profile-form"
                                onSubmit={submitProfileForm}
                                className="flex-1 flex flex-col justify-between space-y-4"
                            >
                                <div className="space-y-2">
                                    <Label htmlFor="name">Full Name</Label>
                                    <Input
                                        id="name"
                                        value={formData.name}
                                        onChange={(e) =>
                                            setFormData({ ...formData, name: e.target.value })
                                        }
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="email">Email Address</Label>
                                        <Input
                                            id="email"
                                            value={user?.email}
                                            disabled
                                            className="bg-muted text-muted-foreground font-mono text-xs"
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="phone">Phone Number</Label>
                                        <Input
                                            id="phone"
                                            value={formData.phone}
                                            onChange={(e) =>
                                                setFormData({ ...formData, phone: e.target.value })
                                            }
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="address">Residential Address</Label>
                                    <Input
                                        id="address"
                                        value={formData.address}
                                        onChange={(e) =>
                                            setFormData({ ...formData, address: e.target.value })
                                        }
                                        required
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="pincode">Postal Pincode</Label>
                                    <Input
                                        id="pincode"
                                        value={formData.pincode}
                                        onChange={(e) =>
                                            setFormData({ ...formData, pincode: e.target.value })
                                        }
                                        maxLength={6}
                                        required
                                    />
                                </div>
                            </form>
                        </CardContent>

                        <CardFooter className="pt-4 border-t bg-muted/20 flex flex-col sm:flex-row items-center justify-end gap-3">
                            <Button
                                type="submit"
                                form="profile-form"
                                className="font-bold shadow-md w-full sm:w-auto"
                                disabled={loading}
                            >
                                <Save className="mr-2 h-4 w-4" />
                                {loading ? "Saving Changes..." : "Save Profile Updates"}
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </div>

            <ConfirmationModal
                isOpen={confirmUpdate}
                onClose={() => setConfirmUpdate(false)}
                onConfirm={handleSaveProfile}
                title="Update Profile?"
                description="Are you sure you want to save these changes to your citizen profile?"
                confirmText="Save Changes"
                isLoading={loading}
                icon={SaveAll}
            />

            <ConfirmationModal
                isOpen={confirmPass}
                onClose={() => setConfirmPass(false)}
                onConfirm={handlePasswordUpdate}
                title="Update Password?"
                description="Are you sure you want to change your security password? You will need to use this new password next time you login."
                confirmText="Update Password"
                isLoading={passLoading}
                icon={KeyRound}
            />
        </div>
    );
};
