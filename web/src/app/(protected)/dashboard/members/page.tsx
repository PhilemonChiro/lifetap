import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getMembers } from "@/actions/members";
import { memberStatuses } from "@/lib/constants";
import { PageHeader } from "@/components/page-header";
import { MembersTable } from "./members-table";
import { MemberFilters } from "./member-filters";

interface PageProps {
  searchParams: Promise<{
    status?: string;
    search?: string;
    page?: string;
  }>;
}

export default async function MembersPage({ searchParams }: PageProps) {
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
    status: params.status,
    search: params.search,
  };

  const { data: members, total } = await getMembers(filters, page, 20);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Members"
        description="Manage LifeTap members and their subscriptions"
      />

      <MemberFilters statuses={memberStatuses} currentFilters={filters} />

      <MembersTable members={members} total={total} page={page} pageSize={20} />
    </div>
  );
}
