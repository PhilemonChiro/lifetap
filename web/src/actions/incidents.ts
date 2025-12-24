"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";

export interface Incident {
  id: string;
  incident_number: string;
  member_id: string | null;
  member_tier: string | null;
  emergency_type: string | null;
  patient_conscious: boolean | null;
  patient_breathing: boolean | null;
  victim_count: number | null;
  scene_description: string | null;
  activated_by_phone: string | null;
  activation_method: string | null;
  gps_latitude: number | null;
  gps_longitude: number | null;
  address_description: string | null;
  status: string;
  provider_id: string | null;
  ambulance_vehicle_id: string | null;
  paramedic_name: string | null;
  paramedic_phone: string | null;
  activated_at: string;
  dispatched_at: string | null;
  arrived_at: string | null;
  completed_at: string | null;
  destination_hospital: string | null;
  incident_notes: string | null;
  member: {
    first_name: string;
    last_name: string;
    phone_number: string;
  } | null;
}

export interface IncidentFilters {
  status?: string;
  emergency_type?: string;
  search?: string;
}

export async function getIncidents(
  filters: IncidentFilters = {},
  page = 1,
  limit = 20
): Promise<{ data: Incident[]; total: number }> {
  const supabase = await createClient();

  let query = supabase
    .from("incidents")
    .select(
      `
      *,
      member:members(first_name, last_name, phone_number)
    `,
      { count: "exact" }
    )
    .order("activated_at", { ascending: false });

  if (filters.status && filters.status !== "all") {
    query = query.eq("status", filters.status);
  }

  if (filters.emergency_type && filters.emergency_type !== "all") {
    query = query.eq("emergency_type", filters.emergency_type);
  }

  if (filters.search) {
    query = query.or(
      `incident_number.ilike.%${filters.search}%,activated_by_phone.ilike.%${filters.search}%`
    );
  }

  const offset = (page - 1) * limit;
  query = query.range(offset, offset + limit - 1);

  const { data, count, error } = await query;

  if (error) {
    console.error("Error fetching incidents:", error);
    return { data: [], total: 0 };
  }

  const incidents = (data || []).map((item) => ({
    ...item,
    member: Array.isArray(item.member) ? item.member[0] : item.member,
  }));

  return { data: incidents, total: count || 0 };
}

export async function getIncidentById(id: string): Promise<Incident | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("incidents")
    .select(
      `
      *,
      member:members(first_name, last_name, phone_number)
    `
    )
    .eq("id", id)
    .single();

  if (error) {
    console.error("Error fetching incident:", error);
    return null;
  }

  return {
    ...data,
    member: Array.isArray(data.member) ? data.member[0] : data.member,
  };
}

export async function updateIncidentStatus(
  id: string,
  status: string,
  notes?: string
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  const updateData: Record<string, unknown> = {
    status,
    updated_at: new Date().toISOString(),
  };

  // Set timestamp based on status
  if (status === "dispatched") {
    updateData.dispatched_at = new Date().toISOString();
  } else if (status === "arrived") {
    updateData.arrived_at = new Date().toISOString();
  } else if (status === "completed") {
    updateData.completed_at = new Date().toISOString();
    if (notes) updateData.completion_notes = notes;
  }

  if (notes && status !== "completed") {
    updateData.incident_notes = notes;
  }

  const { error } = await supabase.from("incidents").update(updateData).eq("id", id);

  if (error) {
    return { success: false, error: error.message };
  }

  revalidatePath("/dashboard/incidents");
  revalidatePath("/dashboard");
  return { success: true };
}

