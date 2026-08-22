import { Card } from "@/components/ui/card";
import { FileQuestion } from "lucide-react";

export const Error404 = () => {
    return (
        <div className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-background to-muted/30">
            <Card className="w-full max-w-md border-2 border-border shadow-2xl bg-card/95 text-center p-6 space-y-6">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary shadow-inner">
                    <FileQuestion className="h-10 w-10" />
                </div>

                <div className="space-y-2">
                    <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
                        404 - Page Not Found
                    </h1>
                    <p className="text-sm text-muted-foreground">
                        The civic page or service portal you are looking for has been moved,
                        archived, or does not exist.
                    </p>
                </div>
            </Card>
        </div>
    );
};
