import { INITIAL_USERS } from "@/api/mockSeedData";

const USERS_KEY = "civic_users_v2";
const SESSION_KEY = "civic_current_session";

function getUsersFromStorage() {
  const data = localStorage.getItem(USERS_KEY);
  let storedUsers = [];
  if (data) {
    try {
      storedUsers = JSON.parse(data);
    } catch (e) {
      storedUsers = [];
    }
  }
  
  const syncedUsers = INITIAL_USERS.map((seedUser) => {
    const existing = storedUsers.find((u) => u.id === seedUser.id);
    return existing ? { ...existing, ...seedUser } : seedUser;
  });
  
  const customUsers = storedUsers.filter((u) => !INITIAL_USERS.some((seed) => seed.id === u.id));
  const finalUsers = [...syncedUsers, ...customUsers];
  
  localStorage.setItem(USERS_KEY, JSON.stringify(finalUsers));
  return finalUsers;
}

function saveUsersToStorage(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export const authService = {
  login: async (emailOrBadge, password, role) => {
    // Simulate slight network latency
    await new Promise((res) => setTimeout(res, 400));
    const users = getUsersFromStorage();
    
    const user = users.find((u) => {
      if (u.badgeId && u.badgeId.toLowerCase() === emailOrBadge.toLowerCase() && u.password === password && u.role === role) {
        return true;
      }
      return u.email?.toLowerCase() === emailOrBadge.toLowerCase() && u.password === password && u.role === role;
    });

    if (!user) {
      throw new Error(`Invalid credentials for ${role.toUpperCase()} portal. Please verify your email/ID and password.`);
    }

    if (user.isActive === false) {
      throw new Error("This account has been deactivated by system administration.");
    }

    const sessionData = {
      token: `jwt_mock_${user.id}_${Date.now()}`,
      user: user,
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    localStorage.setItem("civic_auth_token", sessionData.token);
    return sessionData;
  },

  signup: async (userData) => {
    await new Promise((res) => setTimeout(res, 500));
    const users = getUsersFromStorage();

    if (users.some((u) => u.email?.toLowerCase() === userData.email?.toLowerCase())) {
      throw new Error("An account with this email address already exists.");
    }

    const newUser = {
      id: `usr_citizen_${Date.now()}`,
      role: "citizen",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80",
      ...userData,
    };

    users.push(newUser);
    saveUsersToStorage(users);

    const sessionData = {
      token: `jwt_mock_${newUser.id}_${Date.now()}`,
      user: newUser,
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    localStorage.setItem("civic_auth_token", sessionData.token);
    return sessionData;
  },

  logout: async () => {
    await new Promise((res) => setTimeout(res, 200));
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem("civic_auth_token");
  },

  getCurrentSession: () => {
    const data = localStorage.getItem(SESSION_KEY);
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch (e) {
      return null;
    }
  },

  updateProfile: async (userId, updatedData) => {
    await new Promise((res) => setTimeout(res, 400));
    const users = getUsersFromStorage();
    const index = users.findIndex((u) => u.id === userId);
    if (index === -1) throw new Error("User not found");

    const updatedUser = { ...users[index], ...updatedData };
    users[index] = updatedUser;
    saveUsersToStorage(users);

    const session = authService.getCurrentSession();
    if (session && session.user.id === userId) {
      session.user = updatedUser;
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    }

    return updatedUser;
  },

  getUsers: () => {
    return getUsersFromStorage();
  }
};
