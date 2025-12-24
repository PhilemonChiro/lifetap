"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";

export type ServiceType = "dispatch" | "ambulance" | "police" | "fire_brigade";

export interface ServiceSettings {
  enabled: boolean;
  phone_numbers: string[];
}

export interface EmergencySmsSettings {
  enabled: boolean;
  dispatch: ServiceSettings;
  ambulance: ServiceSettings;
  police: ServiceSettings;
  fire_brigade: ServiceSettings;
}

export async function getEmergencySmsSettings(): Promise<EmergencySmsSettings | null> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("notification_settings")
    .select("setting_value")
    .eq("setting_key", "emergency_sms_settings")
    .single();

  if (error) {
    console.error("Error fetching SMS settings:", error);
    return null;
  }

  return data?.setting_value as EmergencySmsSettings;
}

export async function updateEmergencySmsSettings(
  settings: EmergencySmsSettings
): Promise<{ success: boolean; error?: string }> {
  const supabase = await createClient();

  const { error } = await supabase
    .from("notification_settings")
    .update({
      setting_value: settings,
      updated_at: new Date().toISOString(),
    })
    .eq("setting_key", "emergency_sms_settings");

  if (error) {
    console.error("Error updating SMS settings:", error);
    return { success: false, error: error.message };
  }

  revalidatePath("/dashboard/settings");
  return { success: true };
}

export async function addServiceNumber(
  service: ServiceType,
  phoneNumber: string
): Promise<{ success: boolean; error?: string }> {
  const settings = await getEmergencySmsSettings();

  if (!settings) {
    return { success: false, error: "Failed to fetch current settings" };
  }

  // Validate phone number format
  const cleanNumber = phoneNumber.trim();
  if (!cleanNumber.startsWith("+") || cleanNumber.length < 10) {
    return { success: false, error: "Phone number must start with + and country code" };
  }

  // Check for duplicates
  if (settings[service].phone_numbers.includes(cleanNumber)) {
    return { success: false, error: "Phone number already exists" };
  }

  settings[service].phone_numbers.push(cleanNumber);
  return updateEmergencySmsSettings(settings);
}

export async function removeServiceNumber(
  service: ServiceType,
  phoneNumber: string
): Promise<{ success: boolean; error?: string }> {
  const settings = await getEmergencySmsSettings();

  if (!settings) {
    return { success: false, error: "Failed to fetch current settings" };
  }

  settings[service].phone_numbers = settings[service].phone_numbers.filter(
    (num) => num !== phoneNumber
  );

  return updateEmergencySmsSettings(settings);
}

export async function toggleServiceNotifications(
  service: ServiceType,
  enabled: boolean
): Promise<{ success: boolean; error?: string }> {
  const settings = await getEmergencySmsSettings();

  if (!settings) {
    return { success: false, error: "Failed to fetch current settings" };
  }

  settings[service].enabled = enabled;
  return updateEmergencySmsSettings(settings);
}

export async function toggleGlobalSmsNotifications(
  enabled: boolean
): Promise<{ success: boolean; error?: string }> {
  const settings = await getEmergencySmsSettings();

  if (!settings) {
    return { success: false, error: "Failed to fetch current settings" };
  }

  settings.enabled = enabled;
  return updateEmergencySmsSettings(settings);
}

export async function testSmsNotification(service: ServiceType): Promise<{
  success: boolean;
  error?: string;
}> {
  const settings = await getEmergencySmsSettings();

  if (!settings) {
    return { success: false, error: "Failed to fetch settings" };
  }

  const serviceSettings = settings[service];
  if (!serviceSettings || serviceSettings.phone_numbers.length === 0) {
    return { success: false, error: "No phone numbers configured for this service" };
  }

  const serviceNames: Record<ServiceType, string> = {
    dispatch: "Dispatch",
    ambulance: "Ambulance",
    police: "Police",
    fire_brigade: "Fire Brigade",
  };

  try {
    const response = await fetch(
      "https://api.sms-gate.app/3rdparty/v1/message",
      {
        method: "POST",
        headers: {
          Authorization: "Basic VE1BODNFOmljc3k2ZGdpbmZlZDNl",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          textMessage: {
            text: `🧪 TEST: LifeTap ${serviceNames[service]} SMS notification system is working correctly.`,
          },
          phoneNumbers: serviceSettings.phone_numbers,
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: `SMS API error: ${errorText}` };
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: `Failed to send test SMS: ${error}` };
  }
}
