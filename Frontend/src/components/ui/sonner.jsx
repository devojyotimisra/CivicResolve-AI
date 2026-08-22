import { useTheme } from "@/context/ThemeContext";
import { Toaster as Sonner } from "sonner";

export const Toaster = ({ ...props }) => {
    const { theme = "light", resolvedTheme } = useTheme();

    return (
        <Sonner
            theme={resolvedTheme || theme}
            className="toaster group"
            position="top-right"
            richColors={true}
            closeButton={true}
            visibleToasts={6}
            expand={true}
            gap={8}
            duration={4000}
            toastOptions={{
                classNames: {
                    toast: "group toast group-[.toaster]:bg-card group-[.toaster]:text-card-foreground group-[.toaster]:border-2 group-[.toaster]:border-border/80 group-[.toaster]:shadow-[0_12px_30px_rgba(0,0,0,0.35)] group-[.toaster]:rounded-xl font-sans antialiased",
                    description: "group-[.toast]:text-muted-foreground font-normal text-xs mt-0.5",
                    actionButton:
                        "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground font-semibold rounded-md shadow-sm px-3 py-1.5 text-xs transition-colors hover:bg-primary/90",
                    cancelButton:
                        "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground font-semibold rounded-md px-3 py-1.5 text-xs transition-colors hover:bg-muted/80",
                    closeButton:
                        "group-[.toast]:!bg-background group-[.toast]:!text-foreground group-[.toast]:!border-border hover:group-[.toast]:!bg-muted transition-colors",
                },
            }}
            {...props}
        />
    );
};
