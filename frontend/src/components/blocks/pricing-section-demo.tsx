"use client"

import { Sparkles, Zap, ArrowDownToDot } from "lucide-react"
import { PricingSection } from "@/components/blocks/pricing-section"

const defaultTiers = [
  {
    name: "Starter Clinic",
    price: {
      monthly: 499,
      yearly: 4999,
    },
    description: "Perfect for single-doctor clinics getting started with automation.",
    icon: (
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-green-500/30 to-green-500/30 blur-2xl rounded-full" />
        <Zap className="w-7 h-7 relative z-10 text-green-500 animate-[float_3s_ease-in-out_infinite]" />
      </div>
    ),
    features: [
      {
        name: "Up to 500 Reminders/month",
        description: "Enough for a typical small practice",
        included: true,
      },
      {
        name: "AI Notepad Scanning",
        description: "Extract details from handwritten notes",
        included: true,
      },
      {
        name: "Standard WhatsApp Messages",
        description: "Send reminders from our shared number",
        included: true,
      },
      {
        name: "Custom Clinic Number",
        description: "Send from your own verified WhatsApp number",
        included: false,
      },
    ],
  },
  {
    name: "Professional",
    price: {
      monthly: 2500,
      yearly: 24999,
    },
    description: "Ideal for busy clinics wanting a professional brand presence.",
    highlight: true,
    badge: "Most Popular",
    icon: (
      <div className="relative">
        <ArrowDownToDot className="w-7 h-7 relative z-10" />
      </div>
    ),
    features: [
      {
        name: "Unlimited Reminders",
        description: "No cap on monthly WhatsApp messages",
        included: true,
      },
      {
        name: "Custom Clinic Number",
        description: "Send from your own verified WhatsApp number",
        included: true,
      },
      {
        name: "Two-way Communication",
        description: "Patients can reply to confirm or reschedule",
        included: true,
      },
      {
        name: "Priority Support",
        description: "24/7 priority email and chat support",
        included: true,
      },
    ],
  },
]

function PricingSectionDemo() {
  return <PricingSection tiers={defaultTiers} />
}

export { PricingSectionDemo }
