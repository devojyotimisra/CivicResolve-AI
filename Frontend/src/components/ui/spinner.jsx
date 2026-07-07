import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

function Spinner({ className, ...props }) {
  return (
    <Loader2
      className={cn("h-4 w-4 animate-spin text-primary", className)}
      {...props}
    />
  );
}

export { Spinner };
