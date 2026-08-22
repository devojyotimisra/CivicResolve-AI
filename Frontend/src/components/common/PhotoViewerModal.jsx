import { useState, useEffect } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from "@/components/ui/dialog";
import { Camera, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export const PhotoViewerModal = ({
    isOpen,
    onClose,
    photos = [],
    initialIndex = 0,
    title = "Evidence Photo",
    description = "Submitted image evidence.",
}) => {
    const getFullUrl = (url) => {
        if (!url) return null;
        if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:"))
            return url;
        const baseUrl = import.meta.env.VITE_API_URL.replace(/\/api\/?$/, "");
        return url.startsWith("/") ? `${baseUrl}${url}` : `${baseUrl}/${url}`;
    };

    const validPhotos = [...new Set((photos || []).filter(Boolean))].map(getFullUrl);

    const [currentIndex, setCurrentIndex] = useState(initialIndex);

    useEffect(() => {
        if (isOpen) {
            setCurrentIndex(Math.min(initialIndex, validPhotos.length - 1 || 0));
        }
    }, [isOpen, initialIndex, validPhotos.length]);

    const handlePrevious = (e) => {
        e.stopPropagation();
        setCurrentIndex((prev) => (prev > 0 ? prev - 1 : validPhotos.length - 1));
    };

    const handleNext = (e) => {
        e.stopPropagation();
        setCurrentIndex((prev) => (prev < validPhotos.length - 1 ? prev + 1 : 0));
    };

    const currentPhotoUrl = validPhotos[currentIndex];

    if (!isOpen) return null;

    return (
        <Dialog open={isOpen} onOpenChange={(o) => !o && onClose()}>
            <DialogContent
                onOpenAutoFocus={(e) => e.preventDefault()}
                className="sm:max-w-3xl p-0 overflow-hidden bg-black/95 border-none"
            >
                <DialogHeader className="p-4 bg-background border-b absolute top-0 w-full z-10 flex flex-row items-center justify-between">
                    <div className="flex flex-col space-y-1">
                        <DialogTitle className="flex items-center gap-2 text-foreground">
                            <Camera className="w-5 h-5" /> {title}
                            {validPhotos.length > 1 && (
                                <span className="text-sm font-normal text-muted-foreground ml-2">
                                    ({currentIndex + 1} of {validPhotos.length})
                                </span>
                            )}
                        </DialogTitle>
                        <DialogDescription className="text-xs text-muted-foreground">
                            {description}
                        </DialogDescription>
                    </div>
                </DialogHeader>
                <div className="relative w-full h-[60vh] sm:h-[75vh] flex flex-col items-center justify-center pt-20 pb-4 px-4 group">
                    {currentPhotoUrl ? (
                        <img
                            src={currentPhotoUrl}
                            alt="Evidence"
                            className="max-w-full max-h-[85%] object-contain rounded-md shadow-2xl ring-1 ring-white/10 transition-transform duration-300"
                        />
                    ) : (
                        <div className="text-white/50 text-sm">No image available</div>
                    )}

                    {validPhotos.length > 1 && (
                        <>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 text-white hover:bg-black/70 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={handlePrevious}
                            >
                                <ChevronLeft className="w-6 h-6" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 text-white hover:bg-black/70 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={handleNext}
                            >
                                <ChevronRight className="w-6 h-6" />
                            </Button>
                        </>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
};
