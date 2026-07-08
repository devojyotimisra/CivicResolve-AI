import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import {
  LayoutDashboard,
  FileText,
  Receipt,
  Building2,
  User,
  Tags,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export const getCitizenLinks = () => [
  { label: "Dashboard", path: "/dash/citizen", icon: LayoutDashboard },
  { label: "Utility Bills", path: "/dash/citizen/bills", icon: Receipt },
  {
    label: "Civic Facilities",
    path: "/dash/citizen/facilities",
    icon: Building2,
  },
  { label: "Profile", path: "/dash/citizen/profile", icon: User },
];

export const getOfficerLinks = () => [
  { label: "Dashboard", path: "/dash/officer", icon: LayoutDashboard },
  { label: "Profile", path: "/dash/officer/profile", icon: User },
];

export const getCommissionerLinks = () => [
  { label: "Dashboard", path: "/dash/commissioner", icon: LayoutDashboard },
  {
    label: "Complaints",
    path: "/dash/commissioner/complaints",
    icon: FileText,
  },
  {
    label: "Field Officers",
    path: "/dash/commissioner/officers",
    icon: ShieldCheck,
  },
  {
    label: "Facilities",
    path: "/dash/commissioner/facilities",
    icon: Building2,
  },
  { label: "Departments", path: "/dash/commissioner/departments", icon: Tags },
  { label: "Bills", path: "/dash/commissioner/bills", icon: Receipt },
  { label: "Profile", path: "/dash/commissioner/profile", icon: User },
];

export const getDashboardLinks = (role) => {
  if (role === "commissioner") return getCommissionerLinks();
  if (role === "officer") return getOfficerLinks();
  return getCitizenLinks();
};

export const Sidebar = () => {
  const { role } = useAuth();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem("sidebar_collapsed");
      return saved !== null ? JSON.parse(saved) : false;
    } catch (e) {
      return false;
    }
  });
  const sidebarRef = React.useRef(null);

  React.useEffect(() => {
    try {
      localStorage.setItem("sidebar_collapsed", JSON.stringify(isCollapsed));
    } catch (e) {}
  }, [isCollapsed]);

  const links = getDashboardLinks(role);

  React.useEffect(() => {
    const sidebar = sidebarRef.current;
    if (!sidebar) return;

    const handleWheel = (e) => {
      const nav = sidebar.querySelector("nav");
      if (!nav) {
        e.preventDefault();
        return;
      }

      const isScrollable = nav.scrollHeight > nav.clientHeight;
      if (!isScrollable) {
        e.preventDefault();
        return;
      }

      const atTop = nav.scrollTop <= 0 && e.deltaY < 0;
      const atBottom =
        Math.abs(nav.scrollHeight - nav.clientHeight - nav.scrollTop) <= 1 &&
        e.deltaY > 0;

      if (atTop || atBottom) {
        e.preventDefault();
      }
    };

    sidebar.addEventListener("wheel", handleWheel, { passive: false });
    return () => sidebar.removeEventListener("wheel", handleWheel);
  }, []);

  return (
    <aside
      ref={sidebarRef}
      className={`hidden md:flex flex-col border-r bg-card/60 backdrop-blur-md h-full p-3 transition-all duration-300 ease-in-out shrink-0 select-none ${
        isCollapsed ? "w-16 items-center" : "w-64"
      }`}
    >
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-6 z-20 flex h-6 w-6 items-center justify-center rounded-full border bg-background text-foreground shadow-md hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
        title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
      >
        {isCollapsed ? (
          <ChevronRight className="h-3.5 w-3.5" />
        ) : (
          <ChevronLeft className="h-3.5 w-3.5" />
        )}
      </button>

      <div
        className={`mb-6 px-2 py-2 transition-opacity duration-300 shrink-0 ${isCollapsed ? "text-center" : ""}`}
      >
        {isCollapsed ? (
          <span
            className="text-xs font-black text-primary block truncate"
            title={
              role === "officer"
                ? "FIELD OFFICER PORTAL"
                : `${role?.toUpperCase()} PORTAL`
            }
          >
            {role?.charAt(0)?.toUpperCase()}P
          </span>
        ) : (
          <h2 className="text-xs font-extrabold uppercase tracking-wider text-muted-foreground truncate">
            {role === "officer"
              ? "FIELD OFFICER PORTAL"
              : `${role?.toUpperCase()} PORTAL`}
          </h2>
        )}
      </div>

      <nav className="flex-1 min-h-0 space-y-1.5 w-full overflow-y-auto overflow-x-hidden pr-1 overscroll-contain">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive =
            location.pathname === link.path ||
            (link.path !== `/dash/${role}` &&
              location.pathname.startsWith(link.path));
          return (
            <Link
              key={link.path}
              to={link.path}
              title={isCollapsed ? link.label : undefined}
              className={`flex items-center rounded-xl px-3 py-2.5 text-sm font-medium transition-all group relative ${
                isCollapsed ? "justify-center px-0" : "gap-3"
              } ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-md font-semibold"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <Icon
                className={`h-4 w-4 shrink-0 transition-transform group-hover:scale-110 ${
                  isActive ? "text-primary-foreground" : "text-muted-foreground"
                }`}
              />
              {!isCollapsed && <span className="truncate">{link.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
