import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Info, CheckCircle2 } from "lucide-react";

export const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  description = "Are you sure you want to proceed?",
  confirmText = "Confirm",
  cancelText = "Cancel",
  isLoading = false,
  variant = "default",
  icon: Icon,
}) => {
  let DefaultIcon = Info;
  let iconColorClass = "text-primary border-primary/20 bg-primary/10";
  let btnClass = "";

  if (variant === "destructive") {
    DefaultIcon = AlertTriangle;
    iconColorClass = "text-destructive border-destructive/20 bg-destructive/10";
  } else if (variant === "success") {
    DefaultIcon = CheckCircle2;
    iconColorClass = "text-emerald-500 border-emerald-500/20 bg-emerald-500/10";
    btnClass = "bg-emerald-600 hover:bg-emerald-700 text-white";
  }

  const DisplayIcon = Icon || DefaultIcon;

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(val) => !val && !isLoading && onClose()}
    >
      <DialogContent className="w-[90vw] sm:w-full max-w-md bg-card/95 border shadow-2xl rounded-2xl p-6 z-[60] text-foreground">
        <DialogHeader className="text-left">
          <DialogTitle className="flex items-center gap-2.5 text-lg font-bold tracking-tight text-foreground">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-xl shrink-0 shadow-sm border ${iconColorClass}`}
            >
              <DisplayIcon className="h-4 w-4" />
            </div>
            <span>{title}</span>
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground mt-2">
            {description}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-5 flex flex-col sm:flex-row justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={isLoading}
            className="rounded-xl font-semibold hover:bg-accent sm:w-auto w-full"
          >
            {cancelText}
          </Button>
          <Button
            variant={variant === "destructive" ? "destructive" : "default"}
            size="sm"
            onClick={onConfirm}
            disabled={isLoading}
            className={`rounded-xl font-semibold shadow-sm sm:w-auto w-full ${variant === "success" ? btnClass : ""}`}
          >
            {isLoading ? "Processing..." : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
