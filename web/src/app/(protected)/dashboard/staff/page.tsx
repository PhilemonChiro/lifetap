import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getStaffUsers } from "@/actions/staff";
import { PageHeader } from "@/components/page-header";
import { StaffTable } from "./staff-table";
import { StaffFilters } from "./staff-filters";
import { InviteStaffDialog } from "./invite-staff-dialog";

interface PageProps {
  searchParams: Promise<{
    role?: string;
    search?: string;
    page?: string;
  }>;
}

const roles = [
  { value: "admin", label: "Administrator" },
  { value: "dispatch", label: "Dispatch Operator" },
  { value: "provider", label: "Provider" },
  { value: "member", label: "Member" },
];

export default async function StaffPage({ searchParams }: PageProps) {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/member");
  }

  const params = await searchParams;
  const page = parseInt(params.page || "1");
  const filters = {
    role: params.role,
    search: params.search,
  };

  const { data: staffUsers, total } = await getStaffUsers(filters, page, 20);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Staff Management"
        description="Manage system users and their roles"
      >
        <InviteStaffDialog roles={roles} />
      </PageHeader>

      <StaffFilters roles={roles} currentFilters={filters} />

      <StaffTable
        users={staffUsers}
        currentUserId={user.id}
        total={total}
        page={page}
        pageSize={20}
        roles={roles}
      />
    </div>
  );
}
