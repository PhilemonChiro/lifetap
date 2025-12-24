"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { updateIncidentStatus } from "@/actions/incidents";
import { Settings } from "lucide-react";

interface IncidentStatusUpdateProps {
  incidentId: string;
  currentStatus: string;
  statuses: { value: string; label: string }[];
}

export function IncidentStatusUpdate({
  incidentId,
  currentStatus,
  statuses,
}: IncidentStatusUpdateProps) {
  const [status, setStatus] = useState(currentStatus);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpdate = async () => {
    if (status === currentStatus && !notes) return;

    setLoading(true);
    setError(null);

    const result = await updateIncidentStatus(incidentId, status, notes);

    if (result.error) {
      setError(result.error);
    } else {
      setNotes("");
    }

    setLoading(false);
  };

  const isTerminal = currentStatus === "completed" || currentStatus === "cancelled";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Update Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isTerminal ? (
          <p className="text-sm text-muted-foreground">
            This incident has been {currentStatus}. No further updates can be made.
          </p>
        ) : (
          <>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Status</label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statuses.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">Notes</label>
              <Textarea
                placeholder="Add notes about this update..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <Button
              onClick={handleUpdate}
              disabled={loading || (status === currentStatus && !notes)}
              className="w-full bg-red-600 hover:bg-red-700"
            >
              {loading ? "Updating..." : "Update Status"}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
