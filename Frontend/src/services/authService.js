import client from "@/api/client";

const SESSION_KEY = "civic_current_session";

export const authService = {
  login: async (emailOrBadge, password, role) => {
    try {
      const response = await client.post("/login", {
        email: emailOrBadge,
        password: password,
        role: role
      });

      const sessionData = {
        token: response.data.token,
        user: response.data.user
      };

      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
      localStorage.setItem("civic_auth_token", sessionData.token);
      return sessionData;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(`Invalid credentials for ${role.toUpperCase()} portal. Please verify your details.`);
    }
  },

  signup: async (userData) => {
    try {

      const response = await client.post("/signup", userData);

      const sessionData = {
        token: response.data.token,
        user: response.data.user
      };

      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
      localStorage.setItem("civic_auth_token", sessionData.token);
      return sessionData;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error("An error occurred during signup.");
    }
  },

  logout: async () => {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem("civic_auth_token");
  },

  getCurrentSession: () => {
    const data = localStorage.getItem(SESSION_KEY);
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  },

  updateProfile: async (userId, updatedData) => {
    try {
      const session = authService.getCurrentSession();
      if (!session) throw new Error("No active session");


      let endpoint = "";
      if (session.user.role === "citizen") endpoint = "/citizen/edit_profile";
      else if (session.user.role === "commissioner") endpoint = "/commissioner/edit_profile";
      else if (session.user.role === "officer") endpoint = "/officer/edit_profile";
      else throw new Error("Invalid role");

      await client.put(endpoint, updatedData);


      let fetchEndpoint = "";
      if (session.user.role === "citizen") fetchEndpoint = "/citizen/profile";
      else if (session.user.role === "commissioner") fetchEndpoint = "/commissioner/profile";
      else if (session.user.role === "officer") fetchEndpoint = "/officer/profile";

      const updatedUserRes = await client.get(fetchEndpoint);



      const newUser = {
        ...session.user,
        ...updatedUserRes.data,
        role: session.user.role,
      };

      const newSession = {
        ...session,
        user: newUser,
      };

      localStorage.setItem(SESSION_KEY, JSON.stringify(newSession));
      return newSession.user;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error("Failed to update profile.");
    }
  },

  updatePassword: async (currentPassword, newPassword) => {
    try {
      const session = authService.getCurrentSession();
      if (!session) throw new Error("No active session");

      const response = await client.put("/update_password", {
        currentPassword,
        newPassword
      });

      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error("Failed to update password.");
    }
  }
};
