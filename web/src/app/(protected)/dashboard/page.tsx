import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getDashboardStats, getRecentIncidents } from "@/actions/dashboard";
import { PageHeader } from "@/components/page-header";
import { StatsCard } from "@/components/stats-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  Users,
  Ambulance,
  Activity,
  Clock,
  CheckCircle,
} from "lucide-react";
import Link from "next/link";

const statusColors: Record<string, string> = {
  activated: "bg-red-100 text-red-700",
  location_received: "bg-orange-100 text-orange-700",
  verified: "bg-yellow-100 text-yellow-700",
  dispatching: "bg-blue-100 text-blue-700",
  dispatched: "bg-blue-100 text-blue-700",
  en_route: "bg-purple-100 text-purple-700",
  arrived: "bg-indigo-100 text-indigo-700",
  transporting: "bg-cyan-100 text-cyan-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-gray-100 text-gray-700",
};

export default async function AdminDashboard() {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/member");
  }

  const [stats, recentIncidents] = await Promise.all([
    getDashboardStats(),
    getRecentIncidents(8),
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description={`Welcome back, ${user.full_name || user.email}`}
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatsCard
          title="Active Incidents"
          value={stats.activeIncidents}
          icon={AlertTriangle}
          variant={stats.activeIncidents > 0 ? "danger" : "default"}
          description="Currently being handled"
        />
        <StatsCard
          title="Pending Dispatch"
          value={stats.pendingIncidents}
          icon={Clock}
          variant={stats.pendingIncidents > 0 ? "warning" : "default"}
          description="Awaiting dispatch"
        />
        <StatsCard
          title="Incidents Today"
          value={stats.incidentsToday}
          icon={Activity}
          description="Total reported"
        />
        <StatsCard
          title="Completed Today"
          value={stats.completedToday}
          icon={CheckCircle}
          variant="success"
          description="Successfully resolved"
        />
        <StatsCard
          title="Total Members"
          value={stats.totalMembers}
          icon={Users}
          description="Registered members"
        />
        <StatsCard
          title="Providers"
          value={stats.totalProviders}
          icon={Ambulance}
          description="Active providers"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Incidents</CardTitle>
            <Link
              href="/dashboard/incidents"
              className="text-sm text-red-600 hover:underline"
            >
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {recentIncidents.length === 0 ? (
              <p className="text-muted-foreground text-sm py-4 text-center">
                No incidents recorded yet.
              </p>
            ) : (
              <div className="space-y-3">
                {recentIncidents.map((incident) => (
                  <div
                    key={incident.id}
                    className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-medium">
                          {incident.incident_number}
                        </span>
                        <Badge
                          variant="secondary"
                          className={statusColors[incident.status] || ""}
                        >
                          {incident.status.replace("_", " ")}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {incident.emergency_type || "Unknown"} •{" "}
                        {incident.member
                          ? `${incident.member.first_name} ${incident.member.last_name}`
                          : "Unknown member"}
                      </p>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      {new Date(incident.activated_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Link
              href="/dashboard/incidents"
              className="flex items-center gap-3 rounded-lg border p-3 hover:bg-accent transition-colors"
            >
              <div className="rounded-md bg-red-100 p-2">
                <AlertTriangle className="h-4 w-4 text-red-600" />
              </div>
              <div>
                <p className="font-medium">Manage Incidents</p>
                <p className="text-sm text-muted-foreground">
                  View and manage all emergency incidents
                </p>
              </div>
            </Link>
            <Link
              href="/dashboard/members"
              className="flex items-center gap-3 rounded-lg border p-3 hover:bg-accent transition-colors"
            >
              <div className="rounded-md bg-blue-100 p-2">
                <Users className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <p className="font-medium">Manage Members</p>
                <p className="text-sm text-muted-foreground">
                  View member profiles and subscriptions
                </p>
              </div>
            </Link>
            <Link
              href="/dashboard/providers"
              className="flex items-center gap-3 rounded-lg border p-3 hover:bg-accent transition-colors"
            >
              <div className="rounded-md bg-green-100 p-2">
                <Ambulance className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="font-medium">Manage Providers</p>
                <p className="text-sm text-muted-foreground">
                  View ambulance providers and fleet
                </p>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
