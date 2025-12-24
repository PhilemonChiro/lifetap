import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Ambulance, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export default async function ProvidersPage() {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/member");
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Providers"
        description="Manage ambulance service providers"
      >
        <Button className="bg-red-600 hover:bg-red-700">
          <Plus className="mr-2 h-4 w-4" />
          Add Provider
        </Button>
      </PageHeader>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Ambulance className="h-5 w-5" />
            Ambulance Providers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="py-8 text-center">
            <Ambulance className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No Providers Yet</h3>
            <p className="text-muted-foreground text-sm max-w-md mx-auto">
              Ambulance service providers will be displayed here. Add your first
              provider to start managing your emergency response network.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
