import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import { useAuth } from "@/context/AuthContext";
import { notificationService } from "@/services/notificationService";
import { toast } from "sonner";

const NotificationContext = createContext(null);

const sortNotifs = (list) =>
  [...list].sort(
    (a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0),
  );

export const NotificationProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);

  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated || !user?.role) {
      setNotifications([]);
      return;
    }

    try {
      const data = await notificationService.getAll();
      setNotifications(sortNotifs(data));
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
      setNotifications([]);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(() => {
      fetchNotifications();
    }, 30000); // Poll every 30 seconds
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = useCallback(async (id) => {
    try {
      const updated = await notificationService.markAsRead(id);
      setNotifications((prev) =>
        sortNotifs(
          prev.map((item) =>
            item.id === id ? { ...item, isRead: true } : item,
          ),
        ),
      );
    } catch (error) {
      console.error("Failed to mark as read:", error);
      toast.error("Failed to mark notification as read");
    }
  }, []);

  const markAsUnread = useCallback(async (id) => {
    try {
      await notificationService.markAsUnread(id);
      setNotifications((prev) =>
        sortNotifs(
          prev.map((item) =>
            item.id === id ? { ...item, isRead: false } : item,
          ),
        ),
      );
    } catch (error) {
      console.error("Failed to mark as unread:", error);
      toast.error("Failed to mark notification as unread");
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) =>
        sortNotifs(prev.map((item) => ({ ...item, isRead: true }))),
      );
      toast.success("All notifications marked as read");
    } catch (error) {
      console.error("Failed to mark all as read:", error);
      toast.error("Failed to mark all as read");
    }
  }, []);

  const deleteNotification = useCallback(async (id) => {
    try {
      await notificationService.deleteOne(id);
      setNotifications((prev) =>
        sortNotifs(prev.filter((item) => item.id !== id)),
      );
    } catch (error) {
      console.error("Failed to delete notification:", error);
      toast.error("Failed to delete notification");
    }
  }, []);

  const clearAll = useCallback(async () => {
    try {
      await notificationService.clearAll();
      setNotifications([]);
      toast.info("Cleared all notifications");
    } catch (error) {
      console.error("Failed to clear notifications:", error);
      toast.error("Failed to clear notifications");
    }
  }, []);

  const addNotification = useCallback((notif) => {
    const newNotif = {
      id: notif.id || `temp-${Date.now()}`,
      createdAt: notif.createdAt || new Date().toISOString(),
      isRead: false,
      ...notif,
    };

    setNotifications((prev) => sortNotifs([newNotif, ...prev]));

    toast[
      newNotif.notifType === "alert" ? "error" : newNotif.notifType || "info"
    ](newNotif.title, {
      description: newNotif.message,
    });
  }, []);

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.isRead).length,
    [notifications],
  );

  const value = useMemo(
    () => ({
      notifications,
      unreadCount,
      markAsRead,
      markAsUnread,
      markAllAsRead,
      deleteNotification,
      clearAll,
      addNotification,
      refetch: fetchNotifications,
    }),
    [
      notifications,
      unreadCount,
      markAsRead,
      markAsUnread,
      markAllAsRead,
      deleteNotification,
      clearAll,
      addNotification,
      fetchNotifications,
    ],
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error(
      "useNotifications must be used within a NotificationProvider",
    );
  }
  return context;
};
