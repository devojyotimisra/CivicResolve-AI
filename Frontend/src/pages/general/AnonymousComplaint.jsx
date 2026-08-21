import React, { useState } from "react";
import { complaintService } from "@/services/complaintService";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { MapPin, Copy, Check, Upload, ShieldCheck } from "lucide-react";
import { ConfirmationModal } from "@/components/common/ConfirmationModal";
import { PhotoViewerModal } from "@/components/common/PhotoViewerModal";

export const AnonymousComplaint = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [photoPreview, setPhotoPreview] = useState("");
  const [photoFile, setPhotoFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submittedToken, setSubmittedToken] = useState(null);
  const [copied, setCopied] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [confirmSubmit, setConfirmSubmit] = useState(false);
  const [viewingImage, setViewingImage] = useState(null);

  const submitForm = (e) => {
    e.preventDefault();
    if (!title.trim() || !location.trim()) {
      toast.error("Title and location are required.");
      return;
    }

    if (!description.trim() && !photoFile) {
      toast.error(
        "Please provide either a detailed description or media evidence.",
      );
      return;
    }

    setConfirmSubmit(true);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const complaintData = {
        title: title.trim(),
        description: description.trim(),
        location: location.trim(),
        photoFile: photoFile,
      };

      const result =
        await complaintService.fileAnonymousComplaint(complaintData);

      const token = result.trackingToken;
      setSubmittedToken(token);
      setIsFormModalOpen(false);
      setConfirmSubmit(false);
      toast.success(
        "Civic report submitted successfully! AI is processing your report.",
      );
    } catch (err) {
      toast.error(err.message || "Failed to submit report");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (submittedToken) {
      navigator.clipboard.writeText(submittedToken);
      setCopied(true);
      toast.success("Tracking token copied to clipboard!");
      setTimeout(() => setCopied(false), 3000);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhotoFile(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveMedia = () => {
    setPhotoPreview("");
    setPhotoFile(null);
  };

  return (
    <div className="flex-1 flex flex-col justify-center p-4 sm:p-6 lg:p-8 bg-gradient-to-b from-background via-background/90 to-muted/30 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-primary/10 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-3xl mx-auto w-full space-y-8 my-auto">
        <div className="text-center space-y-3">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground max-w-2xl mx-auto leading-tight">
            Report a <span className="text-primary">Civic Hazard</span> Now
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Submit road hazards, overflowing waste, or broken street lights
            directly to municipal crews without revealing your identity.
          </p>
        </div>

        <Card className="border-2 shadow-2xl bg-card/90 backdrop-blur-md">
          <CardContent className="p-5 sm:p-6">
            <Button
              type="button"
              size="lg"
              onClick={() => setIsFormModalOpen(true)}
              className="w-full h-12 px-10 text-lg font-extrabold shadow-xl"
            >
              <span>File Anonymous Report Now</span>
            </Button>
          </CardContent>
        </Card>
      </div>

      <Dialog open={isFormModalOpen} onOpenChange={setIsFormModalOpen}>
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="max-w-3xl border-2 border-primary/20 shadow-2xl bg-card/95 backdrop-blur-xl p-0 overflow-hidden">
          <div className="max-h-[85vh] overflow-y-auto p-6 sm:p-8 flex flex-col gap-6">
            <DialogHeader className="border-b pb-4 space-y-2">
              <DialogTitle className="text-2xl font-extrabold text-foreground text-left leading-tight">
                Report Details
              </DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground text-left">
                Please provide location details and evidence to assist field
                officers.
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={submitForm} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title">
                  Issue Summary Title{" "}
                  <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="title"
                  placeholder="e.g., Severe Pothole on 2nd Avenue"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">
                  Landmark <span className="text-destructive">*</span>
                </Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="location"
                    placeholder="e.g., 2nd Avenue, Near Anna Nagar Tower Park, Chennai 600040"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="pl-9"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Detailed Description</Label>
                <Textarea
                  id="description"
                  rows={4}
                  placeholder="Describe the hazard, approximate dimensions, and how long it has been present..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="space-y-3">
                <Label>Media Evidence</Label>

                {!photoPreview ? (
                  <label
                    htmlFor="photo-upload"
                    className="flex flex-col items-center justify-center gap-2 p-6 border-2 border-dashed rounded-lg border-muted-foreground/25 hover:border-primary/50 bg-muted/20 hover:bg-muted/40 transition-colors cursor-pointer text-center"
                  >
                    <div className="p-3 rounded-full bg-background shadow-sm border">
                      <Upload className="w-6 h-6 text-muted-foreground" />
                    </div>
                    <div>
                      <span className="text-sm font-semibold text-foreground">
                        Click to upload evidence
                      </span>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        PNG, JPG, JPEG up to 10MB
                      </p>
                    </div>
                    <input
                      id="photo-upload"
                      type="file"
                      accept="image/png,image/jpeg,image/jpg"
                      className="hidden"
                      onChange={handleFileChange}
                    />
                  </label>
                ) : (
                  <div className="relative w-full max-h-56 overflow-hidden rounded-lg border bg-muted">
                    <div
                      className="w-full h-56 cursor-pointer group relative"
                      onClick={() =>
                        setViewingImage({
                          photos: [photoPreview],
                          initialIndex: 0,
                          title: "Uploaded Evidence Preview",
                        })
                      }
                    >
                      <img
                        src={photoPreview}
                        alt="Uploaded evidence preview"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-bold">
                        Click to View Full Image
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="destructive"
                      size="sm"
                      className="absolute top-2 right-2 text-xs h-7 px-3 shadow"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveMedia();
                      }}
                    >
                      Remove Media
                    </Button>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button
                  type="submit"
                  size="lg"
                  className="h-12 px-8 text-base font-bold shadow-lg"
                  disabled={loading}
                >
                  {loading ? "Submitting..." : "Submit Anonymous Report Now"}
                </Button>
              </div>
            </form>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!submittedToken}
        onOpenChange={(open) => {
          if (!open) {
            setSubmittedToken(null);
            setTitle("");
            setDescription("");
            setLocation("");
            setPhotoPreview("");
            setPhotoFile(null);
          }
        }}
      >
        <DialogContent onOpenAutoFocus={(e) => e.preventDefault()} className="sm:max-w-md border-2 border-primary/30 shadow-2xl bg-card/95 backdrop-blur-xl p-6 overflow-hidden">
          <DialogHeader className="text-center space-y-3 pt-2">
            <DialogTitle className="text-2xl font-extrabold tracking-tight text-foreground text-center">
              Tracking Token
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground leading-relaxed max-w-sm mx-auto text-center">
              Save this code immediately. It is your ONLY key to track
              resolution progress and verify resolution photo proof. AI is
              analyzing your report in the background.
            </DialogDescription>
          </DialogHeader>

          <div className="my-4 p-5 rounded-2xl bg-muted/80 border-2 border-dashed border-primary/50 flex flex-col items-center justify-center text-center space-y-3 relative overflow-hidden group">
            <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest">
              Your Unique Code
            </span>
            <div className="text-2xl sm:text-3xl font-mono font-black tracking-widest text-primary bg-background/90 px-4 py-2.5 rounded-xl shadow-md w-full border border-primary/20 select-all">
              {submittedToken}
            </div>
            <Button
              type="button"
              variant={copied ? "default" : "outline"}
              size="sm"
              onClick={handleCopy}
              className="w-full font-bold h-10 shadow-sm flex items-center justify-center gap-2 transition-all"
            >
              {copied ? (
                <Check className="w-4 h-4 text-primary-foreground" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
              <span>{copied ? "Copied to Clipboard!" : "Copy Token Code"}</span>
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmationModal
        isOpen={confirmSubmit}
        onClose={() => setConfirmSubmit(false)}
        onConfirm={handleSubmit}
        title="Submit Civic Report?"
        description="Are you sure you are ready to file this anonymous report? False reporting is subject to civic penalties."
        confirmText="File Report"
        isLoading={loading}
        icon={ShieldCheck}
      />

      <PhotoViewerModal
        isOpen={!!viewingImage}
        onClose={() => setViewingImage(null)}
        photos={viewingImage?.photos || []}
        initialIndex={viewingImage?.initialIndex || 0}
        title={viewingImage?.title}
        description="Submitted image evidence."
      />
    </div>
  );
};
