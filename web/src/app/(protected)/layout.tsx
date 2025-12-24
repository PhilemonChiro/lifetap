import { redirect } from "next/navigation";
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { getUser } from "@/actions/auth";
import { getNavigation } from "@/config/navigation";
import { Separator } from "@/components/ui/separator";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  // Debug: log user role
  console.log("Layout - User:", user.email, "Role:", user.role);

  const navigation = getNavigation(user.role);

  // Debug: log navigation sections
  console.log("Layout - Navigation sections:", navigation.map(n => n.title));

  return (
    <SidebarProvider>
      <AppSidebar navigation={navigation} user={user} />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
        </header>
        <main className="flex-1 p-4">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
