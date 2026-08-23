import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CitizenLoginTab } from "@/components/auth/CitizenLoginTab";
import { OfficerLoginTab } from "@/components/auth/OfficerLoginTab";
import { CommissionerLoginTab } from "@/components/auth/CommissionerLoginTab";
import { Building2 } from "lucide-react";

export const Login = () => {
    const location = useLocation();
    const [activeTab, setActiveTab] = useState("citizen");

    useEffect(() => {
        if (location.state?.defaultTab) {
            setActiveTab(location.state.defaultTab);
        }
    }, [location.state]);

    return (
        <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-gradient-to-b from-background to-muted/30">
            <div className="w-full max-w-md">
                <Card className="border-2 shadow-xl bg-card/90 backdrop-blur-md">
                    <CardHeader className="pb-4">
                        <CardTitle className="text-xl text-center">Sign In</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                            <TabsList className="grid w-full grid-cols-3 h-11 p-1 bg-muted rounded-lg">
                                <TabsTrigger
                                    value="citizen"
                                    className="text-xs font-semibold flex items-center gap-1.5"
                                >
                                    <span>Citizen</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="officer"
                                    className="text-xs font-semibold flex items-center gap-1.5"
                                >
                                    <span>Officer</span>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="commissioner"
                                    className="text-xs font-semibold flex items-center gap-1.5"
                                >
                                    <Building2 className="w-3.5 h-3.5" />
                                    <span>Commissioner</span>
                                </TabsTrigger>
                            </TabsList>

                            <TabsContent value="citizen">
                                <CitizenLoginTab />
                            </TabsContent>

                            <TabsContent value="officer">
                                <OfficerLoginTab />
                            </TabsContent>

                            <TabsContent value="commissioner">
                                <CommissionerLoginTab />
                            </TabsContent>
                        </Tabs>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};
