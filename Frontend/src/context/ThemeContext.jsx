import React, { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext({
  theme: "dark",
  setTheme: () => null,
});

export const ThemeProvider = ({
  children,
  defaultTheme = "light",
  storageKey = "civic-theme",
}) => {
  const [theme, setThemeState] = useState(() => {
    return localStorage.getItem(storageKey) || defaultTheme;
  });

  const getResolvedTheme = (t) => {
    if (t === "system") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return t;
  };

  const [resolvedTheme, setResolvedTheme] = useState(() =>
    getResolvedTheme(theme),
  );

  useEffect(() => {
    const res = getResolvedTheme(theme);
    setResolvedTheme(res);
    const root = window.document.documentElement;
    root.classList.remove("light", "dark", "system");
    root.classList.add(res);
    localStorage.setItem(storageKey, theme);
  }, [theme, storageKey]);

  const setTheme = (newTheme) => {
    setThemeState(newTheme);
  };

  const toggleTheme = () => {
    setThemeState((prev) => {
      const current = getResolvedTheme(prev);
      return current === "dark" ? "light" : "dark";
    });
  };

  return (
    <ThemeContext.Provider
      value={{ theme, resolvedTheme, setTheme, toggleTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
