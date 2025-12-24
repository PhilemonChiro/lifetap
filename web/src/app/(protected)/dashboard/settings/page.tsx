import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getEmergencySmsSettings } from "@/actions/settings";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Settings, Shield, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SmsSettingsCard } from "./sms-settings";

export default async function SettingsPage() {
  const user = await getUser();

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/member");
  }

  const smsSettings = await getEmergencySmsSettings();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Configure system settings and preferences"
      />

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              General Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">System Name</p>
                <p className="text-sm text-muted-foreground">
                  The name displayed throughout the application
                </p>
              </div>
              <Button variant="outline">Edit</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Default Language</p>
                <p className="text-sm text-muted-foreground">
                  Primary language for the system
                </p>
              </div>
              <Button variant="outline">Edit</Button>
            </div>
          </CardContent>
        </Card>

        <SmsSettingsCard initialSettings={smsSettings} />

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Password Policy</p>
                <p className="text-sm text-muted-foreground">
                  Set minimum password requirements
                </p>
              </div>
              <Button variant="outline">Configure</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Session Timeout</p>
                <p className="text-sm text-muted-foreground">
                  Auto-logout after inactivity period
                </p>
              </div>
              <Button variant="outline">Configure</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Data Management
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Export Data</p>
                <p className="text-sm text-muted-foreground">
                  Export system data for reporting
                </p>
              </div>
              <Button variant="outline">Export</Button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Backup Settings</p>
                <p className="text-sm text-muted-foreground">
                  Configure automatic data backups
                </p>
              </div>
              <Button variant="outline">Configure</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
