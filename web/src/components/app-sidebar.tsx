"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  ChevronUp,
  LogOut,
  User,
  LayoutDashboard,
  Users,
  Ambulance,
  AlertTriangle,
  MapPin,
  Settings,
  FileText,
  Phone,
  UserCircle,
  Building2,
  CreditCard,
  History,
  Bell,
  BarChart3,
  Shield,
} from "lucide-react";
import { type NavSection, type IconName } from "@/config/navigation";
import { type User as AppUser, roleLabels } from "@/lib/auth";
import { logout } from "@/actions/auth";

// Map icon names to actual Lucide components
const iconMap: Record<IconName, React.ComponentType<{ className?: string }>> = {
  "layout-dashboard": LayoutDashboard,
  "users": Users,
  "ambulance": Ambulance,
  "alert-triangle": AlertTriangle,
  "map-pin": MapPin,
  "settings": Settings,
  "file-text": FileText,
  "phone": Phone,
  "user-circle": UserCircle,
  "building-2": Building2,
  "credit-card": CreditCard,
  "history": History,
  "bell": Bell,
  "bar-chart-3": BarChart3,
  "shield": Shield,
};

interface AppSidebarProps {
  navigation: NavSection[];
  user: AppUser;
}

export function AppSidebar({ navigation, user }: AppSidebarProps) {
  const pathname = usePathname();

  const getInitials = (name: string | null) => {
    if (!name) return "U";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2 px-4 py-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-600 text-white font-bold">
            LT
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm">LifeTap</span>
            <span className="text-xs text-muted-foreground">
              {roleLabels[user.role]}
            </span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {navigation.map((section) => (
          <SidebarGroup key={section.title}>
            <SidebarGroupLabel>{section.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {section.items.map((item) => {
                  const isActive = pathname === item.url ||
                    (item.url !== "/" && pathname.startsWith(item.url));
                  const Icon = iconMap[item.icon];
                  return (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild isActive={isActive}>
                        <Link href={item.url}>
                          <Icon className="h-4 w-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton className="w-full">
                  <Avatar className="h-6 w-6">
                    <AvatarImage src={user.avatar_url || undefined} />
                    <AvatarFallback className="text-xs">
                      {getInitials(user.full_name)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="truncate">{user.full_name || user.email}</span>
                  <ChevronUp className="ml-auto h-4 w-4" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                side="top"
                className="w-[--radix-popper-anchor-width]"
              >
                <DropdownMenuItem asChild>
                  <Link href="/settings/profile" className="cursor-pointer">
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="cursor-pointer text-red-600"
                  onClick={() => logout()}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
