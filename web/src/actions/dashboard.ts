"use server";

import { createClient } from "@/lib/supabase/server";

export interface DashboardStats {
  activeIncidents: number;
  totalMembers: number;
  totalProviders: number;
  incidentsToday: number;
  pendingIncidents: number;
  completedToday: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const supabase = await createClient();

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Get active incidents count
  const { count: activeIncidents } = await supabase
    .from("incidents")
    .select("*", { count: "exact", head: true })
    .in("status", ["activated", "location_received", "verified", "dispatching", "dispatched", "en_route", "arrived", "transporting"]);

  // Get pending incidents (not yet dispatched)
  const { count: pendingIncidents } = await supabase
    .from("incidents")
    .select("*", { count: "exact", head: true })
    .in("status", ["activated", "location_received", "verified"]);

  // Get incidents created today
  const { count: incidentsToday } = await supabase
    .from("incidents")
    .select("*", { count: "exact", head: true })
    .gte("created_at", today.toISOString());

  // Get completed incidents today
  const { count: completedToday } = await supabase
    .from("incidents")
    .select("*", { count: "exact", head: true })
    .eq("status", "completed")
    .gte("completed_at", today.toISOString());

  // Get total members
  const { count: totalMembers } = await supabase
    .from("members")
    .select("*", { count: "exact", head: true });

  // For providers, we'll count profiles with provider role for now
  // In production, you'd have a providers table
  const { count: totalProviders } = await supabase
    .from("profiles")
    .select("*", { count: "exact", head: true })
    .eq("role", "provider");

  return {
    activeIncidents: activeIncidents || 0,
    totalMembers: totalMembers || 0,
    totalProviders: totalProviders || 0,
    incidentsToday: incidentsToday || 0,
    pendingIncidents: pendingIncidents || 0,
    completedToday: completedToday || 0,
  };
}

export interface RecentIncident {
  id: string;
  incident_number: string;
  emergency_type: string | null;
  status: string;
  activated_at: string;
  address_description: string | null;
  member: {
    first_name: string;
    last_name: string;
  } | null;
}

export async function getRecentIncidents(limit = 10): Promise<RecentIncident[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("incidents")
    .select(`
      id,
      incident_number,
      emergency_type,
      status,
      activated_at,
      address_description,
      member:members(first_name, last_name)
    `)
    .order("activated_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Error fetching recent incidents:", error);
    return [];
  }

  return (data || []).map((item) => ({
    ...item,
    member: Array.isArray(item.member) ? item.member[0] : item.member,
  }));
}
