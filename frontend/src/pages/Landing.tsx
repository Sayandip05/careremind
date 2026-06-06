import {
  ChevronDown,
  Clock,
  Leaf,
  Plus,
  Shapes,
  BellRing,
  Calendar,
  TrendingDown,
  Menu,
  X,
  ArrowRight,
  Check,
  Loader2,
  LayoutDashboard,
  Users,
  MessageSquare,
  Upload,
  Settings,
  BarChart3,
} from "lucide-react";
import { useState, useEffect } from "react";
import { PricingSectionDemo } from "@/components/blocks/pricing-section-demo";
import { FooterDemo } from "@/components/blocks/footer-demo";
import { QnASection } from "@/components/blocks/qna-section";
import { ImageSlider } from "@/components/blocks/image-slider";
import { AvatarDemo } from "@/components/ui/avatar-demo";

export default function Landing() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="bg-gradient-to-b from-[#e6ffe6] to-[#f0fff0] text-slate-900 font-display min-h-screen flex flex-col relative overflow-hidden transition-colors duration-300">
      {/* Abstract Background Shapes */}
      <div
        className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[500px] h-[500px] top-[10%] left-[-10%] -rotate-[15deg]"
        style={{
          background:
            "linear-gradient(135deg, rgba(74, 222, 128, 0.4) 0%, rgba(21, 128, 61, 0.3) 100%)",
        }}
      ></div>
      <div
        className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[600px] h-[300px] bottom-[20%] right-[-10%] rotate-[30deg]"
        style={{
          background:
            "linear-gradient(135deg, rgba(74, 222, 128, 0.3) 0%, rgba(21, 128, 61, 0.2) 100%)",
        }}
      ></div>
      <div
        className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[400px] h-[400px] top-[30%] left-[40%]"
        style={{
          background:
            "linear-gradient(135deg, rgba(21, 128, 61, 0.2) 0%, rgba(74, 222, 128, 0.1) 100%)",
        }}
      ></div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 w-full z-50 bg-[#e6ffe6]/80 backdrop-blur-md border-b border-[#22c55e]/10">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#1E5F3A] rounded-lg flex items-center justify-center text-white">
              <BellRing className="w-5 h-5" />
            </div>
            <span className="text-xl font-bold text-[#1E5F3A]">CareRemind</span>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            <a
              className="font-medium hover:text-green-700 transition-colors"
              href="#how-it-works"
            >
              How It Works
            </a>
            <a
              className="font-medium hover:text-green-700 transition-colors"
              href="#features"
            >
              Features
            </a>
            <a
              className="font-medium hover:text-green-700 transition-colors"
              href="#pricing"
            >
              Pricing
            </a>
            <a
              className="font-medium hover:text-green-700 transition-colors"
              href="#contact"
            >
              Contact
            </a>
          </nav>

          <div className="flex items-center gap-4">
            <a
              className="hidden md:inline-flex items-center justify-center px-6 py-2.5 bg-primary text-white font-medium rounded hover:bg-green-700 transition-colors"
              href="/login"
            >
              Start Free Trial
            </a>
            <button
              className="md:hidden p-2 text-[#1E5F3A] hover:bg-green-100 rounded-md transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
        {/* Mobile Nav */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-[#22c55e]/10 bg-[#e6ffe6]">
            <nav className="px-4 pt-2 pb-4 space-y-1">
              <a
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-[#1E5F3A] hover:bg-green-100"
                href="#how-it-works"
              >
                How It Works
              </a>
              <a
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-[#1E5F3A] hover:bg-green-100"
                href="#features"
              >
                Features
              </a>
              <a
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-[#1E5F3A] hover:bg-green-100"
                href="#pricing"
              >
                Pricing
              </a>
              <a
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-[#1E5F3A] hover:bg-green-100"
                href="#contact"
              >
                Contact
              </a>
              <a
                className="block px-3 py-2 mt-4 text-center rounded-md text-base font-medium bg-primary text-white hover:bg-green-700"
                href="/login"
              >
                Start Free Trial
              </a>
            </nav>
          </div>
        )}
      </header>

      {/* Main Hero Content */}
      <main className="flex-grow flex flex-col items-center justify-center pt-32 pb-16 px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <div className="max-w-4xl mx-auto mb-8">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-6 leading-tight text-black">
            Automate Patient Reminders
            <br />
            For Your Clinic
          </h1>
          <p className="text-lg md:text-xl text-black mb-10 max-w-2xl mx-auto">
            Just send a WhatsApp photo of your daily register. Our AI handles
            everything.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              className="w-full sm:w-auto px-8 py-3.5 bg-black text-white font-semibold rounded-full hover:bg-slate-800 transition-colors"
              href="/login"
            >
              Get 14 Days Free Trial
            </a>
            <a
              className="w-full sm:w-auto px-8 py-3.5 bg-white text-black border border-slate-200 font-semibold rounded-full hover:bg-slate-50 transition-colors shadow-sm"
              href="/login"
            >
              Book A Demo
            </a>
          </div>
          <div className="mt-5">
            <a
              href="/dashboard"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-[#1E5F3A] hover:underline underline-offset-4 transition-colors"
            >
              <LayoutDashboard className="w-4 h-4" />
              Preview the dashboard →
            </a>
          </div>

        </div>

        {/* Overlapping Cards Replacement -> Image Slider */}
        <div className="w-full max-w-7xl mx-auto mt-6 sm:mt-10 mb-8 sm:mb-16 px-4 sm:px-6 lg:px-8">
          <ImageSlider />
        </div>
      </main>

      {/* Trusted By Section */}
      <section className="w-full pb-8 pt-4 relative z-10 bg-transparent flex justify-center">
        <AvatarDemo />
      </section>

      {/* Problem Statement Section (Features) */}
      <section
        id="features"
        className="w-full py-16 relative z-10 bg-[#F4FFF4]"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4 text-black">
              Your Patients Are Forgetting Their Appointments
            </h2>
            <p className="text-lg text-black leading-relaxed">
              Manual follow-ups are inefficient and cost your clinic thousands
              in lost revenue every month.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8 pb-8">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mb-6">
                <Calendar className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                Missed follow-ups
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                Patients often miss critical post-care checkups simply because
                they forgot or lost their prescription slip.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-amber-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                Time wasted on manual calling
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                Your receptionists spend 2-3 hours daily making manual calls.
                That's time they could spend helping patients in-clinic.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-green-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                Revenue loss from no-shows
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                Every empty appointment slot is a loss. Reducing no-shows by
                even 20% can significantly boost your monthly profit.
              </p>
            </div>

            {/* Card 4 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center mb-6">
                <MessageSquare className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                WhatsApp self-booking
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                Patients book their next visit directly from the reminder chat.
                No app download, no login — just tap, pick a slot, and pay.
              </p>
            </div>

            {/* Card 5 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center mb-6">
                <svg
                  className="w-6 h-6 text-purple-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                Razorpay payment built-in
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                Online patients pay upfront via Razorpay and get a PDF bill
                instantly. No cash collection hassle at the clinic.
              </p>
            </div>

            {/* Card 6 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center mb-6">
                <svg
                  className="w-6 h-6 text-emerald-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">
                Midnight patient list PDF
              </h3>
              <p className="text-slate-600 leading-relaxed text-sm">
                At 12 AM, doctor receives an auto-generated PDF with tomorrow's
                full patient schedule — online first, walk-in slots marked.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works section */}
      <section
        id="how-it-works"
        className="w-full py-16 md:py-24 bg-white relative z-10"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 flex flex-col items-center gap-4">
            <span className="px-4 py-1.5 rounded-full border border-slate-200 bg-slate-50 text-sm font-medium text-slate-700 shadow-sm">
              How it works
            </span>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-black">
              6 Steps. Zero Manual Work.
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl text-center">
              From scanning your notepad to delivering a midnight patient list —
              everything runs on autopilot.
            </p>
          </div>

          <div className="relative mx-auto max-w-5xl mb-12 w-full">
            <img
              src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop"
              alt="Doctor typing on laptop"
              className="aspect-[4/3] sm:aspect-video md:aspect-[21/9] max-h-[500px] w-full rounded-2xl md:rounded-3xl object-cover shadow-2xl border border-white/10"
              referrerPolicy="no-referrer"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Step 1 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center mb-6">
                <Upload className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-[11px] font-bold tracking-wider text-green-600 uppercase mb-2">
                Step 1
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                Scan Your Notepad
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Take a photo of your daily patient register and send it to our
                WhatsApp bot. Works with handwritten notes too.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mb-6">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-[11px] font-bold tracking-wider text-blue-600 uppercase mb-2">
                Step 2
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                AI Extracts Details
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Our AI instantly extracts patient names, phone numbers, and
                appointment details — securely and accurately.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-teal-50 flex items-center justify-center mb-6">
                <MessageSquare className="w-5 h-5 text-teal-600" />
              </div>
              <div className="text-[11px] font-bold tracking-wider text-teal-600 uppercase mb-2">
                Step 3
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                Automated Reminders
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Patients receive timely, personalized WhatsApp reminders from
                your clinic's number. No manual calling needed.
              </p>
            </div>

            {/* Step 4 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center mb-6">
                <svg
                  className="w-5 h-5 text-purple-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="text-[11px] font-bold tracking-wider text-purple-600 uppercase mb-2">
                Step 4
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                Patient Self-Books
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                From the same reminder chat, patients tap to book their next
                slot and pay via Razorpay. No app download needed.
              </p>
            </div>

            {/* Step 5 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center mb-6">
                <Users className="w-5 h-5 text-amber-600" />
              </div>
              <div className="text-[11px] font-bold tracking-wider text-amber-600 uppercase mb-2">
                Step 5
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                Priority Queue Built
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Online-booked patients are automatically placed first in queue.
                Walk-in slots are reserved separately for the rest.
              </p>
            </div>

            {/* Step 6 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mb-6">
                <svg
                  className="w-5 h-5 text-slate-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div className="text-[11px] font-bold tracking-wider text-emerald-600 uppercase mb-2">
                Step 6
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">
                Midnight PDF Delivered
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                At 12 AM, doctor receives a ready-made patient list on WhatsApp
                — organized by priority. Hand it to your receptionist.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Two-Panel Cards Section */}
      <section className="w-full py-16 relative z-10 bg-[#f0fff0]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <div className="flex justify-center mb-4">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z"
                  fill="#1E5F3A"
                />
              </svg>
            </div>
            <h2 className="text-4xl md:text-5xl font-serif font-bold text-black mb-4">
              For you and your clinic
            </h2>
            <p className="text-lg text-black">
              A platform loved by solo doctors across India
            </p>
          </div>

          <div className="flex flex-col md:flex-row gap-6 items-start">
            {/* Left Card */}
            <div className="flex-1 w-full bg-[#1E5F3A] rounded-[24px] p-8 md:p-10 shadow-lg flex flex-col relative overflow-hidden text-white h-auto md:h-[760px]">
              <div className="flex justify-between items-start mb-8">
                <span className="bg-[#22c55e] text-white text-[11px] font-bold px-3 py-1.5 rounded-full tracking-wider uppercase">
                  FOR DOCTORS
                </span>
                <button className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition-colors shrink-0">
                  <ArrowRight className="w-5 h-5 text-white" />
                </button>
              </div>

              <h3 className="text-[32px] font-bold mt-2 mb-8 leading-[1.2] pr-4">
                CareRemind gives you complete visibility of all patient
                reminders
              </h3>

              <div className="w-full h-px bg-white/10 mb-8"></div>

              <ul className="space-y-5 mb-12 relative z-10">
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">
                    See total reminders sent, confirmed, and failed today
                  </span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">
                    Upload Excel or photo — AI processes everything
                    automatically
                  </span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">
                    One click to trigger reminders for any patient manually
                  </span>
                </li>
              </ul>

              {/* Laptop Mockup */}
              <div className="mt-8 md:mt-auto md:absolute md:bottom-0 md:left-12 md:right-[-20px] h-[280px] bg-white rounded-t-md shadow-2xl flex flex-col overflow-hidden text-slate-800">
                {/* Browser Chrome */}
                <div className="bg-[#F1F5F9] px-4 py-3 flex items-center gap-2 border-b border-slate-200">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56]"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F]"></div>
                  </div>
                  <div className="ml-4 flex-1 max-w-sm h-6 bg-white rounded-md border border-slate-200 flex items-center px-3">
                    <span className="text-[10px] text-slate-400">
                      careremind.com/dashboard
                    </span>
                  </div>
                </div>
                {/* App Interface */}
                <div className="flex-1 flex bg-white">
                  {/* Sidebar */}
                  <div className="w-[100px] sm:w-[140px] bg-[#0F172A] p-2 sm:p-3 flex flex-col gap-1">
                    <div className="flex items-center gap-2 mb-4 px-1 sm:px-2 text-white">
                      <div className="w-5 h-5 rounded bg-white/10 flex items-center justify-center shrink-0">
                        <BellRing className="w-3 h-3" />
                      </div>
                      <span className="text-[9px] sm:text-[10px] font-bold truncate">
                        CareRemind
                      </span>
                    </div>
                    <div className="h-7 w-full bg-white/10 rounded px-1 sm:px-2 flex items-center gap-2 text-white">
                      <LayoutDashboard className="w-3 h-3 shrink-0" />
                      <span className="text-[8px] sm:text-[9px] truncate">
                        Dashboard
                      </span>
                    </div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400">
                      <Users className="w-3 h-3 shrink-0" />
                      <span className="text-[8px] sm:text-[9px] truncate">
                        Patients
                      </span>
                    </div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400">
                      <MessageSquare className="w-3 h-3 shrink-0" />
                      <span className="text-[8px] sm:text-[9px] truncate">
                        Reminders
                      </span>
                    </div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400">
                      <Upload className="w-3 h-3 shrink-0" />
                      <span className="text-[8px] sm:text-[9px] truncate">
                        Upload
                      </span>
                    </div>
                    <div className="mt-auto h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400">
                      <Settings className="w-3 h-3 shrink-0" />
                      <span className="text-[8px] sm:text-[9px] truncate">
                        Settings
                      </span>
                    </div>
                  </div>
                  {/* Main Content */}
                  <div className="flex-1 p-5 bg-slate-50 overflow-hidden">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-xs font-bold text-slate-800">
                        Analytics Overview
                      </h4>
                    </div>

                    {/* 4 Stat Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">
                          Today's Reminders
                        </div>
                        <div className="text-xs sm:text-sm font-bold text-slate-800">
                          47{" "}
                          <span className="text-[7px] sm:text-[8px] font-normal text-slate-400">
                            Sent
                          </span>
                        </div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">
                          Confirmed
                        </div>
                        <div className="text-xs sm:text-sm font-bold text-emerald-600">
                          31
                        </div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">
                          Failed
                        </div>
                        <div className="text-xs sm:text-sm font-bold text-red-600">
                          3
                        </div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">
                          Pending
                        </div>
                        <div className="text-xs sm:text-sm font-bold text-amber-600">
                          13
                        </div>
                      </div>
                    </div>

                    {/* Bar Chart */}
                    <div className="bg-white p-3 rounded border border-slate-100 shadow-sm h-[100px] flex flex-col">
                      <div className="text-[9px] font-semibold text-slate-700 mb-2 flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" /> Reminders This Week
                      </div>
                      <div className="flex-1 flex items-end justify-between gap-2 px-2">
                        <div className="w-full bg-green-100 rounded-t h-[40%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Mon
                          </div>
                        </div>
                        <div className="w-full bg-green-100 rounded-t h-[60%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Tue
                          </div>
                        </div>
                        <div className="w-full bg-green-500 rounded-t h-[90%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-green-600 font-bold">
                            Wed
                          </div>
                        </div>
                        <div className="w-full bg-green-100 rounded-t h-[50%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Thu
                          </div>
                        </div>
                        <div className="w-full bg-green-100 rounded-t h-[70%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Fri
                          </div>
                        </div>
                        <div className="w-full bg-green-100 rounded-t h-[30%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Sat
                          </div>
                        </div>
                        <div className="w-full bg-green-100 rounded-t h-[20%] relative">
                          <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">
                            Sun
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Card */}
            <div className="flex-1 w-full bg-[#f0fff0] rounded-[24px] p-8 md:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 flex flex-col relative overflow-hidden text-[#1E5F3A] h-auto md:h-[760px]">
              <div className="flex justify-between items-start mb-8">
                <span className="bg-white text-[#1E5F3A] text-[11px] font-bold px-3 py-1.5 rounded-full tracking-wider uppercase shadow-sm">
                  YOUR AI ASSISTANT
                </span>
                <button className="w-10 h-10 bg-[#1E5F3A] rounded-full flex items-center justify-center hover:bg-[#15472B] transition-colors shrink-0">
                  <ArrowRight className="w-5 h-5 text-white" />
                </button>
              </div>

              <h3 className="text-[32px] font-bold mt-2 mb-8 leading-[1.2] pr-4">
                Ask your AI assistant anything about your clinic
              </h3>

              <div className="w-full h-px bg-slate-200 mb-8"></div>

              <ul className="space-y-5 mb-12 relative z-10">
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">
                    Ask how many reminders were sent this month
                  </span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">
                    Get instant patient confirmation rates
                  </span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">
                    Know which patients need a follow-up today
                  </span>
                </li>
              </ul>

              {/* Phone Mockup */}
              <div className="mt-8 md:mt-auto md:absolute md:bottom-[-100px] md:left-1/2 md:-translate-x-1/2 w-[85%] max-w-[280px] mx-auto">
                <div className="bg-black rounded-[32px] p-2 shadow-xl border-4 border-slate-800 relative">
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-5 bg-black rounded-b-xl z-10"></div>
                  <div className="bg-[#F8FAFC] h-[400px] rounded-[24px] overflow-hidden flex flex-col relative">
                    {/* Header */}
                    <div className="bg-white border-b border-slate-100 p-3 pt-6 flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                        <BellRing className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">
                          CareRemind AI
                        </div>
                        <div className="text-[9px] text-green-500">Online</div>
                      </div>
                    </div>
                    {/* Chat Area */}
                    <div className="p-3 flex flex-col gap-3 overflow-y-auto text-[10px] flex-1 pb-6">
                      <div className="bg-[#1E5F3A] text-white p-2.5 rounded-xl rounded-tr-sm max-w-[85%] shadow-sm self-end">
                        How many reminders did I send this month?
                      </div>
                      <div className="bg-white border border-slate-100 p-2.5 rounded-xl rounded-tl-sm max-w-[85%] shadow-sm self-start text-slate-800">
                        This month you sent 312 reminders.
                        <br />
                        248 patients confirmed ✅
                        <br />
                        18 failed ❌
                        <br />
                        46 still pending ⏳
                      </div>
                      <div className="bg-[#1E5F3A] text-white p-2.5 rounded-xl rounded-tr-sm max-w-[85%] shadow-sm self-end">
                        Who needs follow-up today?
                      </div>
                      <div className="bg-white border border-slate-100 p-2.5 rounded-xl rounded-tl-sm max-w-[85%] shadow-sm self-start text-slate-800">
                        3 patients have not confirmed yet:
                        <br />
                        Ram Sharma, Priya Das, Mohan Roy
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <div id="pricing">
        <PricingSectionDemo />
      </div>

      {/* QnA Section */}
      <div id="faq">
        <QnASection />
      </div>

      {/* Contact Section */}
      <section
        id="contact"
        className="w-full py-20 bg-[#F4FFF4] relative z-10 border-t border-slate-100"
      >
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 text-slate-900">
            Let's Talk About Your Clinic
          </h2>
          <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
            Ready to reduce no-shows and automate your reminders? Send us a
            message and we'll get back to you within 24 hours.
          </p>
          <form className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="text-left">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                  placeholder="John"
                />
              </div>
              <div className="text-left">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                  placeholder="Doe"
                />
              </div>
            </div>
            <div className="text-left mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                placeholder="john@clinic.com"
              />
            </div>
            <div className="text-left mb-8">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Message
              </label>
              <textarea
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                placeholder="How can we help you?"
              ></textarea>
            </div>
            <button
              type="button"
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-base font-semibold text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors"
            >
              Send Message
            </button>
          </form>
        </div>
      </section>

      {/* Footer Section */}
      <FooterDemo />
    </div>
  );
}
