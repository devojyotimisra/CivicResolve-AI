import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { INITIAL_USERS } from "@/api/mockSeedData";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Lock, ArrowRight } from "lucide-react";

export const CitizenLoginTab = () => {
  const defaultCitizen = INITIAL_USERS.find((u) => u.role === "citizen") || {};
  const [email, setEmail] = useState(defaultCitizen.email);
  const [password, setPassword] = useState(defaultCitizen.password);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password, "citizen");
      navigate("/dash/citizen");
    } catch (err) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-4">
      <div className="space-y-2">
        <Label htmlFor="citizen-email">Email Address or Phone Number</Label>
        <div className="relative">
          <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="citizen-email"
            type="text"
            placeholder="e.g., citizen@civic.org"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="pl-9"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="citizen-password">Password</Label>
        </div>
        <div className="relative">
          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="citizen-password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="pl-9"
            required
          />
        </div>
      </div>

      <Button
        type="submit"
        className="w-full font-semibold shadow-md mt-2"
        disabled={loading}
      >
        {loading ? "Authenticating..." : "Sign In"}
        {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
      </Button>

      <div className="text-center pt-2 text-xs text-muted-foreground">
        Don't have an account yet?{" "}
        <Link
          to="/signup"
          className="font-semibold text-primary hover:underline"
        >
          Register Here
        </Link>
      </div>
    </form>
  );
};
