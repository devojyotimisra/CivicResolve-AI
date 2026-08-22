import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Mail, Phone, MapPin, Lock, ArrowRight } from "lucide-react";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";
import { toast } from "sonner";

export const Signup = () => {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        phone: "",
        address: "",
        pincode: "",
        password: "",
        confirmPassword: "",
    });
    const [loading, setLoading] = useState(false);
    const [confirmSubmit, setConfirmSubmit] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    const submitForm = (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            toast.error("Passwords do not match.");
            return;
        }
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
        if (!passwordRegex.test(formData.password)) {
            toast.error(
                "Password must be at least 8 characters long and contain a number and a special character."
            );
            return;
        }
        const phoneRegex = /^(\+\d{1,3}[- ]?)?\d{10}$/;
        if (!phoneRegex.test(formData.phone)) {
            toast.error("Please enter a valid 10-digit phone number.");
            return;
        }
        const pincodeRegex = /^[0-9]{6}$/;
        if (!pincodeRegex.test(formData.pincode)) {
            toast.error("Please enter a valid 6-digit pincode.");
            return;
        }
        setConfirmSubmit(true);
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await signup({
                name: formData.name,
                email: formData.email,
                phone: formData.phone,
                address: formData.address,
                pincode: formData.pincode,
                password: formData.password,
            });
            navigate("/dash/citizen");
        } catch {
            setConfirmSubmit(false);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-gradient-to-b from-background to-muted/30">
            <div className="w-full max-w-lg">
                <Card className="border-2 shadow-xl bg-card/90 backdrop-blur-md">
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-center">
                            <CardTitle className="text-xl">Sign Up</CardTitle>
                        </div>
                    </CardHeader>

                    <CardContent className="pt-2">
                        <form onSubmit={submitForm} className="space-y-2">
                            <div className="space-y-2">
                                <Label htmlFor="name">Full Name</Label>
                                <div className="relative">
                                    <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="name"
                                        type="text"
                                        placeholder="e.g., Rajesh Kumar"
                                        value={formData.name}
                                        onChange={handleChange}
                                        className="pl-9"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="citizen@example.com"
                                            value={formData.email}
                                            onChange={handleChange}
                                            className="pl-9"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="phone">Phone Number</Label>
                                    <div className="relative">
                                        <Phone className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="phone"
                                            type="tel"
                                            placeholder="9876543210"
                                            value={formData.phone}
                                            onChange={handleChange}
                                            className="pl-9"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="address">Residential Address</Label>
                                <div className="relative">
                                    <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="address"
                                        type="text"
                                        placeholder="e.g., 42, MG Road, Adyar, Chennai"
                                        value={formData.address}
                                        onChange={handleChange}
                                        className="pl-9"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="pincode">Postal Pincode</Label>
                                <Input
                                    id="pincode"
                                    type="text"
                                    placeholder="600020"
                                    value={formData.pincode}
                                    onChange={handleChange}
                                    maxLength={6}
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                                <div className="space-y-2">
                                    <Label htmlFor="password">Password</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="password"
                                            type="password"
                                            placeholder="••••••••"
                                            value={formData.password}
                                            onChange={handleChange}
                                            className="pl-9"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="confirmPassword">Confirm Password</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input
                                            id="confirmPassword"
                                            type="password"
                                            placeholder="••••••••"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            className="pl-9"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>

                            <Button
                                type="submit"
                                className="w-full font-semibold shadow-lg mt-4 h-11"
                                disabled={loading}
                            >
                                {loading
                                    ? "Creating Account..."
                                    : "Complete Registration & Sign In"}
                                {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
                            </Button>
                        </form>
                    </CardContent>

                    <CardFooter className="flex-col gap-2 py-3 px-4 text-center">
                        <div className="text-xs text-muted-foreground">
                            Already registered?{" "}
                            <Link
                                to="/login"
                                className="font-semibold text-primary hover:underline"
                            >
                                Sign In Here
                            </Link>
                        </div>
                    </CardFooter>
                </Card>
            </div>

            <ConfirmationModal
                isOpen={confirmSubmit}
                onClose={() => setConfirmSubmit(false)}
                onConfirm={handleSubmit}
                title="Create Citizen Account?"
                description="Are you sure you want to register with these details? You will be able to file complaints and pay taxes with this account."
                confirmText="Register"
                isLoading={loading}
                icon={User}
            />
        </div>
    );
};
