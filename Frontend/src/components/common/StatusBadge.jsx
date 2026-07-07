import React from "react";

export const StatusBadge = ({ status, className = "" }) => {
  const getLabel = (st) => {
    switch (st?.toLowerCase()) {
      case "submitted":
        return "Submitted";
      case "assigned":
        return "Assigned";
      case "en route":
      case "en_route":
        return "En Route";
      case "on site":
      case "on_site":
        return "On Site";
      case "in progress":
      case "in_progress":
        return "In Progress";
      case "resolved":
        return "Resolved";
      case "closed":
        return "Closed";
      default:
        return status || "Unknown";
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md border bg-background text-xs font-medium text-foreground shadow-sm ${className}`}
    >
      <span className="text-muted-foreground font-normal">Status:</span>
      <strong className="font-semibold">{getLabel(status)}</strong>
    </span>
  );
};
