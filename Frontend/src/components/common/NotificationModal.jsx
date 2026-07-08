import React, { useState, useRef } from "react";
import { useNotifications } from "@/context/NotificationContext";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Bell,
  BellRing,
  CheckCircle2,
  AlertTriangle,
  Info,
  Trash2,
  Check,
  Inbox,
} from "lucide-react";

const formatTimeAgo = (dateString) => {
  if (!dateString) return "";
  const now = new Date();
  const date = new Date(dateString);
  const diffInSeconds = Math.floor((now - date) / 1000);

  if (isNaN(diffInSeconds) || diffInSeconds < 60) return "Just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
};

export const NotificationModal = ({
  customTrigger,
  open: propOpen,
  onOpenChange: propOnOpenChange,
}) => {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAsUnread,
    deleteNotification,
  } = useNotifications();
  const { user } = useAuth();
  const [internalOpen, setInternalOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const ignoreOutsideRef = useRef(false);
  const open = propOpen !== undefined ? propOpen : internalOpen;
  const setOpen =
    propOnOpenChange !== undefined ? propOnOpenChange : setInternalOpen;

  const openConfirm = (data) => {
    ignoreOutsideRef.current = true;
    setConfirmDelete(data);
  };

  const closeConfirm = () => {
    setConfirmDelete(null);
    setTimeout(() => {
      ignoreOutsideRef.current = false;
    }, 500);
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "alert":
        return (
          <div className="p-2 rounded-xl bg-destructive/15 text-destructive shrink-0 shadow-sm">
            <AlertTriangle className="h-4 w-4" />
          </div>
        );
      case "warning":
        return (
          <div className="p-2 rounded-xl bg-amber-500/15 text-amber-600 dark:text-amber-400 shrink-0 shadow-sm">
            <AlertTriangle className="h-4 w-4" />
          </div>
        );
      case "success":
        return (
          <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 shrink-0 shadow-sm">
            <CheckCircle2 className="h-4 w-4" />
          </div>
        );
      case "info":
      default:
        return (
          <div className="p-2 rounded-xl bg-primary/15 text-primary shrink-0 shadow-sm">
            <Info className="h-4 w-4" />
          </div>
        );
    }
  };

  const renderNotificationList = (list) => {
    if (list.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-52 text-center p-6 border border-dashed rounded-2xl bg-muted/20 my-3 animate-in fade-in-50 duration-300">
          <div className="h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center mb-3 text-muted-foreground/50">
            <Inbox className="h-6 w-6" />
          </div>
          <p className="text-sm font-semibold text-foreground">
            No notifications here
          </p>
          <p className="text-xs text-muted-foreground mt-1 max-w-[200px]">
            You're all caught up! When civic alerts occur, they will appear
            right here.
          </p>
        </div>
      );
    }

    const sortedList = [...list].sort(
      (a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0),
    );

    return (
      <div className="flex-1 overflow-y-auto pr-1 space-y-2.5 my-3 max-h-[50vh] sm:max-h-[55vh] min-h-[220px] custom-scrollbar">
        {sortedList.map((item) => (
          <div
            key={item.id}
            className={cn(
              "group relative flex items-start gap-3 p-3.5 rounded-2xl border transition-all duration-200 hover:shadow-md hover:border-primary/30",
              item.read
                ? "bg-card/60 border-border/60 opacity-80 hover:opacity-100"
                : "bg-primary/5 border-primary/25 shadow-xs font-medium",
            )}
          >
            {getTypeIcon(item.type)}

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <h4
                  className={cn(
                    "text-sm font-semibold truncate tracking-tight text-foreground",
                    !item.read && "text-primary dark:text-primary font-bold",
                  )}
                >
                  {item.title}
                </h4>
                <div className="flex items-center gap-1.5 shrink-0">
                  <span
                    className="text-[10px] font-medium text-muted-foreground bg-muted/60 px-1.5 py-0.5 rounded-md"
                    title={
                      item.timestamp
                        ? new Date(item.timestamp).toLocaleString()
                        : "Arrival time"
                    }
                  >
                    {formatTimeAgo(item.timestamp)}
                  </span>
                  {!item.read ? (
                    <button
                      onClick={() => markAsRead(item.id)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground transition-all duration-150 shadow-2xs"
                      title="Mark as read"
                    >
                      <Check className="h-3 w-3" />
                      <span>Read</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => markAsUnread(item.id)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-muted text-muted-foreground hover:bg-primary/10 hover:text-primary transition-all duration-150 shadow-2xs"
                      title="Mark as unread"
                    >
                      <Bell className="h-3 w-3" />
                      <span>Unread</span>
                    </button>
                  )}
                  <button
                    onClick={() =>
                      openConfirm({
                        type: "single",
                        id: item.id,
                        title: item.title,
                      })
                    }
                    className="p-1 rounded-md text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all"
                    title="Delete notification"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              <p className="text-xs text-muted-foreground mt-1 leading-relaxed line-clamp-2">
                {item.message}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const unreadList = notifications.filter((n) => !n.read);
  const readList = notifications.filter((n) => n.read);

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          {customTrigger || (
            <Button
              variant="ghost"
              size="icon"
              className="relative h-8 w-8 sm:h-9 sm:w-9 rounded-full text-muted-foreground hover:text-foreground hover:bg-accent/80 transition-all duration-200 focus-visible:ring-2 focus-visible:ring-primary/50"
              title="Notifications"
            >
              {unreadCount > 0 ? (
                <BellRing className="h-4 w-4 text-primary transition-transform duration-200" />
              ) : (
                <Bell className="h-4 w-4" />
              )}
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 sm:h-5 sm:w-5 items-center justify-center rounded-full bg-primary text-[10px] sm:text-xs font-bold text-primary-foreground shadow-md animate-pulse ring-2 ring-background">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Button>
          )}
        </DialogTrigger>

        <DialogContent
          onPointerDownOutside={(e) => {
            if (ignoreOutsideRef.current) e.preventDefault();
          }}
          onInteractOutside={(e) => {
            if (ignoreOutsideRef.current) e.preventDefault();
          }}
          onFocusOutside={(e) => e.preventDefault()}
          className="w-[95vw] sm:w-full max-w-lg max-h-[88vh] flex flex-col p-4 sm:p-6 bg-card border-border shadow-2xl rounded-2xl overflow-hidden animate-in fade-in-0 zoom-in-95 duration-200"
        >
          <DialogHeader className="pb-2 border-b border-border/40 text-left">
            <div className="flex items-center justify-between gap-2">
              <DialogTitle className="flex items-center gap-2.5 text-lg font-bold tracking-tight text-foreground">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-xs">
                  <Bell className="h-4 w-4" />
                </div>
                <span>Notifications</span>
                {unreadCount > 0 && (
                  <Badge
                    variant="secondary"
                    className="bg-primary/15 text-primary font-bold text-xs px-2 py-0.5 rounded-full shadow-2xs animate-pulse"
                  >
                    {unreadCount} New
                  </Badge>
                )}
              </DialogTitle>
            </div>
            <DialogDescription className="text-xs sm:text-sm text-muted-foreground mt-1">
              Stay updated with your latest civic activities, alerts, and{" "}
              {user?.role || "user"} notices.
            </DialogDescription>
          </DialogHeader>

          <Tabs
            defaultValue="all"
            className="flex-1 flex flex-col min-h-0 mt-3"
          >
            <TabsList className="grid w-full grid-cols-3 bg-muted/60 p-1 rounded-xl border border-border/40 shadow-inner">
              <TabsTrigger
                value="all"
                className="rounded-lg text-xs font-semibold data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all"
              >
                All ({notifications.length})
              </TabsTrigger>
              <TabsTrigger
                value="unread"
                className="rounded-lg text-xs font-semibold data-[state=active]:bg-background data-[state=active]:text-primary data-[state=active]:shadow-sm transition-all"
              >
                Unread ({unreadCount})
              </TabsTrigger>
              <TabsTrigger
                value="read"
                className="rounded-lg text-xs font-semibold data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm transition-all"
              >
                Read ({readList.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent
              value="all"
              className="flex-1 flex flex-col min-h-0 mt-0 focus-visible:outline-none"
            >
              {renderNotificationList(notifications)}
            </TabsContent>
            <TabsContent
              value="unread"
              className="flex-1 flex flex-col min-h-0 mt-0 focus-visible:outline-none"
            >
              {renderNotificationList(unreadList)}
            </TabsContent>
            <TabsContent
              value="read"
              className="flex-1 flex flex-col min-h-0 mt-0 focus-visible:outline-none"
            >
              {renderNotificationList(readList)}
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!confirmDelete}
        onOpenChange={(val) => !val && closeConfirm()}
      >
        <DialogContent className="w-[90vw] sm:w-full max-w-md bg-card/95 border shadow-2xl rounded-2xl p-6 z-[60] text-foreground">
          <DialogHeader className="text-left">
            <DialogTitle className="flex items-center gap-2.5 text-lg font-bold tracking-tight text-foreground">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl shrink-0 shadow-sm border">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <span>Delete Notification?</span>
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground mt-2">
              Are you sure you want to delete "
              {confirmDelete?.title || "this notification"}"? This action cannot
              be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="mt-5 flex flex-row justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={closeConfirm}
              className="rounded-xl font-semibold hover:bg-accent"
            >
              Cancel
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => {
                if (confirmDelete?.id) {
                  deleteNotification(confirmDelete.id);
                }
                closeConfirm();
              }}
              className="rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-sm"
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
