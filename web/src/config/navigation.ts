import { UserRole } from "@/lib/auth";

// Icon names that map to lucide-react icons
export type IconName =
  | "layout-dashboard"
  | "users"
  | "ambulance"
  | "alert-triangle"
  | "map-pin"
  | "settings"
  | "file-text"
  | "phone"
  | "user-circle"
  | "building-2"
  | "credit-card"
  | "history"
  | "bell"
  | "bar-chart-3"
  | "shield";

export interface NavItem {
  title: string;
  url: string;
  icon: IconName;
  badge?: string;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

// Admin navigation
const adminNav: NavSection[] = [
  {
    title: "Overview",
    items: [
      { title: "Dashboard", url: "/dashboard", icon: "layout-dashboard" },
      { title: "Analytics", url: "/dashboard/analytics", icon: "bar-chart-3" },
    ],
  },
  {
    title: "Emergency Management",
    items: [
      { title: "Active Incidents", url: "/dashboard/incidents", icon: "alert-triangle" },
      { title: "Dispatch Queue", url: "/dashboard/dispatch", icon: "phone" },
      { title: "Live Map", url: "/dashboard/map", icon: "map-pin" },
    ],
  },
  {
    title: "User Management",
    items: [
      { title: "Members", url: "/dashboard/members", icon: "users" },
      { title: "Providers", url: "/dashboard/providers", icon: "ambulance" },
      { title: "Staff", url: "/dashboard/staff", icon: "shield" },
    ],
  },
  {
    title: "System",
    items: [
      { title: "Reports", url: "/dashboard/reports", icon: "file-text" },
      { title: "Audit Logs", url: "/dashboard/audit", icon: "shield" },
      { title: "Settings", url: "/dashboard/settings", icon: "settings" },
    ],
  },
];

// Dispatch operator navigation
const dispatchNav: NavSection[] = [
  {
    title: "Dispatch Center",
    items: [
      { title: "Dashboard", url: "/dispatch", icon: "layout-dashboard" },
      { title: "Active Incidents", url: "/dispatch/incidents", icon: "alert-triangle" },
      { title: "Dispatch Queue", url: "/dispatch/queue", icon: "phone" },
      { title: "Live Map", url: "/dispatch/map", icon: "map-pin" },
    ],
  },
  {
    title: "Resources",
    items: [
      { title: "Available Units", url: "/dispatch/units", icon: "ambulance" },
      { title: "Notifications", url: "/dispatch/notifications", icon: "bell" },
    ],
  },
];

// Provider navigation
const providerNav: NavSection[] = [
  {
    title: "Provider Portal",
    items: [
      { title: "Dashboard", url: "/provider", icon: "layout-dashboard" },
      { title: "Active Jobs", url: "/provider/jobs", icon: "alert-triangle" },
      { title: "Job History", url: "/provider/history", icon: "history" },
    ],
  },
  {
    title: "Fleet",
    items: [
      { title: "Vehicles", url: "/provider/vehicles", icon: "ambulance" },
      { title: "Coverage Areas", url: "/provider/coverage", icon: "map-pin" },
    ],
  },
  {
    title: "Account",
    items: [
      { title: "Payments", url: "/provider/payments", icon: "credit-card" },
      { title: "Profile", url: "/provider/profile", icon: "user-circle" },
    ],
  },
];

// Member navigation
const memberNav: NavSection[] = [
  {
    title: "My Account",
    items: [
      { title: "Dashboard", url: "/member", icon: "layout-dashboard" },
      { title: "My Profile", url: "/member/profile", icon: "user-circle" },
      { title: "Emergency Contacts", url: "/member/contacts", icon: "phone" },
    ],
  },
  {
    title: "History",
    items: [
      { title: "Incident History", url: "/member/incidents", icon: "history" },
    ],
  },
  {
    title: "Subscription",
    items: [
      { title: "My Plan", url: "/member/subscription", icon: "credit-card" },
    ],
  },
];

// Get navigation based on user role
export function getNavigation(role: UserRole): NavSection[] {
  switch (role) {
    case "admin":
      return adminNav;
    case "dispatch":
      return dispatchNav;
    case "provider":
      return providerNav;
    case "member":
      return memberNav;
    default:
      return memberNav;
  }
}

// Get the base path for a role
export function getRoleBasePath(role: UserRole): string {
  switch (role) {
    case "admin":
      return "/dashboard";
    case "dispatch":
      return "/dispatch";
    case "provider":
      return "/provider";
    case "member":
      return "/member";
    default:
      return "/member";
  }
}
