import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { PageHeader } from "@/components/page-header";

export default async function ProviderPage() {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "provider" && user.role !== "admin") {
    redirect("/member");
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Provider Portal"
        description="Manage your ambulance fleet and respond to emergencies"
      />
      <p className="text-muted-foreground">Provider portal coming soon.</p>
    </div>
  );
}
