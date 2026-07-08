import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { NotificationProvider } from "@/context/NotificationContext";
import { Toaster } from "@/components/ui/sonner";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { Home } from "@/pages/general/Home";
import { Login } from "@/pages/general/Login";
import { Signup } from "@/pages/general/Signup";
import { AnonymousComplaint } from "@/pages/general/AnonymousComplaint";
import { TrackComplaint } from "@/pages/general/TrackComplaint";
import { Error403 } from "@/pages/general/Error403";
import { Error404 } from "@/pages/general/Error404";
import { CitizenDashboard } from "@/pages/citizen/Dashboard";
import { CitizenBills } from "@/pages/citizen/Bills";
import { CitizenFacilities } from "@/pages/citizen/Facilities";
import { CitizenProfile } from "@/pages/citizen/Profile";
import { OfficerDashboard } from "@/pages/officer/Dashboard";
import { OfficerProfile } from "@/pages/officer/Profile";
import { CommissionerDashboard } from "@/pages/commissioner/Dashboard";
import { CommissionerComplaints } from "@/pages/commissioner/Complaints";
import { CommissionerOfficers } from "@/pages/commissioner/Officers";
import { CommissionerProfile } from "@/pages/commissioner/Profile";
import { CommissionerFacilities } from "@/pages/commissioner/Facilities";
import { CommissionerDepartments } from "@/pages/commissioner/Departments";
import { CommissionerBills } from "@/pages/commissioner/Bills";

const DashboardLayout = ({ children }) => {
  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden bg-background">
      <Sidebar />
      <main className="flex-1 h-full overflow-y-auto p-4 sm:p-6 lg:p-8 transition-all">
        <div className="max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
};

const PublicLayout = ({ children }) => {
  return <main className="flex-1 flex flex-col bg-background">{children}</main>;
};

const DashboardRedirect = () => {
  const { user, isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (user?.role === "commissioner")
    return <Navigate to="/dash/commissioner" replace />;
  if (user?.role === "officer") return <Navigate to="/dash/officer" replace />;
  return <Navigate to="/dash/citizen" replace />;
};

export function AppContent() {
  const location = useLocation();
  const isDashboardRoute = location.pathname.startsWith("/dash");

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground font-sans antialiased selection:bg-primary/20 selection:text-primary">
      <Navbar />

      <div className="flex-1 flex flex-col">
        <Routes>
          <Route
            path="/"
            element={
              <PublicLayout>
                <Home />
              </PublicLayout>
            }
          />
          <Route
            path="/login"
            element={
              <PublicLayout>
                <Login />
              </PublicLayout>
            }
          />
          <Route
            path="/signup"
            element={
              <PublicLayout>
                <Signup />
              </PublicLayout>
            }
          />
          <Route
            path="/complaint/anonymous"
            element={
              <PublicLayout>
                <AnonymousComplaint />
              </PublicLayout>
            }
          />
          <Route
            path="/complaint/track"
            element={
              <PublicLayout>
                <TrackComplaint />
              </PublicLayout>
            }
          />
          <Route
            path="/403"
            element={
              <PublicLayout>
                <Error403 />
              </PublicLayout>
            }
          />
          <Route
            path="/404"
            element={
              <PublicLayout>
                <Error404 />
              </PublicLayout>
            }
          />

          <Route path="/dash" element={<DashboardRedirect />} />

          <Route
            path="/dash/citizen/*"
            element={
              <ProtectedRoute allowedRoles={["citizen"]}>
                <DashboardLayout>
                  <Routes>
                    <Route path="/" element={<CitizenDashboard />} />
                    <Route path="/bills" element={<CitizenBills />} />
                    <Route path="/facilities" element={<CitizenFacilities />} />
                    <Route
                      path="/facilities/book/:id"
                      element={
                        <Navigate to="/dash/citizen/facilities" replace />
                      }
                    />
                    <Route
                      path="/bookings"
                      element={
                        <Navigate to="/dash/citizen/facilities" replace />
                      }
                    />
                    <Route path="/profile" element={<CitizenProfile />} />
                    <Route
                      path="*"
                      element={<Navigate to="/dash/citizen" replace />}
                    />
                  </Routes>
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dash/officer/*"
            element={
              <ProtectedRoute allowedRoles={["officer"]}>
                <DashboardLayout>
                  <Routes>
                    <Route path="/" element={<OfficerDashboard />} />
                    <Route path="/profile" element={<OfficerProfile />} />
                    <Route
                      path="*"
                      element={<Navigate to="/dash/officer" replace />}
                    />
                  </Routes>
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dash/commissioner/*"
            element={
              <ProtectedRoute allowedRoles={["commissioner"]}>
                <DashboardLayout>
                  <Routes>
                    <Route path="/" element={<CommissionerDashboard />} />
                    <Route
                      path="/complaints"
                      element={<CommissionerComplaints />}
                    />
                    <Route
                      path="/officers"
                      element={<CommissionerOfficers />}
                    />
                    <Route
                      path="/facilities"
                      element={<CommissionerFacilities />}
                    />
                    <Route
                      path="/departments"
                      element={<CommissionerDepartments />}
                    />
                    <Route path="/bills" element={<CommissionerBills />} />

                    <Route path="/profile" element={<CommissionerProfile />} />
                    <Route
                      path="*"
                      element={<Navigate to="/dash/commissioner" replace />}
                    />
                  </Routes>
                </DashboardLayout>
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </div>

      {!isDashboardRoute && <Footer />}
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="civic-theme">
      <AuthProvider>
        <NotificationProvider>
          <Router>
            <AppContent />
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
