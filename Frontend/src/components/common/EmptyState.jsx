import { Button } from "@/components/ui/button";
import { Inbox } from "lucide-react";

export const EmptyState = ({
    title = "No items found",
    description = "There are currently no records matching your criteria.",
    icon: Icon = Inbox,
    actionLabel,
    onAction,
    inCard = false,
    bordered = true,
    className,
}) => {
    const showBorder = bordered && !inCard;
    return (
        <div
            className={`flex flex-col items-center justify-center p-12 text-center ${
                showBorder
                    ? "rounded-xl border border-dashed border-border bg-card/30 my-6"
                    : "py-12"
            } ${className || ""}`}
        >
            <div className="p-4 rounded-full bg-muted/60 text-muted-foreground mb-4">
                <Icon className="w-10 h-10 stroke-1" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>
            <p className="text-sm text-muted-foreground max-w-md mb-6">{description}</p>
            {actionLabel && onAction && (
                <Button onClick={onAction} className="shadow-md">
                    {actionLabel}
                </Button>
            )}
        </div>
    );
};
