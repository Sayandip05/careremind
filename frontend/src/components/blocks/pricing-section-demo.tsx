"use client";

import { Sparkles, Zap, ArrowDownToDot } from "lucide-react";
import { PricingSection } from "@/components/blocks/pricing-section";

const defaultTiers = [
  {
    name: "Professional",
    price: {
      monthly: 1999,
      yearly: 19999,
    },
    description:
      "Ideal for busy clinics wanting a professional brand presence out of the box.",
    highlight: true,
    badge: "All-in-one",
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
      {
        name: "AI Notepad Scanning",
        description: "Extract details from handwritten notes",
        included: true,
      },
    ],
  },
];

function PricingSectionDemo() {
  return <PricingSection tiers={defaultTiers} />;
}

export { PricingSectionDemo };
