import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { INITIAL_USERS } from "@/api/mockSeedData";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ShieldCheck, Lock, ArrowRight } from "lucide-react";

export const CommissionerLoginTab = () => {
  const defaultComm =
    INITIAL_USERS.find((u) => u.role === "commissioner") || {};
  const [emailOrBadge, setEmailOrBadge] = useState(
    defaultComm.badgeId || defaultComm.email,
  );
  const [password, setPassword] = useState(defaultComm.password);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(emailOrBadge, password, "commissioner");
      navigate("/dash/commissioner");
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-4">
      {error && (
        <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-xs text-destructive font-medium">
          {error}
        </div>
      )}
      <div className="space-y-2">
        <Label htmlFor="comm-email">Badge ID or Email</Label>
        <div className="relative">
          <ShieldCheck className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="comm-email"
            type="text"
            placeholder="e.g., COM-001 or commissioner1@civicresolveai.org"
            value={emailOrBadge}
            onChange={(e) => setEmailOrBadge(e.target.value)}
            className="pl-9"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="comm-password">Password</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="comm-password"
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
        className="w-full font-semibold mt-2"
        disabled={loading}
      >
        {loading ? "Authenticating..." : "Sign In"}
        {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
      </Button>
    </form>
  );
};
