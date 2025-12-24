export type UserRole = "admin" | "dispatch" | "provider" | "member";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  full_name: string | null;
  avatar_url: string | null;
  created_at: string;
}

export const roleLabels: Record<UserRole, string> = {
  admin: "Administrator",
  dispatch: "Dispatch Operator",
  provider: "Service Provider",
  member: "Member",
};
