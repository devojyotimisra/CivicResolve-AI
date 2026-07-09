import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  useCallback,
} from "react";
import { authService } from "@/services/authService";
import { toast } from "sonner";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = authService.getCurrentSession();
    if (session && session.user && session.token) {
      setUser(session.user);
      setToken(session.token);
    }
    setLoading(false);
  }, []);

  const login = async (emailOrBadge, password, role) => {
    try {
      const session = await authService.login(emailOrBadge, password, role);
      setUser(session.user);
      setToken(session.token);
      toast.success(
        `Welcome to the ${role.toUpperCase()} portal, ${session.user.name}!`,
      );
      return session;
    } catch (error) {
      toast.error(error.message || "Login failed");
      throw error;
    }
  };

  const signup = async (userData) => {
    try {
      const session = await authService.signup(userData);
      setUser(session.user);
      setToken(session.token);
      toast.success(
        `Account created successfully! Welcome, ${session.user.name}!`,
      );
      return session;
    } catch (error) {
      toast.error(error.message || "Registration failed");
      throw error;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setToken(null);
    toast.info("You have been logged out securely.");
  };

  const updateProfile = useCallback(
    async (updatedData) => {
      try {
        if (!user) return;
        const updatedUser = await authService.updateProfile(
          user.id,
          updatedData,
        );
        setUser(updatedUser);
        toast.success("Profile updated successfully!");
        return updatedUser;
      } catch (error) {
        toast.error(error.message || "Failed to update profile");
        throw error;
      }
    },
    [user],
  );

  const value = useMemo(
    () => ({
      user,
      role: user?.role || null,
      token,
      loading,
      isAuthenticated: !!user,
      login,
      signup,
      logout,
      updateProfile,
    }),
    [user, token, loading, updateProfile],
  );

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
