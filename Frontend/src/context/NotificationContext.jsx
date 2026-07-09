import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import { useAuth } from "@/context/AuthContext";
import { INITIAL_NOTIFICATIONS } from "@/api/mockSeedData";
import { toast } from "sonner";

const NotificationContext = createContext(null);

const sortNotifs = (list) =>
  [...list].sort(
    (a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0),
  );

export const NotificationProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!isAuthenticated || !user?.role) {
      setNotifications([]);
      return;
    }

    const storageKey = `civic_notifications_${user.id || user.role}`;
    const defaults = INITIAL_NOTIFICATIONS[user.role] || [];
    const stored = localStorage.getItem(storageKey);
    let currentList = [];

    if (stored) {
      try {
        currentList = JSON.parse(stored);
      } catch {
        currentList = [];
      }
    }

    const syncedDefaults = defaults.map((seedNotif) => {
      const existing = currentList.find((n) => n.id === seedNotif.id);
      return existing ? { ...existing, ...seedNotif } : seedNotif;
    });

    const customNotifs = currentList.filter(
      (n) => !defaults.some((seed) => seed.id === n.id),
    );
    const finalList = sortNotifs([...syncedDefaults, ...customNotifs]);

    setNotifications(finalList);
    localStorage.setItem(storageKey, JSON.stringify(finalList));
  }, [isAuthenticated, user]);

  const saveToStorage = useCallback(
    (updatedList) => {
      if (!isAuthenticated || !user?.role) return;
      const storageKey = `civic_notifications_${user.id || user.role}`;
      localStorage.setItem(storageKey, JSON.stringify(updatedList));
    },
    [isAuthenticated, user],
  );

  const markAsRead = useCallback(
    (id) => {
      setNotifications((prev) => {
        const updated = sortNotifs(
          prev.map((item) =>
            item.id === id ? { ...item, isRead: true } : item,
          ),
        );
        saveToStorage(updated);
        return updated;
      });
    },
    [saveToStorage],
  );

  const markAsUnread = useCallback(
    (id) => {
      setNotifications((prev) => {
        const updated = sortNotifs(
          prev.map((item) =>
            item.id === id ? { ...item, isRead: false } : item,
          ),
        );
        saveToStorage(updated);
        return updated;
      });
    },
    [saveToStorage],
  );

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => {
      const updated = sortNotifs(
        prev.map((item) => ({ ...item, isRead: true })),
      );
      saveToStorage(updated);
      toast.success("All notifications marked as read");
      return updated;
    });
  }, [saveToStorage]);

  const deleteNotification = useCallback(
    (id) => {
      setNotifications((prev) => {
        const updated = sortNotifs(prev.filter((item) => item.id !== id));
        saveToStorage(updated);
        return updated;
      });
    },
    [saveToStorage],
  );

  const clearAll = useCallback(() => {
    setNotifications([]);
    saveToStorage([]);
    toast.info("Cleared all notifications");
  }, [saveToStorage]);

  const addNotification = useCallback(
    (notif) => {
      const newNotif = {
        id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        createdAt: new Date().toISOString(),
        isRead: false,
        ...notif,
      };

      setNotifications((prev) => {
        const updated = sortNotifs([newNotif, ...prev]);
        saveToStorage(updated);
        return updated;
      });

      toast[
        newNotif.notifType === "alert" ? "error" : newNotif.notifType || "info"
      ](newNotif.title, {
        description: newNotif.message,
      });
    },
    [saveToStorage],
  );

  const simulateNewNotification = useCallback(() => {
    if (!user?.role) {
      toast.error("Please log in to simulate notifications");
      return;
    }

    const pool =
      INITIAL_NOTIFICATIONS[user.role] || INITIAL_NOTIFICATIONS.citizen || [];
    if (!pool.length) return;
    const randomNotif = pool[Math.floor(Math.random() * pool.length)];
    addNotification({
      title: randomNotif.title,
      message: randomNotif.message,
      notifType: randomNotif.notifType,
    });
  }, [user, addNotification]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.simulateNotification = simulateNewNotification;
    }
  }, [simulateNewNotification]);

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
      simulateNewNotification,
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
      simulateNewNotification,
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
