import client from "@/api/client";

export const notificationService = {
    getAll: async () => {
        const response = await client.get("/notifications");
        return response.data.notifications || [];
    },

    markAsRead: async (id) => {
        const response = await client.patch(`/notifications/${id}/read`);
        return response.data;
    },

    markAsUnread: async (id) => {
        const response = await client.patch(`/notifications/${id}/unread`);
        return response.data;
    },

    markAllAsRead: async () => {
        const response = await client.patch("/notifications/read-all");
        return response.data;
    },

    deleteOne: async (id) => {
        const response = await client.delete(`/notifications/${id}`);
        return response.data;
    },

    clearAll: async () => {
        const response = await client.delete("/notifications");
        return response.data;
    },
};
