export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      cards: {
        Row: {
          activated_at: string | null
          card_number: string
          created_at: string | null
          deactivated_at: string | null
          delivery_address: string | null
          id: string
          issued_at: string | null
          issued_by_agent_id: string | null
          member_id: string
          nfc_uid: string | null
          qr_code_hash: string
          status: string | null
        }
        Insert: {
          activated_at?: string | null
          card_number: string
          created_at?: string | null
          deactivated_at?: string | null
          delivery_address?: string | null
          id?: string
          issued_at?: string | null
          issued_by_agent_id?: string | null
          member_id: string
          nfc_uid?: string | null
          qr_code_hash: string
          status?: string | null
        }
        Update: {
          activated_at?: string | null
          card_number?: string
          created_at?: string | null
          deactivated_at?: string | null
          delivery_address?: string | null
          id?: string
          issued_at?: string | null
          issued_by_agent_id?: string | null
          member_id?: string
          nfc_uid?: string | null
          qr_code_hash?: string
          status?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cards_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
        ]
      }
      emr_records: {
        Row: {
          allergies: Json | null
          blood_type: string | null
          chronic_conditions: Json | null
          created_at: string | null
          current_medications: Json | null
          data_completeness_score: number | null
          emergency_notes: string | null
          id: string
          last_updated_by: string | null
          member_id: string
          past_surgeries: Json | null
          primary_physician_name: string | null
          primary_physician_phone: string | null
          specialist_consultations: Json | null
          updated_at: string | null
        }
        Insert: {
          allergies?: Json | null
          blood_type?: string | null
          chronic_conditions?: Json | null
          created_at?: string | null
          current_medications?: Json | null
          data_completeness_score?: number | null
          emergency_notes?: string | null
          id?: string
          last_updated_by?: string | null
          member_id: string
          past_surgeries?: Json | null
          primary_physician_name?: string | null
          primary_physician_phone?: string | null
          specialist_consultations?: Json | null
          updated_at?: string | null
        }
        Update: {
          allergies?: Json | null
          blood_type?: string | null
          chronic_conditions?: Json | null
          created_at?: string | null
          current_medications?: Json | null
          data_completeness_score?: number | null
          emergency_notes?: string | null
          id?: string
          last_updated_by?: string | null
          member_id?: string
          past_surgeries?: Json | null
          primary_physician_name?: string | null
          primary_physician_phone?: string | null
          specialist_consultations?: Json | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "emr_records_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: true
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
        ]
      }
      incidents: {
        Row: {
          activated_at: string | null
          activated_by_phone: string | null
          activation_method: string | null
          address_description: string | null
          ambulance_vehicle_id: string | null
          arrived_at: string | null
          completed_at: string | null
          completion_notes: string | null
          created_at: string | null
          destination_address: string | null
          destination_hospital: string | null
          dispatched_at: string | null
          emergency_type: string | null
          gps_accuracy_meters: number | null
          gps_latitude: number | null
          gps_longitude: number | null
          id: string
          incident_notes: string | null
          incident_number: string
          initial_eta_minutes: number | null
          member_id: string | null
          member_tier: string | null
          paramedic_name: string | null
          paramedic_phone: string | null
          patient_breathing: boolean | null
          patient_conscious: boolean | null
          payment_token_id: string | null
          provider_acknowledged_at: string | null
          provider_id: string | null
          scene_description: string | null
          status: string
          transport_started_at: string | null
          updated_at: string | null
          verified_at: string | null
          victim_count: number | null
        }
        Insert: {
          activated_at?: string | null
          activated_by_phone?: string | null
          activation_method?: string | null
          address_description?: string | null
          ambulance_vehicle_id?: string | null
          arrived_at?: string | null
          completed_at?: string | null
          completion_notes?: string | null
          created_at?: string | null
          destination_address?: string | null
          destination_hospital?: string | null
          dispatched_at?: string | null
          emergency_type?: string | null
          gps_accuracy_meters?: number | null
          gps_latitude?: number | null
          gps_longitude?: number | null
          id?: string
          incident_notes?: string | null
          incident_number: string
          initial_eta_minutes?: number | null
          member_id?: string | null
          member_tier?: string | null
          paramedic_name?: string | null
          paramedic_phone?: string | null
          patient_breathing?: boolean | null
          patient_conscious?: boolean | null
          payment_token_id?: string | null
          provider_acknowledged_at?: string | null
          provider_id?: string | null
          scene_description?: string | null
          status?: string
          transport_started_at?: string | null
          updated_at?: string | null
          verified_at?: string | null
          victim_count?: number | null
        }
        Update: {
          activated_at?: string | null
          activated_by_phone?: string | null
          activation_method?: string | null
          address_description?: string | null
          ambulance_vehicle_id?: string | null
          arrived_at?: string | null
          completed_at?: string | null
          completion_notes?: string | null
          created_at?: string | null
          destination_address?: string | null
          destination_hospital?: string | null
          dispatched_at?: string | null
          emergency_type?: string | null
          gps_accuracy_meters?: number | null
          gps_latitude?: number | null
          gps_longitude?: number | null
          id?: string
          incident_notes?: string | null
          incident_number?: string
          initial_eta_minutes?: number | null
          member_id?: string | null
          member_tier?: string | null
          paramedic_name?: string | null
          paramedic_phone?: string | null
          patient_breathing?: boolean | null
          patient_conscious?: boolean | null
          payment_token_id?: string | null
          provider_acknowledged_at?: string | null
          provider_id?: string | null
          scene_description?: string | null
          status?: string
          transport_started_at?: string | null
          updated_at?: string | null
          verified_at?: string | null
          victim_count?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "incidents_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
        ]
      }
      members: {
        Row: {
          address_city: string | null
          address_line1: string | null
          address_province: string | null
          created_at: string | null
          date_of_birth: string | null
          email: string | null
          first_name: string
          gender: string | null
          id: string
          kyc_status: string | null
          language_preference: string | null
          last_name: string
          member_id: string
          national_id_hash: string | null
          phone_number: string
          phone_number_verified: boolean | null
          registration_agent_id: string | null
          registration_channel: string | null
          status: string | null
          updated_at: string | null
        }
        Insert: {
          address_city?: string | null
          address_line1?: string | null
          address_province?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          email?: string | null
          first_name: string
          gender?: string | null
          id?: string
          kyc_status?: string | null
          language_preference?: string | null
          last_name: string
          member_id: string
          national_id_hash?: string | null
          phone_number: string
          phone_number_verified?: boolean | null
          registration_agent_id?: string | null
          registration_channel?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          address_city?: string | null
          address_line1?: string | null
          address_province?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          email?: string | null
          first_name?: string
          gender?: string | null
          id?: string
          kyc_status?: string | null
          language_preference?: string | null
          last_name?: string
          member_id?: string
          national_id_hash?: string | null
          phone_number?: string
          phone_number_verified?: boolean | null
          registration_agent_id?: string | null
          registration_channel?: string | null
          status?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      next_of_kin: {
        Row: {
          created_at: string | null
          email: string | null
          full_name: string
          id: string
          is_primary: boolean | null
          member_id: string
          notification_preference: string | null
          phone_number: string
          relationship: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email?: string | null
          full_name: string
          id?: string
          is_primary?: boolean | null
          member_id: string
          notification_preference?: string | null
          phone_number: string
          relationship: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string | null
          full_name?: string
          id?: string
          is_primary?: boolean | null
          member_id?: string
          notification_preference?: string | null
          phone_number?: string
          relationship?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "next_of_kin_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
        ]
      }
      payment_tokens: {
        Row: {
          amount_claimed_cents: number | null
          claim_id: string | null
          created_at: string | null
          expires_at: string
          id: string
          incident_id: string | null
          issued_at: string | null
          max_coverage_cents: number
          member_id: string
          services_covered: Json
          status: string
          subscription_id: string
          tier_id: string | null
          token_code: string
          updated_at: string | null
          used_at: string | null
          verified_at: string | null
          verified_by_provider_id: string | null
        }
        Insert: {
          amount_claimed_cents?: number | null
          claim_id?: string | null
          created_at?: string | null
          expires_at: string
          id?: string
          incident_id?: string | null
          issued_at?: string | null
          max_coverage_cents: number
          member_id: string
          services_covered?: Json
          status?: string
          subscription_id: string
          tier_id?: string | null
          token_code: string
          updated_at?: string | null
          used_at?: string | null
          verified_at?: string | null
          verified_by_provider_id?: string | null
        }
        Update: {
          amount_claimed_cents?: number | null
          claim_id?: string | null
          created_at?: string | null
          expires_at?: string
          id?: string
          incident_id?: string | null
          issued_at?: string | null
          max_coverage_cents?: number
          member_id?: string
          services_covered?: Json
          status?: string
          subscription_id?: string
          tier_id?: string | null
          token_code?: string
          updated_at?: string | null
          used_at?: string | null
          verified_at?: string | null
          verified_by_provider_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "payment_tokens_incident_id_fkey"
            columns: ["incident_id"]
            isOneToOne: false
            referencedRelation: "incidents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payment_tokens_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payment_tokens_subscription_id_fkey"
            columns: ["subscription_id"]
            isOneToOne: false
            referencedRelation: "subscriptions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payment_tokens_tier_id_fkey"
            columns: ["tier_id"]
            isOneToOne: false
            referencedRelation: "tiers"
            referencedColumns: ["id"]
          },
        ]
      }
      subscriptions: {
        Row: {
          auto_renew: boolean | null
          created_at: string | null
          expires_at: string | null
          grace_period_ends_at: string | null
          id: string
          member_id: string
          payment_method_id: string | null
          started_at: string | null
          status: string
          tier_id: string
          updated_at: string | null
        }
        Insert: {
          auto_renew?: boolean | null
          created_at?: string | null
          expires_at?: string | null
          grace_period_ends_at?: string | null
          id?: string
          member_id: string
          payment_method_id?: string | null
          started_at?: string | null
          status?: string
          tier_id: string
          updated_at?: string | null
        }
        Update: {
          auto_renew?: boolean | null
          created_at?: string | null
          expires_at?: string | null
          grace_period_ends_at?: string | null
          id?: string
          member_id?: string
          payment_method_id?: string | null
          started_at?: string | null
          status?: string
          tier_id?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "subscriptions_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "subscriptions_tier_id_fkey"
            columns: ["tier_id"]
            isOneToOne: false
            referencedRelation: "tiers"
            referencedColumns: ["id"]
          },
        ]
      }
      tiers: {
        Row: {
          billing_period_days: number | null
          created_at: string | null
          currency: string | null
          description: string | null
          display_name: string
          features: Json | null
          id: string
          is_active: boolean | null
          max_coverage_cents: number
          name: string
          price_cents: number
          services_covered: Json
          sort_order: number | null
          updated_at: string | null
        }
        Insert: {
          billing_period_days?: number | null
          created_at?: string | null
          currency?: string | null
          description?: string | null
          display_name: string
          features?: Json | null
          id?: string
          is_active?: boolean | null
          max_coverage_cents: number
          name: string
          price_cents: number
          services_covered?: Json
          sort_order?: number | null
          updated_at?: string | null
        }
        Update: {
          billing_period_days?: number | null
          created_at?: string | null
          currency?: string | null
          description?: string | null
          display_name?: string
          features?: Json | null
          id?: string
          is_active?: boolean | null
          max_coverage_cents?: number
          name?: string
          price_cents?: number
          services_covered?: Json
          sort_order?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      transactions: {
        Row: {
          amount_cents: number
          created_at: string | null
          currency: string | null
          description: string | null
          external_ref: string | null
          failed_at: string | null
          id: string
          initiated_at: string | null
          member_id: string | null
          metadata: Json | null
          paid_at: string | null
          payment_method: string | null
          paynow_poll_url: string | null
          paynow_reference: string | null
          paynow_status: string | null
          phone_number: string | null
          status: string
          subscription_id: string | null
          transaction_ref: string
          transaction_type: string
          updated_at: string | null
        }
        Insert: {
          amount_cents: number
          created_at?: string | null
          currency?: string | null
          description?: string | null
          external_ref?: string | null
          failed_at?: string | null
          id?: string
          initiated_at?: string | null
          member_id?: string | null
          metadata?: Json | null
          paid_at?: string | null
          payment_method?: string | null
          paynow_poll_url?: string | null
          paynow_reference?: string | null
          paynow_status?: string | null
          phone_number?: string | null
          status?: string
          subscription_id?: string | null
          transaction_ref: string
          transaction_type: string
          updated_at?: string | null
        }
        Update: {
          amount_cents?: number
          created_at?: string | null
          currency?: string | null
          description?: string | null
          external_ref?: string | null
          failed_at?: string | null
          id?: string
          initiated_at?: string | null
          member_id?: string | null
          metadata?: Json | null
          paid_at?: string | null
          payment_method?: string | null
          paynow_poll_url?: string | null
          paynow_reference?: string | null
          paynow_status?: string | null
          phone_number?: string | null
          status?: string
          subscription_id?: string | null
          transaction_ref?: string
          transaction_type?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "transactions_member_id_fkey"
            columns: ["member_id"]
            isOneToOne: false
            referencedRelation: "members"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "transactions_subscription_id_fkey"
            columns: ["subscription_id"]
            isOneToOne: false
            referencedRelation: "subscriptions"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Functions: {
      generate_card_number: { Args: never; Returns: string }
      generate_member_id: { Args: never; Returns: string }
      generate_payment_token_code: { Args: never; Returns: string }
    }
    Enums: {}
  }
}

// Helper types
export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type InsertTables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Insert']
export type UpdateTables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Update']

// Convenience exports
export type Member = Tables<'members'>
export type Subscription = Tables<'subscriptions'>
export type Card = Tables<'cards'>
export type NextOfKin = Tables<'next_of_kin'>
export type EmrRecord = Tables<'emr_records'>
export type Incident = Tables<'incidents'>
export type Tier = Tables<'tiers'>
export type Transaction = Tables<'transactions'>
export type PaymentToken = Tables<'payment_tokens'>
