import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Shield, Sun, Moon, LogOut, Menu, PanelLeft, Bell } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { getDashboardLinks } from "@/components/layout/Sidebar";
import { NotificationModal } from "@/components/common/NotificationModal";
import { useNotifications } from "@/context/NotificationContext";

export const Navbar = () => {
  const { user, role, isAuthenticated, logout } = useAuth();
  const { unreadCount } = useNotifications();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isDashboardRoute = location.pathname.startsWith("/dash");

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const getRoleBadgeColor = () => {
    return "bg-primary/10 text-primary border-primary/20";
  };

  const navLinks = [
    { label: "Report Issue", path: "/complaint/anonymous", alwaysShow: true },
    { label: "Track Token", path: "/complaint/track", alwaysShow: true },
    { label: "Dashboard", path: `/dash/${role}`, authOnly: true },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur-md transition-colors">
      <div className="container mx-auto flex h-16 items-center justify-between px-2.5 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          {isAuthenticated && isDashboardRoute && (
            <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="outline"
                  size="icon"
                  className="md:hidden h-9 w-9 rounded-lg border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary shadow-sm shrink-0"
                  title="Toggle Sidebar"
                >
                  <PanelLeft className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-[75vw] sm:w-[280px] p-4 bg-card/95 backdrop-blur-md border-r"
              >
                <SheetHeader className="pb-4 mb-4 border-b text-left">
                  <SheetTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    {role === "officer"
                      ? "FIELD OFFICER PORTAL"
                      : `${role?.toUpperCase()} PORTAL`}
                  </SheetTitle>
                </SheetHeader>
                <nav className="flex flex-col space-y-1.5">
                  {getDashboardLinks(role).map((link) => {
                    const Icon = link.icon;
                    const isActive =
                      location.pathname === link.path ||
                      (link.path !== `/dash/${role}` &&
                        location.pathname.startsWith(link.path));
                    return (
                      <Link
                        key={link.path}
                        to={link.path}
                        onClick={() => setIsSidebarOpen(false)}
                        className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                          isActive
                            ? "bg-primary text-primary-foreground shadow-md font-semibold"
                            : "text-muted-foreground hover:bg-accent hover:text-foreground"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{link.label}</span>
                      </Link>
                    );
                  })}
                </nav>
              </SheetContent>
            </Sheet>
          )}

          <Link
            to="/"
            className="flex items-center gap-1.5 sm:gap-2.5 transition-opacity hover:opacity-90 shrink-0"
          >
            <div className="flex h-8 w-8 sm:h-9 sm:w-9 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-md">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base sm:text-lg font-bold tracking-tight text-foreground">
                Civic<span className="text-primary">Resolve</span> AI
              </span>
            </div>
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-1 lg:gap-2">
          {navLinks.map((link) => {
            if (link.publicOnly && isAuthenticated) return null;
            if (link.authOnly && !isAuthenticated) return null;
            const isActive =
              location.pathname === link.path ||
              (link.path !== "/" && location.pathname.startsWith(link.path));
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary/10 text-primary font-semibold"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-1 sm:gap-3 shrink-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="rounded-full h-8 w-8 sm:h-9 sm:w-9 text-muted-foreground hover:text-foreground"
            title="Toggle color theme"
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4 text-foreground" />
            ) : (
              <Moon className="h-4 w-4 text-foreground" />
            )}
          </Button>

          {isAuthenticated &&
            ["citizen", "officer", "commissioner"].includes(role) && (
              <NotificationModal
                open={isNotifOpen}
                onOpenChange={setIsNotifOpen}
              />
            )}

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={`hidden sm:inline-flex capitalize font-bold px-2.5 py-0.5 shadow-sm rounded-md ${getRoleBadgeColor()}`}
              >
                {role === "officer" ? "Field Officer" : role}
              </Badge>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-9 w-9 rounded-full p-0 ring-2 ring-primary/20 hover:ring-primary/50"
                  >
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="bg-primary/20 text-primary font-bold">
                        {user?.name?.charAt(0) || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  className="w-auto min-w-[16rem] max-w-[24rem]"
                  align="end"
                  forceMount
                >
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1.5">
                      <p className="text-sm font-bold leading-none text-foreground">
                        {user?.name}
                      </p>
                      <p className="text-xs leading-normal text-muted-foreground break-all">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={handleLogout}
                    className="text-destructive focus:text-destructive focus:bg-destructive/10"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log Out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <div className="flex items-center gap-1 sm:gap-2">
              <Button
                variant="default"
                size="sm"
                onClick={() => navigate("/login")}
                className="font-semibold shadow-md h-8 px-2.5 text-xs sm:h-9 sm:px-3 sm:text-sm"
              >
                <span className="sm:hidden">Sign In</span>
                <span className="hidden sm:inline">Sign In</span>
              </Button>
            </div>
          )}

          <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden h-8 w-8 sm:h-9 sm:w-9 rounded-md"
              >
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent
              side="right"
              className="w-[80vw] sm:w-[350px] overflow-y-auto"
            >
              <SheetHeader className="pb-4 border-b">
                <SheetTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  <span>CivicResolve AI</span>
                </SheetTitle>
              </SheetHeader>
              <div className="flex flex-col gap-3 py-6">
                <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground px-4 mb-1">
                  General Services
                </p>
                {navLinks.map((link) => {
                  if (link.publicOnly && isAuthenticated) return null;
                  if (link.authOnly && !isAuthenticated) return null;
                  return (
                    <Link
                      key={link.path}
                      to={link.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  );
                })}

                {isAuthenticated &&
                  ["citizen", "officer", "commissioner"].includes(role) && (
                    <button
                      onClick={() => {
                        setIsMobileMenuOpen(false);
                        setTimeout(() => setIsNotifOpen(true), 150);
                      }}
                      className="flex items-center justify-between px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-accent transition-colors text-muted-foreground hover:text-foreground text-left w-full"
                    >
                      <span className="flex items-center gap-2.5">
                        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10 text-primary">
                          <Bell className="h-3.5 w-3.5" />
                        </span>
                        <span>Notifications</span>
                      </span>
                      {unreadCount > 0 && (
                        <span className="flex h-5 px-2 items-center justify-center rounded-full bg-primary text-[11px] font-bold text-primary-foreground shadow-xs animate-pulse">
                          {unreadCount}
                        </span>
                      )}
                    </button>
                  )}

                {!isAuthenticated && (
                  <Button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      navigate("/login");
                    }}
                    className="w-full mt-4 font-semibold"
                  >
                    Sign In to Portal
                  </Button>
                )}
                {isAuthenticated && (
                  <Button
                    variant="destructive"
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      handleLogout();
                    }}
                    className="w-full mt-4 justify-start"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Log Out
                  </Button>
                )}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
};
