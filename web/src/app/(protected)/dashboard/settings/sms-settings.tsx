"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  MessageSquare,
  Plus,
  Trash2,
  Send,
  Loader2,
  Ambulance,
  Shield,
  Flame,
  Phone,
} from "lucide-react";
import {
  type EmergencySmsSettings,
  type ServiceType,
  addServiceNumber,
  removeServiceNumber,
  toggleServiceNotifications,
  toggleGlobalSmsNotifications,
  testSmsNotification,
} from "@/actions/settings";

interface SmsSettingsCardProps {
  initialSettings: EmergencySmsSettings | null;
}

const SERVICE_CONFIG: Record<
  ServiceType,
  { label: string; icon: React.ReactNode; color: string }
> = {
  dispatch: {
    label: "Dispatch Center",
    icon: <Phone className="h-4 w-4" />,
    color: "text-blue-600",
  },
  ambulance: {
    label: "Ambulance",
    icon: <Ambulance className="h-4 w-4" />,
    color: "text-red-600",
  },
  police: {
    label: "Police",
    icon: <Shield className="h-4 w-4" />,
    color: "text-indigo-600",
  },
  fire_brigade: {
    label: "Fire Brigade",
    icon: <Flame className="h-4 w-4" />,
    color: "text-orange-600",
  },
};

const DEFAULT_SETTINGS: EmergencySmsSettings = {
  enabled: true,
  dispatch: { enabled: true, phone_numbers: [] },
  ambulance: { enabled: true, phone_numbers: [] },
  police: { enabled: true, phone_numbers: [] },
  fire_brigade: { enabled: true, phone_numbers: [] },
};

