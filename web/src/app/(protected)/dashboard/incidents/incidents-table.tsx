"use client";

import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronLeft, ChevronRight, MoreHorizontal, Eye, MapPin } from "lucide-react";
import { type Incident } from "@/actions/incidents";
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

interface IncidentsTableProps {
  incidents: Incident[];
  total: number;
  page: number;
  pageSize: number;
}

export function IncidentsTable({
  incidents,
  total,
  page,
  pageSize,
}: IncidentsTableProps) {
  const router = useRouter();
  const totalPages = Math.ceil(total / pageSize);

  const goToPage = (newPage: number) => {
    const params = new URLSearchParams(window.location.search);
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-ZW", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (incidents.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center">
        <p className="text-muted-foreground">No incidents found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Incident #</TableHead>
              <TableHead>Member</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Activated</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {incidents.map((incident) => (
              <TableRow key={incident.id}>
                <TableCell className="font-mono font-medium">
                  {incident.incident_number}
                </TableCell>
                <TableCell>
                  {incident.member ? (
                    <div>
                      <p className="font-medium">
                        {incident.member.first_name} {incident.member.last_name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {incident.activated_by_phone || incident.member.phone_number}
                      </p>
                    </div>
                  ) : (
                    <span className="text-muted-foreground">
                      {incident.activated_by_phone || "Unknown"}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <span className="capitalize">
                    {incident.emergency_type || "Unknown"}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="secondary"
                    className={statusColors[incident.status] || ""}
                  >
                    {incident.status.replace("_", " ")}
                  </Badge>
                </TableCell>
                <TableCell className="max-w-[200px]">
                  {incident.gps_latitude && incident.gps_longitude ? (
                    <a
                      href={`https://www.google.com/maps?q=${incident.gps_latitude},${incident.gps_longitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:underline"
                    >
                      <MapPin className="h-3 w-3" />
                      <span className="truncate text-sm">
                        {incident.address_description ||
                          `${incident.gps_latitude.toFixed(4)}, ${incident.gps_longitude.toFixed(4)}`}
                      </span>
                    </a>
                  ) : (
                    <span className="text-muted-foreground text-sm">
                      No location
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(incident.activated_at)}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/dashboard/incidents/${incident.id}`}>
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </Link>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {(page - 1) * pageSize + 1} to{" "}
          {Math.min(page * pageSize, total)} of {total} incidents
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => goToPage(page - 1)}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="text-sm">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => goToPage(page + 1)}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
