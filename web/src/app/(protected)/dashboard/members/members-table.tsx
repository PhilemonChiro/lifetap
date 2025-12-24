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
import { ChevronLeft, ChevronRight, MoreHorizontal, Eye } from "lucide-react";
import { type Member } from "@/actions/members";
import Link from "next/link";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  active: "bg-green-100 text-green-700",
  suspended: "bg-red-100 text-red-700",
  lapsed: "bg-gray-100 text-gray-700",
};

const subscriptionStatusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  active: "bg-green-100 text-green-700",
  grace_period: "bg-orange-100 text-orange-700",
  restricted: "bg-red-100 text-red-700",
  expired: "bg-gray-100 text-gray-700",
  cancelled: "bg-gray-100 text-gray-700",
};

interface MembersTableProps {
  members: Member[];
  total: number;
  page: number;
  pageSize: number;
}

export function MembersTable({
  members,
  total,
  page,
  pageSize,
}: MembersTableProps) {
  const router = useRouter();
  const totalPages = Math.ceil(total / pageSize);

  const goToPage = (newPage: number) => {
    const params = new URLSearchParams(window.location.search);
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-ZW", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  if (members.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center">
        <p className="text-muted-foreground">No members found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Member</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Subscription</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Joined</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {members.map((member) => (
              <TableRow key={member.id}>
                <TableCell>
                  <div>
                    <p className="font-medium">
                      {member.first_name} {member.last_name}
                    </p>
                    <p className="text-sm text-muted-foreground font-mono">
                      {member.member_id}
                    </p>
                  </div>
                </TableCell>
                <TableCell>{member.phone_number}</TableCell>
                <TableCell>
                  <Badge
                    variant="secondary"
                    className={statusColors[member.status] || ""}
                  >
                    {member.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {member.subscription ? (
                    <div className="space-y-1">
                      <Badge
                        variant="secondary"
                        className={
                          subscriptionStatusColors[member.subscription.status] || ""
                        }
                      >
                        {member.subscription.status.replace("_", " ")}
                      </Badge>
                      <p className="text-xs text-muted-foreground">
                        {member.subscription.tier?.display_name || "No tier"}
                      </p>
                    </div>
                  ) : (
                    <span className="text-muted-foreground text-sm">
                      No subscription
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-sm">
                  {member.address_city || member.address_province
                    ? `${member.address_city || ""} ${member.address_province || ""}`.trim()
                    : "—"}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(member.created_at)}
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
                        <Link href={`/dashboard/members/${member.id}`}>
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
          {Math.min(page * pageSize, total)} of {total} members
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