export function SmsSettingsCard({ initialSettings }: SmsSettingsCardProps) {
  const [settings, setSettings] = useState<EmergencySmsSettings>(
    initialSettings || DEFAULT_SETTINGS
  );
  const [newNumbers, setNewNumbers] = useState<Record<ServiceType, string>>({
    dispatch: "",
    ambulance: "",
    police: "",
    fire_brigade: "",
  });
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleAddNumber = async (service: ServiceType) => {
    const number = newNumbers[service];
    if (!number.trim()) return;

    setLoading(`add-${service}`);
    setMessage(null);

    const result = await addServiceNumber(service, number);

    if (result.success) {
      setSettings((prev) => ({
        ...prev,
        [service]: {
          ...prev[service],
          phone_numbers: [...prev[service].phone_numbers, number.trim()],
        },
      }));
      setNewNumbers((prev) => ({ ...prev, [service]: "" }));
      setMessage({ type: "success", text: "Phone number added" });
    } else {
      setMessage({ type: "error", text: result.error || "Failed to add number" });
    }

    setLoading(null);
  };

  const handleRemoveNumber = async (service: ServiceType, phone: string) => {
    setLoading(`remove-${service}-${phone}`);
    setMessage(null);

    const result = await removeServiceNumber(service, phone);

    if (result.success) {
      setSettings((prev) => ({
        ...prev,
        [service]: {
          ...prev[service],
          phone_numbers: prev[service].phone_numbers.filter((n) => n !== phone),
        },
      }));
      setMessage({ type: "success", text: "Phone number removed" });
    } else {
      setMessage({ type: "error", text: result.error || "Failed to remove number" });
    }

    setLoading(null);
  };

  const handleToggleService = async (service: ServiceType, enabled: boolean) => {
    setLoading(`toggle-${service}`);
    setMessage(null);

    const result = await toggleServiceNotifications(service, enabled);

    if (result.success) {
      setSettings((prev) => ({
        ...prev,
        [service]: { ...prev[service], enabled },
      }));
      setMessage({
        type: "success",
        text: `${SERVICE_CONFIG[service].label} notifications ${enabled ? "enabled" : "disabled"}`,
      });
    } else {
      setMessage({ type: "error", text: result.error || "Failed to update" });
    }

    setLoading(null);
  };

  const handleToggleGlobal = async (enabled: boolean) => {
    setLoading("toggle-global");
    setMessage(null);

    const result = await toggleGlobalSmsNotifications(enabled);

    if (result.success) {
      setSettings((prev) => ({ ...prev, enabled }));
      setMessage({
        type: "success",
        text: `SMS notifications ${enabled ? "enabled" : "disabled"}`,
      });
    } else {
      setMessage({ type: "error", text: result.error || "Failed to update" });
    }

    setLoading(null);
  };

  const handleTestSms = async (service: ServiceType) => {
    setLoading(`test-${service}`);
    setMessage(null);

    const result = await testSmsNotification(service);

    if (result.success) {
      setMessage({ type: "success", text: "Test SMS sent successfully!" });
    } else {
      setMessage({ type: "error", text: result.error || "Failed to send test SMS" });
    }

    setLoading(null);
  };

  const renderServiceSection = (service: ServiceType) => {
    const config = SERVICE_CONFIG[service];
    const serviceSettings = settings[service];

    return (
      <div key={service} className="border rounded-lg p-4 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className={config.color}>{config.icon}</span>
            <h4 className="font-medium">{config.label}</h4>
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor={`${service}-enabled`} className="text-sm text-muted-foreground">
              {serviceSettings.enabled ? "On" : "Off"}
            </Label>
            <Switch
              id={`${service}-enabled`}
              checked={serviceSettings.enabled}
              onCheckedChange={(checked) => handleToggleService(service, checked)}
              disabled={loading !== null || !settings.enabled}
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="+263776123456"
            value={newNumbers[service]}
            onChange={(e) =>
              setNewNumbers((prev) => ({ ...prev, [service]: e.target.value }))
            }
            onKeyDown={(e) => e.key === "Enter" && handleAddNumber(service)}
            disabled={loading !== null}
          />
          <Button
            size="sm"
            onClick={() => handleAddNumber(service)}
            disabled={loading !== null || !newNumbers[service].trim()}
          >
            {loading === `add-${service}` ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
          </Button>
        </div>

        {serviceSettings.phone_numbers.length > 0 ? (
          <div className="space-y-2">
            {serviceSettings.phone_numbers.map((phone) => (
              <div
                key={phone}
                className="flex items-center justify-between p-2 bg-muted rounded-md"
              >
                <span className="font-mono text-sm">{phone}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveNumber(service, phone)}
                  disabled={loading !== null}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 h-7 w-7 p-0"
                >
                  {loading === `remove-${service}-${phone}` ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Trash2 className="h-3 w-3" />
                  )}
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-muted-foreground italic">No numbers configured</p>
        )}

        {serviceSettings.phone_numbers.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTestSms(service)}
            disabled={loading !== null}
          >
            {loading === `test-${service}` ? (
              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            ) : (
              <Send className="h-3 w-3 mr-1" />
            )}
            Test
          </Button>
        )}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Emergency SMS Notifications
          </div>
          <div className="flex items-center gap-2">
            <Label htmlFor="sms-global-enabled" className="text-sm font-normal">
              {settings.enabled ? "Enabled" : "Disabled"}
            </Label>
            <Switch
              id="sms-global-enabled"
              checked={settings.enabled}
              onCheckedChange={handleToggleGlobal}
              disabled={loading !== null}
            />
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Configure phone numbers for each emergency service to receive SMS alerts when
          new incidents are created.
        </p>

        {message && (
          <div
            className={`p-3 rounded-md text-sm ${
              message.type === "success"
                ? "bg-green-50 text-green-700 border border-green-200"
                : "bg-red-50 text-red-700 border border-red-200"
            }`}
          >
            {message.text}
          </div>
        )}

        {!settings.enabled && (
          <div className="p-3 bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-md text-sm">
            SMS notifications are globally disabled. Enable them to configure services.
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          {(Object.keys(SERVICE_CONFIG) as ServiceType[]).map(renderServiceSection)}
        </div>

        <p className="text-xs text-muted-foreground">
          Enter phone numbers with country code (e.g., +263776123456). All configured
          numbers will receive SMS alerts for every new incident.
        </p>
      </CardContent>
    </Card>
  );
}
