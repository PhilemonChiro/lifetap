"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, X } from "lucide-react";
import { useState, useCallback } from "react";

interface IncidentFiltersProps {
  statuses: { value: string; label: string }[];
  emergencyTypes: { value: string; label: string }[];
  currentFilters: {
    status?: string;
    emergency_type?: string;
    search?: string;
  };
}

export function IncidentFilters({
  statuses,
  emergencyTypes,
  currentFilters,
}: IncidentFiltersProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(currentFilters.search || "");

  const updateFilter = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value && value !== "all") {
        params.set(key, value);
      } else {
        params.delete(key);
      }
      params.delete("page"); // Reset to page 1
      router.push(`?${params.toString()}`);
    },
    [router, searchParams]
  );

  const handleSearch = () => {
    updateFilter("search", search);
  };

  const clearFilters = () => {
    setSearch("");
    router.push("/dashboard/incidents");
  };

  const hasFilters =
    currentFilters.status ||
    currentFilters.emergency_type ||
    currentFilters.search;

  return (
    <div className="flex flex-wrap gap-4 items-end">
      <div className="flex-1 min-w-[200px] max-w-sm">
        <label className="text-sm font-medium mb-1.5 block">Search</label>
        <div className="flex gap-2">
          <Input
            placeholder="Incident # or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <Button variant="outline" size="icon" onClick={handleSearch}>
            <Search className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="w-[180px]">
        <label className="text-sm font-medium mb-1.5 block">Status</label>
        <Select
          value={currentFilters.status || "all"}
          onValueChange={(value) => updateFilter("status", value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {statuses.map((status) => (
              <SelectItem key={status.value} value={status.value}>
                {status.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="w-[180px]">
        <label className="text-sm font-medium mb-1.5 block">Type</label>
        <Select
          value={currentFilters.emergency_type || "all"}
          onValueChange={(value) => updateFilter("type", value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            {emergencyTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {hasFilters && (
        <Button variant="ghost" onClick={clearFilters} className="gap-1">
          <X className="h-4 w-4" />
          Clear
        </Button>
      )}
    </div>
  );
}
