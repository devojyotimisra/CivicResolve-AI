import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { INITIAL_USERS } from "@/api/mockSeedData";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Shield, Lock, ArrowRight } from "lucide-react";

export const OfficerLoginTab = () => {
  const defaultOfficer = INITIAL_USERS.find((u) => u.role === "officer") || {};
  const [badgeId, setBadgeId] = useState(
    defaultOfficer.badgeId || defaultOfficer.email,
  );
  const [password, setPassword] = useState(defaultOfficer.password);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(badgeId, password, "officer");
      navigate("/dash/officer");
    } catch (err) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 pt-4">
      <div className="space-y-2">
        <Label htmlFor="officer-badge">Badge ID or Email</Label>
        <div className="relative">
          <Shield className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="officer-badge"
            type="text"
            placeholder="e.g., OFF-104 or officer@civic.org"
            value={badgeId}
            onChange={(e) => setBadgeId(e.target.value)}
            className="pl-9"
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="officer-password">Password</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            id="officer-password"
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
        {loading ? "Authenticating...." : "Sign In"}
        {!loading && <ArrowRight className="ml-2 h-4 w-4" />}
      </Button>
    </form>
  );
};
