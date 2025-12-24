"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";

export interface Member {
  id: string;
  member_id: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string | null;
  status: string;
  kyc_status: string;
  date_of_birth: string | null;
  address_city: string | null;
  address_province: string | null;
  registration_channel: string | null;
  created_at: string;
  subscription: {
    status: string;
    tier: {
      display_name: string;
    } | null;
    expires_at: string | null;
  } | null;
}

export interface MemberFilters {
  status?: string;
  search?: string;
}

export async function getMembers(
  filters: MemberFilters = {},
  page = 1,
  limit = 20
): Promise<{ data: Member[]; total: number }> {
  const supabase = await createClient();

  let query = supabase
    .from("members")
    .select(
      `
      *,
      subscription:subscriptions(
        status,
        expires_at,
        tier:tiers(display_name)
      )
    `,
      { count: "exact" }
    )
    .order("created_at", { ascending: false });

  if (filters.status && filters.status !== "all") {
    query = query.eq("status", filters.status);
  }

  if (filters.search) {
    query = query.or(
      `first_name.ilike.%${filters.search}%,last_name.ilike.%${filters.search}%,phone_number.ilike.%${filters.search}%,member_id.ilike.%${filters.search}%`
    );
  }

  const offset = (page - 1) * limit;
  query = query.range(offset, offset + limit - 1);

  const { data, count, error } = await query;

  if (error) {
    console.error("Error fetching members:", error);
    return { data: [], total: 0 };
  }

  const members = (data || []).map((item) => {
    const sub = Array.isArray(item.subscription)
      ? item.subscription[0]
      : item.subscription;
    return {
      ...item,
      subscription: sub
        ? {
            ...sub,
            tier: Array.isArray(sub.tier) ? sub.tier[0] : sub.tier,
          }
        : null,
    };
  });

  return { data: members, total: count || 0 };
}

export async function getMemberById(id: string): Promise<Member | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("members")
    .select(
      `
      *,
      subscription:subscriptions(
        status,
        expires_at,
        tier:tiers(display_name)
      )
    `
    )
    .eq("id", id)
    .single();

  if (error) {
    console.error("Error fetching member:", error);
    return null;
  }

  const sub = Array.isArray(data.subscription)
    ? data.subscription[0]
    : data.subscription;

  return {
    ...data,
    subscription: sub
      ? {
          ...sub,
          tier: Array.isArray(sub.tier) ? sub.tier[0] : sub.tier,
        }
      : null,
  };
}

export async function updateMemberStatus(
  id: string,
  status: string
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  const { error } = await supabase
    .from("members")
    .update({ status, updated_at: new Date().toISOString() })
    .eq("id", id);

  if (error) {
    return { success: false, error: error.message };
  }

  revalidatePath("/dashboard/members");
  return { success: true };
}

