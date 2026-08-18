import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { complaintService } from "@/services/complaintService";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PhotoViewerModal } from "@/components/common/PhotoViewerModal";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  MapPin,
  User,
  CheckCircle2,
  Clock,
  Camera,
  FileCheck,
  EyeOff,
} from "lucide-react";
import { toast } from "sonner";

export const TrackComplaint = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialToken = searchParams.get("token") || "";
  const [tokenInput, setTokenInput] = useState(initialToken);
  const [complaint, setComplaint] = useState(null);
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewingImage, setViewingImage] = useState(null);

  const fetchComplaint = async (tokenStr, updateUrl = true) => {
    if (!tokenStr || !tokenStr.trim()) return;
    const cleanToken = tokenStr.trim().toUpperCase();
    if (complaint && complaint.token?.toUpperCase() === cleanToken) return;
    setLoading(true);
    setError(null);
    try {
      const data = await complaintService.getComplaintByToken(cleanToken);

      const complaintData = data.complaint || data;
      const updatesData = data.updates || [];

      setComplaint({
        ...complaintData,
        token: complaintData.token,
        title: complaintData.title,
        description: complaintData.description,
        category: complaintData.category,
        submittedPhoto:
          complaintData.submitted_photo || complaintData.submittedPhoto,
        location: complaintData.location,
        status: complaintData.status,
        severity: complaintData.severity,
        resolutionPhoto:
          complaintData.resolution_photo || complaintData.resolutionPhoto,
        resolutionNote:
          complaintData.resolution_note || complaintData.resolutionNote,
        createdAt: complaintData.created_at || complaintData.createdAt,
        updatedAt: complaintData.updated_at || complaintData.updatedAt,
        resolvedAt: complaintData.resolved_at || complaintData.resolvedAt,
        closedAt: complaintData.closed_at || complaintData.closedAt,
        department: complaintData.category || complaintData.department,
      });
      setUpdates(
        updatesData.map((u) => ({
          ...u,
          oldStatus: u.old_status || u.oldStatus,
          newStatus: u.new_status || u.newStatus,
          createdAt: u.created_at || u.createdAt,
          note: u.note,
        })),
      );
      if (
        updateUrl &&
        searchParams.get("token")?.toUpperCase() !== cleanToken
      ) {
        setSearchParams({ token: cleanToken }, { replace: true });
      }
    } catch {
      setError(
        "No civic report found matching this 12-character tracking token. Please check the token code.",
      );
      setComplaint(null);
      setUpdates([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const tokenInUrl = searchParams.get("token") || "";
    if (
      tokenInUrl &&
      (!complaint ||
        complaint.token?.toUpperCase() !== tokenInUrl.toUpperCase())
    ) {
      fetchComplaint(tokenInUrl, false);
    }
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (tokenInput.trim()) {
      fetchComplaint(tokenInput.trim());
    } else {
      toast.error("Please enter a valid 12-character token code.");
    }
  };

  const handleCitizenResolutionResponse = async (accept) => {
    if (!complaint) return;
    const newStatus = accept ? "Closed" : "In Progress";
    const note = accept
      ? "Citizen verified and accepted the resolution photo proof. Case closed."
      : "Citizen rejected resolution proof and requested re-opening.";

    try {
      const updated = await complaintService.updateComplaintStatus(
        complaint.id,
        newStatus,
        note,
      );
      setComplaint({ ...updated });
      toast.success(
        accept
          ? "Resolution accepted! Thank you for your feedback."
          : "Case re-opened and flagged to department supervisor.",
      );
    } catch {
      toast.error("Failed to update status");
    }
  };

  return (
    <div className="flex-1 flex flex-col justify-center p-4 sm:p-6 lg:p-8 bg-gradient-to-b from-background via-background/90 to-muted/30 relative overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-primary/10 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-3xl mx-auto w-full space-y-8 my-auto">
        <div className="text-center space-y-3">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground max-w-2xl mx-auto leading-tight">
            Track Your <span className="text-primary">Civic Report</span>
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Enter your 12-character zero-knowledge tracking token to view
            real-time status, assigned department officers, and resolution photo
            proof.
          </p>
        </div>

        <Card className="border-2 shadow-2xl bg-card/90 backdrop-blur-md">
          <CardContent className="p-5 sm:p-6">
            <form
              onSubmit={handleSearch}
              className="flex flex-col sm:flex-row items-center gap-3"
            >
              <div className="relative w-full">
                <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Enter Token Code (e.g., CRA-8B2Z9X)"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  className="pl-11 h-12 font-mono uppercase text-base tracking-wider font-semibold"
                />
              </div>
              <Button
                type="submit"
                size="lg"
                className="w-full sm:w-auto h-12 px-8 font-bold shrink-0 shadow-lg"
              >
                {loading ? "Searching..." : "Track Status"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Dialog
        open={!!error}
        onOpenChange={(open) => {
          if (!open) setError(null);
        }}
      >
        <DialogContent className="sm:max-w-md border-2 border-destructive/30 shadow-2xl bg-card/95 backdrop-blur-xl p-6 text-center">
          <DialogHeader className="space-y-3">
            <DialogTitle className="text-xl font-bold text-foreground">
              Token Not Found
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground">
              {error}
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!complaint}
        onOpenChange={(open) => {
          if (!open && !viewingImage) {
            setComplaint(null);
            setUpdates([]);
            setSearchParams({});
          }
        }}
      >
        <DialogContent className="max-w-4xl border-2 border-primary/20 shadow-2xl bg-card/95 backdrop-blur-xl p-0 overflow-hidden">
          <div className="max-h-[85vh] overflow-y-auto p-6 flex flex-col gap-4">
            <DialogHeader className="border-b pb-4 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className="font-mono text-xs font-bold px-2.5 py-0.5 bg-primary/10 text-primary border-primary/30"
                  >
                    {complaint?.token}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    Submitted on{" "}
                    {complaint?.createdAt &&
                      new Date(complaint.createdAt).toLocaleDateString()}
                  </span>
                  <Badge variant="outline" className="w-fit ml-2">
                    {complaint?.department ||
                      complaint?.category ||
                      "Pending AI routing"}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge
                    status={complaint?.status}
                    className="text-xs py-0.5 px-2.5"
                  />
                </div>
              </div>
              <DialogTitle className="text-2xl font-extrabold text-foreground text-left leading-tight">
                {complaint?.title}
              </DialogTitle>
            </DialogHeader>

            <div className="flex flex-col gap-6 w-full pt-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full items-stretch">
                <div className="flex flex-col gap-4 h-full justify-between">
                  <div className="p-4 rounded-xl bg-muted/50 border text-xs space-y-2 flex-1">
                    <div className="flex items-start gap-2.5">
                      <MapPin className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-foreground block">
                          Landmark
                        </span>
                        <span className="text-muted-foreground leading-relaxed">
                          {complaint?.location}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2.5 pt-2 border-t">
                      <User className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-foreground block">
                          Assigned Officer
                        </span>
                        <span className="text-muted-foreground">
                          {complaint?.assignedOfficerName ||
                            complaint?.assignedOfficer ||
                            "Awaiting Department Assignment"}
                        </span>
                        <span className="block text-[11px] text-muted-foreground mt-0.5">
                          Dept: {complaint?.department}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1.5 flex-1 flex flex-col">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Description
                    </h4>
                    <p className="text-sm leading-relaxed text-foreground bg-muted/30 p-4 rounded-lg border flex-1">
                      {complaint?.description}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-4 h-full justify-between">
                  <Card className="flex-1 border shadow-sm bg-muted/20 flex flex-col justify-center p-5">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <div className="space-y-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                          <Camera className="w-4 h-4 text-primary" />
                          <span>Evidence Uploaded by Citizen</span>
                        </span>
                        <p className="text-xs text-muted-foreground">
                          Original hazard evidence submitted by reporter
                        </p>
                      </div>
                      {complaint?.submittedPhoto ? (
                        <Button
                          type="button"
                          size="lg"
                          className="w-full sm:w-auto h-12 px-8 font-bold shrink-0 shadow-lg"
                          onClick={() =>
                            setViewingImage({
                              url: complaint.submittedPhoto,
                              title: "Evidence by Citizen",
                            })
                          }
                        >
                          View
                        </Button>
                      ) : (
                        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                          <EyeOff className="w-4 h-4" />
                          <span>Not Uploaded</span>
                        </div>
                      )}
                    </div>
                  </Card>

                  <Card className="flex-1 border shadow-sm bg-muted/20 flex flex-col justify-center p-5">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                      <div className="space-y-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                          <FileCheck className="w-4 h-4 text-primary" />
                          <span>Evidence Uploaded by Field Officer</span>
                        </span>
                        <p className="text-xs text-muted-foreground">
                          Resolution verification proof submitted by field crew
                        </p>
                        {complaint?.resolutionNote && (
                          <p className="text-xs italic text-foreground/80 mt-1.5 border-l-2 border-primary/50 pl-2">
                            {complaint.resolutionNote}
                          </p>
                        )}
                      </div>
                      {complaint?.resolutionPhoto ? (
                        <Button
                          type="button"
                          size="lg"
                          className="w-full sm:w-auto h-12 px-8 font-bold shrink-0 shadow-lg"
                          onClick={() =>
                            setViewingImage({
                              url: complaint.resolutionPhoto,
                              title: "Evidence Uploaded by Field Officer",
                            })
                          }
                        >
                          View
                        </Button>
                      ) : (
                        <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-muted/60 border border-dashed text-muted-foreground font-semibold text-xs shrink-0">
                          <EyeOff className="w-4 h-4" />
                          <span>Not Uploaded</span>
                        </div>
                      )}
                    </div>
                  </Card>
                </div>
              </div>

              <div className="w-full space-y-6 pt-4 border-t">
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-primary" />
                    <span>Resolution Timeline</span>
                  </h4>

                  <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
                    {updates &&
                      updates.length > 0 &&
                      updates.map((item, idx) => {
                        const isLatest = idx === updates.length - 1;
                        return (
                          <div
                            key={idx}
                            className="relative flex items-start gap-3"
                          >
                            <div
                              className={`absolute -left-6 top-1 h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                                isLatest
                                  ? "bg-primary border-primary text-primary-foreground shadow-md scale-110"
                                  : "bg-muted border-primary/40 text-primary"
                              }`}
                            >
                              <CheckCircle2 className="w-3 h-3" />
                            </div>
                            <div className="flex-1 rounded-lg bg-muted/40 p-3 border text-xs space-y-1">
                              <div className="flex items-center justify-between font-semibold text-foreground">
                                <span>
                                  Status: {item.newStatus || item.new_status}
                                </span>
                                <span className="text-[11px] font-normal text-muted-foreground">
                                  {item.createdAt
                                    ? new Date(item.createdAt).toLocaleString()
                                    : ""}
                                </span>
                              </div>
                              {item.note ? (
                                <p className="text-muted-foreground mt-1">
                                  {item.note}
                                </p>
                              ) : null}
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>

                {complaint?.status === "Resolved" && (
                  <div className="pt-4 p-5 rounded-xl bg-primary/5 border border-primary/20 space-y-3">
                    <span className="font-bold text-foreground block text-center text-sm">
                      Are you satisfied with this resolution?
                    </span>
                    <p className="text-xs text-muted-foreground text-center max-w-md mx-auto">
                      Please review the resolution photo and summary note above.
                      Accepting will close this ticket.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto pt-1">
                      <Button
                        size="sm"
                        className="flex-1 font-bold h-10 shadow-md"
                        onClick={() => handleCitizenResolutionResponse(true)}
                      >
                        Accept & Close Ticket
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleCitizenResolutionResponse(false)}
                        className="flex-1 font-bold h-10 border-destructive/40 text-destructive hover:bg-destructive/10"
                      >
                        Reject & Re-open
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <PhotoViewerModal
            isOpen={!!viewingImage}
            onClose={() => setViewingImage(null)}
            photoUrl={viewingImage?.url}
            title={viewingImage?.title}
            description="Submitted image evidence."
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};
