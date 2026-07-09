import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Camera } from "lucide-react";

export const PhotoViewerModal = ({
  isOpen,
  onClose,
  photoUrl,
  title = "Evidence Photo",
  description = "Submitted image evidence.",
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="sm:max-w-xl p-0 overflow-hidden bg-black/95 border-none">
        <DialogHeader className="p-4 bg-background border-b absolute top-0 w-full z-10 flex flex-row items-center justify-between">
          <div className="flex flex-col space-y-1">
            <DialogTitle className="flex items-center gap-2 text-foreground">
              <Camera className="w-5 h-5" /> {title}
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground">
              {description}
            </DialogDescription>
          </div>
        </DialogHeader>
        <div className="relative w-full h-[60vh] sm:h-[70vh] flex items-center justify-center pt-20 pb-4 px-4">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt="Evidence"
              className="max-w-full max-h-full object-contain rounded-md shadow-2xl ring-1 ring-white/10"
            />
          ) : (
            <div className="text-white/50 text-sm">No image available</div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
