import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export const StatsCard = ({
  title,
  value,
  icon: Icon,
  description,
  trend,
  trendUp = true,
  className,
}) => {
  return (
    <Card
      className={`overflow-hidden transition-all duration-200 hover:shadow-lg hover:border-primary/50 bg-card ${className || ""}`}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          {Icon && (
            <div className="p-2.5 rounded-xl border bg-primary/10 text-primary border-primary/20">
              <Icon className="w-5 h-5" />
            </div>
          )}
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <h3 className="text-3xl font-bold tracking-tight text-foreground">
            {value}
          </h3>
          {trend && (
            <span
              className={`inline-flex items-center gap-1 text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                trendUp
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                  : "bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30 shadow-sm"
              }`}
            >
              {trend.includes("%") ||
              trend.includes("faster") ||
              trend.includes("slower")
                ? trendUp
                  ? "↑"
                  : "↓"
                : trendUp
                  ? "✓"
                  : "!"}{" "}
              {trend}
            </span>
          )}
        </div>
        {description && (
          <p className="mt-2 text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
};
