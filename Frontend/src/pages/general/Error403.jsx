import React from "react";
import { Card } from "@/components/ui/card";
import { ShieldAlert } from "lucide-react";

export const Error403 = () => {
  return (
    <div className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-background to-muted/30">
      <Card className="w-full max-w-md border shadow-2xl bg-card text-center p-6 space-y-6">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 text-destructive shadow-inner">
          <ShieldAlert className="h-10 w-10 animate-pulse" />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            403 - Access Denied
          </h1>
          <p className="text-sm text-muted-foreground">
            You do not have the required municipal clearance or role privileges
            to view this administrative portal.
          </p>
        </div>

        <div className="p-3 rounded-lg bg-muted/60 border text-xs text-muted-foreground">
          If you are a City Commissioner or Field Officer, please verify that
          you are signed in with your official municipal credentials.
        </div>
      </Card>
    </div>
  );
};
