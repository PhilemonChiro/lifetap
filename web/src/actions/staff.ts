"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import { UserRole } from "@/lib/auth";

export interface StaffUser {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface StaffFilters {
  role?: string;
  search?: string;
}

export async function getStaffUsers(
  filters: StaffFilters = {},
  page = 1,
  limit = 20
): Promise<{ data: StaffUser[]; total: number }> {
  const supabase = await createClient();

  let query = supabase
    .from("profiles")
    .select("*", { count: "exact" })
    .order("created_at", { ascending: false });

  if (filters.role && filters.role !== "all") {
    query = query.eq("role", filters.role);
  }

  if (filters.search) {
    query = query.or(
      `email.ilike.%${filters.search}%,full_name.ilike.%${filters.search}%`
    );
  }

  const offset = (page - 1) * limit;
  query = query.range(offset, offset + limit - 1);

  const { data, count, error } = await query;

  if (error) {
    console.error("Error fetching staff users:", error);
    return { data: [], total: 0 };
  }

  return { data: data || [], total: count || 0 };
}

export async function updateUserRole(
  userId: string,
  role: UserRole
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  // Verify current user is admin
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return { success: false, error: "Not authenticated" };
  }

  const { data: currentUserProfile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();

  if (currentUserProfile?.role !== "admin") {
    return { success: false, error: "Only admins can change user roles" };
  }

  // Prevent admin from changing their own role
  if (userId === user.id) {
    return { success: false, error: "You cannot change your own role" };
  }

  const { error } = await supabase
    .from("profiles")
    .update({ role, updated_at: new Date().toISOString() })
    .eq("id", userId);

  if (error) {
    return { success: false, error: error.message };
  }

  revalidatePath("/dashboard/staff");
  return { success: true };
}

export async function deleteUser(
  userId: string
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  // Verify current user is admin
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return { success: false, error: "Not authenticated" };
  }

  const { data: currentUserProfile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();

  if (currentUserProfile?.role !== "admin") {
    return { success: false, error: "Only admins can delete users" };
  }

  // Prevent admin from deleting themselves
  if (userId === user.id) {
    return { success: false, error: "You cannot delete your own account" };
  }

  // Delete profile (auth.users deletion requires admin API)
  const { error } = await supabase
    .from("profiles")
    .delete()
    .eq("id", userId);

  if (error) {
    return { success: false, error: error.message };
  }

  revalidatePath("/dashboard/staff");
  return { success: true };
}

export async function inviteStaffUser(
  email: string,
  fullName: string,
  role: UserRole
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  // Verify current user is admin
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return { success: false, error: "Not authenticated" };
  }

  const { data: currentUserProfile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();

  if (currentUserProfile?.role !== "admin") {
    return { success: false, error: "Only admins can invite users" };
  }

  // Generate a temporary password
  const tempPassword = generateTempPassword();

  // Create user via Supabase Auth
  // Note: In production, you'd use the admin API or send an invite email
  const { data: newUser, error: signUpError } = await supabase.auth.signUp({
    email,
    password: tempPassword,
    options: {
      data: {
        full_name: fullName,
        role: role,
      },
    },
  });

  if (signUpError) {
    return { success: false, error: signUpError.message };
  }

  if (!newUser.user) {
    return { success: false, error: "Failed to create user" };
  }

  // Update the profile with the correct role (trigger sets default)
  const { error: updateError } = await supabase
    .from("profiles")
    .update({ role, full_name: fullName })
    .eq("id", newUser.user.id);

  if (updateError) {
    console.error("Error updating profile role:", updateError);
  }

  revalidatePath("/dashboard/staff");

  // Return success with temp password (in production, send via email)
  return {
    success: true,
    error: `User created. Temporary password: ${tempPassword}`
  };
}

function generateTempPassword(): string {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
  let password = "";
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}
