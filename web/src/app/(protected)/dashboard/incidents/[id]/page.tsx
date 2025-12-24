import { redirect, notFound } from "next/navigation";
import Link from "next/link";
import { getUser } from "@/actions/auth";
import { getIncidentById } from "@/actions/incidents";
import { incidentStatuses } from "@/lib/constants";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  MapPin,
  Phone,
  Clock,
  User,
  AlertTriangle,
  Ambulance,
} from "lucide-react";
import { IncidentStatusUpdate } from "./status-update";

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

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function IncidentDetailPage({ params }: PageProps) {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/member");
  }

  const { id } = await params;
  const incident = await getIncidentById(id);

  if (!incident) {
    notFound();
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleString("en-ZW", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/incidents">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <PageHeader
          title={`Incident ${incident.incident_number}`}
          description={`${incident.emergency_type || "Unknown type"} emergency`}
        >
          <Badge
            variant="secondary"
            className={`text-base px-3 py-1 ${statusColors[incident.status]}`}
          >
            {incident.status.replace("_", " ")}
          </Badge>
        </PageHeader>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                Incident Details
              </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Emergency Type</p>
                <p className="font-medium capitalize">
                  {incident.emergency_type || "Unknown"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Member Tier</p>
                <p className="font-medium capitalize">
                  {incident.member_tier || "Unknown"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Victim Count</p>
                <p className="font-medium">{incident.victim_count || 1}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Activation Method</p>
                <p className="font-medium capitalize">
                  {incident.activation_method || "Unknown"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Patient Conscious</p>
                <p className="font-medium">
                  {incident.patient_conscious === null
                    ? "Unknown"
                    : incident.patient_conscious
                    ? "Yes"
                    : "No"}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Patient Breathing</p>
                <p className="font-medium">
                  {incident.patient_breathing === null
                    ? "Unknown"
                    : incident.patient_breathing
                    ? "Yes"
                    : "No"}
                </p>
              </div>
              {incident.scene_description && (
                <div className="sm:col-span-2">
                  <p className="text-sm text-muted-foreground">Scene Description</p>
                  <p className="font-medium">{incident.scene_description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-blue-600" />
                Location
              </CardTitle>
            </CardHeader>
            <CardContent>
              {incident.gps_latitude && incident.gps_longitude ? (
                <div className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Coordinates</p>
                      <p className="font-mono">
                        {incident.gps_latitude.toFixed(6)},{" "}
                        {incident.gps_longitude.toFixed(6)}
                      </p>
                    </div>
                    {incident.address_description && (
                      <div>
                        <p className="text-sm text-muted-foreground">Address</p>
                        <p className="font-medium">
                          {incident.address_description}
                        </p>
                      </div>
                    )}
                  </div>
                  <a
                    href={`https://www.google.com/maps?q=${incident.gps_latitude},${incident.gps_longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block"
                  >
                    <Button variant="outline">
                      <MapPin className="mr-2 h-4 w-4" />
                      Open in Google Maps
                    </Button>
                  </a>
                </div>
              ) : (
                <p className="text-muted-foreground">No location data available</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-orange-600" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <TimelineItem
                  label="Activated"
                  time={formatDate(incident.activated_at)}
                  active
                />
                <TimelineItem
                  label="Dispatched"
                  time={formatDate(incident.dispatched_at)}
                  active={!!incident.dispatched_at}
                />
                <TimelineItem
                  label="Arrived on Scene"
                  time={formatDate(incident.arrived_at)}
                  active={!!incident.arrived_at}
                />
                <TimelineItem
                  label="Completed"
                  time={formatDate(incident.completed_at)}
                  active={!!incident.completed_at}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-green-600" />
                Member Info
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {incident.member ? (
                <>
                  <div>
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-medium">
                      {incident.member.first_name} {incident.member.last_name}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Phone</p>
                    <p className="font-medium flex items-center gap-2">
                      <Phone className="h-4 w-4" />
                      {incident.member.phone_number}
                    </p>
                  </div>
                </>
              ) : (
                <p className="text-muted-foreground">Member not found</p>
              )}
              {incident.activated_by_phone && (
                <div>
                  <p className="text-sm text-muted-foreground">Activated By</p>
                  <p className="font-medium">{incident.activated_by_phone}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {(incident.paramedic_name || incident.ambulance_vehicle_id) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Ambulance className="h-5 w-5 text-red-600" />
                  Response Unit
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {incident.ambulance_vehicle_id && (
                  <div>
                    <p className="text-sm text-muted-foreground">Vehicle ID</p>
                    <p className="font-medium">{incident.ambulance_vehicle_id}</p>
                  </div>
                )}
                {incident.paramedic_name && (
                  <div>
                    <p className="text-sm text-muted-foreground">Paramedic</p>
                    <p className="font-medium">{incident.paramedic_name}</p>
                  </div>
                )}
                {incident.paramedic_phone && (
                  <div>
                    <p className="text-sm text-muted-foreground">Paramedic Phone</p>
                    <p className="font-medium">{incident.paramedic_phone}</p>
                  </div>
                )}
                {incident.destination_hospital && (
                  <div>
                    <p className="text-sm text-muted-foreground">Destination</p>
                    <p className="font-medium">{incident.destination_hospital}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          <IncidentStatusUpdate
            incidentId={incident.id}
            currentStatus={incident.status}
            statuses={incidentStatuses}
          />
        </div>
      </div>
    </div>
  );
}

function TimelineItem({
  label,
  time,
  active,
}: {
  label: string;
  time: string;
  active: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`h-3 w-3 rounded-full ${
          active ? "bg-green-500" : "bg-gray-200"
        }`}
      />
      <div className="flex-1">
        <p className={`text-sm ${active ? "font-medium" : "text-muted-foreground"}`}>
          {label}
        </p>
      </div>
      <p className="text-sm text-muted-foreground">{time}</p>
    </div>
  );
}
