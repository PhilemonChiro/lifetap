import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getIncidents } from "@/actions/incidents";
import { incidentStatuses, emergencyTypes } from "@/lib/constants";
import { PageHeader } from "@/components/page-header";
import { IncidentsTable } from "./incidents-table";
import { IncidentFilters } from "./incident-filters";

interface PageProps {
  searchParams: Promise<{
    status?: string;
    type?: string;
    search?: string;
    page?: string;
  }>;
}

export default async function IncidentsPage({ searchParams }: PageProps) {
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
    emergency_type: params.type,
    search: params.search,
  };

  const { data: incidents, total } = await getIncidents(filters, page, 20);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incidents"
        description="Manage and monitor all emergency incidents"
      />

      <IncidentFilters
        statuses={incidentStatuses}
        emergencyTypes={emergencyTypes}
        currentFilters={filters}
      />

      <IncidentsTable
        incidents={incidents}
        total={total}
        page={page}
        pageSize={20}
      />
    </div>
  );
}
