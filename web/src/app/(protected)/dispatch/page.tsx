import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { PageHeader } from "@/components/page-header";

export default async function DispatchPage() {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "dispatch" && user.role !== "admin") {
    redirect("/member");
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dispatch Center"
        description="Manage emergency dispatch operations"
      />
      <p className="text-muted-foreground">Dispatch center coming soon.</p>
    </div>
  );
}
