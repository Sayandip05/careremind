import { ChevronDown, Clock, Leaf, Plus, Shapes, BellRing, Calendar, TrendingDown, Menu, ArrowRight, Check, Loader2, LayoutDashboard, Users, MessageSquare, Upload, Settings, BarChart3, Smartphone, CreditCard, FileText } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Hero45 } from '@/components/blocks/shadcnblocks-com-hero45';
import { PricingSectionDemo } from '@/components/blocks/pricing-section-demo';
import { FooterDemo } from '@/components/blocks/footer-demo';
import { QnASection } from '@/components/blocks/qna-section';

export default function Landing() {
  return (
    <div className="bg-gradient-to-b from-[#e6ffe6] to-[#f0fff0] text-slate-900 font-display min-h-screen flex flex-col relative overflow-hidden transition-colors duration-300">
      {/* Abstract Background Shapes */}
      <div className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[500px] h-[500px] top-[10%] left-[-10%] -rotate-[15deg]" style={{ background: 'linear-gradient(135deg, rgba(74, 222, 128, 0.4) 0%, rgba(21, 128, 61, 0.3) 100%)' }}></div>
      <div className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[600px] h-[300px] bottom-[20%] right-[-10%] rotate-[30deg]" style={{ background: 'linear-gradient(135deg, rgba(74, 222, 128, 0.3) 0%, rgba(21, 128, 61, 0.2) 100%)' }}></div>
      <div className="absolute z-0 pointer-events-none rounded-full blur-[60px] w-[400px] h-[400px] top-[30%] left-[40%]" style={{ background: 'linear-gradient(135deg, rgba(21, 128, 61, 0.2) 0%, rgba(74, 222, 128, 0.1) 100%)' }}></div>

      {/* Header */}
      <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between relative z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#1E5F3A] rounded-lg flex items-center justify-center text-white">
            <BellRing className="w-5 h-5" />
          </div>
          <span className="text-xl font-bold text-[#1E5F3A]">CareRemind</span>
        </div>
        
        <nav className="hidden md:flex items-center gap-8">
          <a className="font-medium hover:text-primary transition-colors" href="#how-it-works">How It Works</a>
          <a className="font-medium hover:text-primary transition-colors" href="#features">Features</a>
          <a className="font-medium hover:text-primary transition-colors" href="#pricing">Pricing</a>
          <a className="font-medium hover:text-primary transition-colors" href="#faq">Contact</a>
        </nav>

        <div className="flex items-center gap-4">
          <a className="hidden md:inline-flex items-center justify-center px-6 py-2.5 bg-primary text-white font-medium rounded hover:bg-green-700 transition-colors" href="/login">
            Start Free Trial
          </a>
          <button className="md:hidden p-2 text-slate-600 hover:text-slate-900">
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Main Hero Content */}
      <main className="flex-grow flex flex-col items-center justify-center pt-12 pb-16 px-6 relative z-10 text-center">
        <div className="max-w-4xl mx-auto mb-8">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-6 leading-tight text-black">
            Automate Patient Reminders<br />For Your Clinic
          </h1>
          <p className="text-lg md:text-xl text-black mb-10 max-w-2xl mx-auto">
            Send a WhatsApp photo of your daily register. AI reminds your patients automatically — and patients can book their next slot right from the chat.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a className="w-full sm:w-auto px-8 py-3.5 bg-black text-white font-semibold rounded-full hover:bg-slate-800 transition-colors" href="/login">
              Get 14 Days Free Trial
            </a>
            <a className="w-full sm:w-auto px-8 py-3.5 bg-white text-black border border-slate-200 font-semibold rounded-full hover:bg-slate-50 transition-colors shadow-sm" href="/login">
              Book A Demo
            </a>
          </div>
        </div>

        {/* Overlapping Cards */}
        <div className="relative w-full max-w-4xl h-[320px] min-[400px]:h-[380px] sm:h-[500px] md:h-[600px] mt-4 sm:mt-8 mb-8 sm:mb-12 flex justify-center items-center mx-auto overflow-hidden sm:overflow-visible">
          <div className="relative w-[800px] h-[550px] transform scale-[0.4] min-[375px]:scale-[0.45] min-[400px]:scale-[0.5] sm:scale-[0.7] md:scale-100 origin-center">
            
            {/* Left Card - Notepad Scan */}
            <div className="absolute left-4 top-0 w-[400px] h-[440px] flex flex-col bg-[#2C2E33] text-white rounded-[32px] p-8 shadow-2xl transform -rotate-[8deg] hover:-rotate-4 transition-transform duration-300 z-20 border border-white/5 overflow-hidden">
            {/* Abstract background curves */}
            <div className="absolute inset-0 opacity-50 pointer-events-none overflow-hidden rounded-[32px]">
              <svg className="absolute w-[150%] h-[150%] -top-[20%] -left-[20%] stroke-black/40 fill-none stroke-[20]" viewBox="0 0 200 200">
                <path d="M 0,100 C 50,150 150,50 200,100" />
                <path d="M 0,150 C 80,200 120,0 200,50" />
              </svg>
            </div>

            <div className="relative z-10 flex flex-col h-full">
              <h3 className="font-medium text-[22px] mb-6">Notepad Scanned.</h3>
              
              <div className="flex flex-wrap items-center gap-4 mb-6">
                <span className="px-4 py-1.5 bg-[#10B981] text-sm font-medium rounded-full text-white">12 Patients</span>
                <span className="flex items-center gap-1.5 text-sm text-slate-300">
                  <Clock className="w-4 h-4" />
                  Today, 10:30 AM
                </span>
              </div>
              
              <div className="w-full h-px bg-white/10 mb-6"></div>
              
              <div className="space-y-6 flex-grow">
                <div className="flex items-center gap-3 text-sm text-slate-400 w-full pb-3 border-b border-white/10">
                  <span className="flex-1">Patient Name</span>
                  <span>Contact Number</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-base text-slate-200 font-medium">Rajesh Kumar</span>
                  <span className="text-sm text-slate-400">+91 98765 43210</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-base text-slate-200 font-medium">Priya Singh</span>
                  <span className="text-sm text-slate-400">+91 91234 56789</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-base text-slate-200 font-medium">Amit Sharma</span>
                  <span className="text-sm text-slate-400">+91 99887 76655</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-base text-slate-200 font-medium">Neha Gupta</span>
                  <span className="text-sm text-slate-400">+91 98765 12345</span>
                </div>
              </div>
            </div>
          </div>

            {/* Right Card - WhatsApp Action */}
            <div className="absolute right-4 bottom-0 w-[400px] h-[440px] flex flex-col bg-[#09090B] text-white rounded-[32px] p-8 shadow-2xl transform rotate-[8deg] hover:rotate-4 transition-transform duration-300 z-30 border border-white/5 overflow-hidden">
              {/* Abstract background curves */}
            <div className="absolute inset-0 opacity-40 pointer-events-none overflow-hidden rounded-[32px]">
              <svg className="absolute w-[200%] h-[200%] -top-[20%] -left-[50%] stroke-white/10 fill-none stroke-[6]" viewBox="0 0 200 200">
                <path d="M 100,-50 C 200,50 0,150 100,250" />
                <path d="M 150,-50 C 50,50 250,150 150,250" />
              </svg>
            </div>

            <div className="relative z-10 flex flex-col h-full">
              <h3 className="font-medium text-[22px] mb-8 leading-snug">Automated WhatsApp<br />Reminders Sent.</h3>
              
              {/* Chat Bubble */}
              <div className="bg-[#1E293B] rounded-2xl rounded-tr-sm p-4 mb-8 border border-white/10 relative">
                <p className="text-sm text-slate-200 leading-relaxed">
                  "Hello Rajesh, is your skin feeling better now? - Dr. Abhishek"
                </p>
                <div className="absolute -right-2 top-0 w-4 h-4 bg-[#1E293B] border-t border-r border-white/10 transform rotate-45"></div>
                <div className="mt-2 text-xs text-slate-400 text-right">10:35 AM <span className="text-[#3B82F6]">✓✓</span></div>
              </div>

              <div className="flex items-center mb-auto">
                <div className="flex-1">
                  <div className="text-[48px] font-light mb-1 leading-none text-[#10B981]">12</div>
                  <div className="text-sm text-slate-400">Reminders Sent</div>
                </div>
                <div className="w-px h-12 bg-white/10 mx-4"></div>
                <div className="flex-1 pl-4">
                  <div className="text-[48px] font-light mb-1 leading-none text-[#3B82F6]">8</div>
                  <div className="text-sm text-slate-400">Replies Received</div>
                </div>
              </div>

              <div className="mt-8">
                <div className="flex items-center justify-center text-sm text-slate-400 border border-white/10 rounded-full p-1.5 bg-white/5">
                  <div className="flex items-center gap-2 px-4 py-2">
                    <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></div>
                    <span className="text-white font-medium">WhatsApp API Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

      {/* Stats Strip */}
      <section className="w-full border-t border-slate-200/50 py-8 relative z-10 bg-transparent">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm text-slate-500 mb-8 font-medium">
            The problem is real. The market is massive.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-12 md:gap-24">
            <div className="text-center">
              <div className="text-4xl font-bold text-[#1E5F3A]">500K+</div>
              <div className="text-sm text-slate-500 mt-1">Small clinic doctors in India</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-[#1E5F3A]">40%</div>
              <div className="text-sm text-slate-500 mt-1">Patients forget follow-up visits</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-[#1E5F3A]">30sec</div>
              <div className="text-sm text-slate-500 mt-1">Daily work for the doctor</div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Statement Section */}
      <section id="features" className="w-full py-16 relative z-10 bg-[#F4FFF4]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-10">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4 text-black">
              Your Patients Are Forgetting Their Appointments
            </h2>
            <p className="text-lg text-black leading-relaxed">
              Manual follow-ups are inefficient and cost your clinic thousands in lost revenue every month.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8 pb-8">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mb-6">
                <Calendar className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">Missed follow-ups</h3>
              <p className="text-slate-600 leading-relaxed">
                Patients often miss critical post-care checkups simply because they forgot or lost their prescription slip.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-amber-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">Time wasted on manual calling</h3>
              <p className="text-slate-600 leading-relaxed">
                Your receptionists spend 2–3 hours daily making manual calls. That’s time they could spend helping patients in-clinic.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center mb-6">
                <TrendingDown className="w-6 h-6 text-green-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">Revenue loss from no-shows</h3>
              <p className="text-slate-600 leading-relaxed">
                Every empty appointment slot is a loss. Reducing no-shows by even 20% can significantly boost your monthly profit.
              </p>
            </div>

            {/* Card 4 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center mb-6">
                <Smartphone className="w-6 h-6 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">WhatsApp self-booking</h3>
              <p className="text-slate-600 leading-relaxed">
                Patients book their next visit directly from the reminder chat. No app download, no login — just tap, pick a slot, and pay.
              </p>
            </div>

            {/* Card 5 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center mb-6">
                <CreditCard className="w-6 h-6 text-purple-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">Razorpay payment built-in</h3>
              <p className="text-slate-600 leading-relaxed">
                Online patients pay upfront via Razorpay and get a PDF bill instantly. No cash collection hassle at the clinic.
              </p>
            </div>

            {/* Card 6 */}
            <div className="bg-white rounded-2xl p-8 border border-green-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center mb-6">
                <FileText className="w-6 h-6 text-emerald-500" />
              </div>
              <h3 className="text-xl font-semibold text-[#1E5F3A] mb-3">Midnight patient list PDF</h3>
              <p className="text-slate-600 leading-relaxed">
                At 12 AM, doctor receives an auto-generated PDF with tomorrow’s full patient schedule — online first, walk-in slots marked.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="w-full relative bg-white pt-16 pb-20 overflow-hidden">
        {/* Green Background Shapes for the bottom half */}
        <div className="absolute bottom-0 left-0 w-full h-[45%] md:h-[55%] bg-[#22c55e] z-0 overflow-hidden">
          {/* Light green shape on right */}
          <div className="absolute -top-[50%] -right-[20%] w-[70%] h-[200%] bg-[#4ade80] transform -rotate-[35deg]"></div>
          {/* Darker green shape on left */}
          <div className="absolute -bottom-[50%] -left-[20%] w-[60%] h-[200%] bg-[#16a34a] transform rotate-[35deg]"></div>
        </div>

        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-8">
            <h2 className="text-4xl md:text-5xl lg:text-[56px] font-bold text-black max-w-xl leading-[1.1] tracking-tight">
              Powerful feature to<br />elevate your business.
            </h2>
            <p className="text-lg text-slate-500 max-w-md leading-relaxed">
              Stay informed with real-time advanced analytics highlights the transformative advantage solutions.
            </p>
          </div>

          <div className="relative w-full aspect-video rounded-[32px] overflow-hidden shadow-2xl group cursor-pointer">
            <img 
              src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop" 
              alt="Video thumbnail showing working procedure" 
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors duration-300"></div>
            
            {/* Play Button */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[100px] h-[72px] bg-white rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
              <svg className="w-8 h-8 text-black ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      {/* How it works — 6 steps */}
      <section id="how-it-works" className="w-full py-16 md:py-24 relative z-10 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="inline-block bg-slate-100 text-slate-900 text-xs font-medium px-4 py-1.5 rounded-full mb-6 border border-slate-200">How it works</span>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4 text-black">
              6 Steps. Zero Manual Work.
            </h2>
            <p className="text-lg text-slate-500 leading-relaxed">
              From scanning your notepad to delivering a midnight patient list — everything runs on autopilot.
            </p>
          </div>

          {/* Hero Image */}
          <div className="relative w-full aspect-[16/7] rounded-[24px] overflow-hidden mb-14 shadow-lg">
            <img 
              src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop" 
              alt="Doctor scanning notepad" 
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center mb-6">
                <Upload className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 1</div>
              <h3 className="text-xl font-semibold text-black mb-3">Scan Your Notepad</h3>
              <p className="text-slate-600 leading-relaxed">
                Take a photo of your daily patient register and send it to our WhatsApp bot. Works with handwritten notes too.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center mb-6">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 2</div>
              <h3 className="text-xl font-semibold text-black mb-3">AI Extracts Details</h3>
              <p className="text-slate-600 leading-relaxed">
                Our AI instantly extracts patient names, phone numbers, and appointment details — securely and accurately.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center mb-6">
                <MessageSquare className="w-6 h-6 text-emerald-600" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 3</div>
              <h3 className="text-xl font-semibold text-black mb-3">Automated Reminders</h3>
              <p className="text-slate-600 leading-relaxed">
                Patients receive timely, personalized WhatsApp reminders from your clinic's number. No manual calling needed.
              </p>
            </div>

            {/* Step 4 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center mb-6">
                <Smartphone className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 4</div>
              <h3 className="text-xl font-semibold text-black mb-3">Patient Self-Books</h3>
              <p className="text-slate-600 leading-relaxed">
                From the same reminder chat, patients tap to book their next slot and pay via Razorpay. No app download needed.
              </p>
            </div>

            {/* Step 5 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center mb-6">
                <Users className="w-6 h-6 text-amber-600" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 5</div>
              <h3 className="text-xl font-semibold text-black mb-3">Priority Queue Built</h3>
              <p className="text-slate-600 leading-relaxed">
                Online-booked patients are automatically placed first in queue. Walk-in slots are reserved separately for the rest.
              </p>
            </div>

            {/* Step 6 */}
            <div className="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm">
              <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6">
                <FileText className="w-6 h-6 text-slate-700" />
              </div>
              <div className="text-xs font-bold text-[#16a34a] mb-2 tracking-wider uppercase">Step 6</div>
              <h3 className="text-xl font-semibold text-black mb-3">Midnight PDF Delivered</h3>
              <p className="text-slate-600 leading-relaxed">
                At 12 AM, doctor receives a ready-made patient list on WhatsApp — organized by priority. Hand it to your receptionist.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Two-Panel Cards Section */}
      <section className="w-full py-16 relative z-10 bg-[#f0fff0]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-10">
            <div className="flex justify-center mb-4">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z" fill="#1E5F3A"/>
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
                CareRemind gives you complete visibility of all patient reminders
              </h3>
              
              <div className="w-full h-px bg-white/10 mb-8"></div>
              
              <ul className="space-y-5 mb-12 relative z-10">
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">See total reminders sent, confirmed, and failed today</span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">Upload Excel or photo — AI processes everything automatically</span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-400 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-[#1E5F3A] stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-100 leading-snug font-medium">One click to trigger reminders for any patient manually</span>
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
                    <span className="text-[10px] text-slate-400">careremind.com/dashboard</span>
                  </div>
                </div>
                {/* App Interface */}
                <div className="flex-1 flex bg-white">
                  {/* Sidebar */}
                  <div className="w-[100px] sm:w-[140px] bg-[#0F172A] p-2 sm:p-3 flex flex-col gap-1">
                    <div className="flex items-center gap-2 mb-4 px-1 sm:px-2 text-white">
                      <div className="w-5 h-5 rounded bg-white/10 flex items-center justify-center shrink-0"><BellRing className="w-3 h-3" /></div>
                      <span className="text-[9px] sm:text-[10px] font-bold truncate">CareRemind</span>
                    </div>
                    <div className="h-7 w-full bg-white/10 rounded px-1 sm:px-2 flex items-center gap-2 text-white"><LayoutDashboard className="w-3 h-3 shrink-0" /><span className="text-[8px] sm:text-[9px] truncate">Dashboard</span></div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400"><Users className="w-3 h-3 shrink-0" /><span className="text-[8px] sm:text-[9px] truncate">Patients</span></div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400"><MessageSquare className="w-3 h-3 shrink-0" /><span className="text-[8px] sm:text-[9px] truncate">Reminders</span></div>
                    <div className="h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400"><Upload className="w-3 h-3 shrink-0" /><span className="text-[8px] sm:text-[9px] truncate">Upload</span></div>
                    <div className="mt-auto h-7 w-full hover:bg-white/5 rounded px-1 sm:px-2 flex items-center gap-2 text-slate-400"><Settings className="w-3 h-3 shrink-0" /><span className="text-[8px] sm:text-[9px] truncate">Settings</span></div>
                  </div>
                  {/* Main Content */}
                  <div className="flex-1 p-5 bg-slate-50 overflow-hidden">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-xs font-bold text-slate-800">Analytics Overview</h4>
                    </div>
                    
                    {/* 4 Stat Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">Today's Reminders</div>
                        <div className="text-xs sm:text-sm font-bold text-slate-800">47 <span className="text-[7px] sm:text-[8px] font-normal text-slate-400">Sent</span></div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">Confirmed</div>
                        <div className="text-xs sm:text-sm font-bold text-emerald-600">31</div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">Failed</div>
                        <div className="text-xs sm:text-sm font-bold text-red-600">3</div>
                      </div>
                      <div className="bg-white p-2 rounded border border-slate-100 shadow-sm overflow-hidden">
                        <div className="text-[7px] sm:text-[8px] text-slate-500 mb-1 truncate">Pending</div>
                        <div className="text-xs sm:text-sm font-bold text-amber-600">13</div>
                      </div>
                    </div>

                    {/* Bar Chart */}
                    <div className="bg-white p-3 rounded border border-slate-100 shadow-sm h-[100px] flex flex-col">
                      <div className="text-[9px] font-semibold text-slate-700 mb-2 flex items-center gap-1"><BarChart3 className="w-3 h-3" /> Reminders This Week</div>
                      <div className="flex-1 flex items-end justify-between gap-2 px-2">
                        <div className="w-full bg-green-100 rounded-t h-[40%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Mon</div></div>
                        <div className="w-full bg-green-100 rounded-t h-[60%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Tue</div></div>
                        <div className="w-full bg-green-500 rounded-t h-[90%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-green-600 font-bold">Wed</div></div>
                        <div className="w-full bg-green-100 rounded-t h-[50%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Thu</div></div>
                        <div className="w-full bg-green-100 rounded-t h-[70%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Fri</div></div>
                        <div className="w-full bg-green-100 rounded-t h-[30%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Sat</div></div>
                        <div className="w-full bg-green-100 rounded-t h-[20%] relative"><div className="absolute -top-3 left-1/2 -translate-x-1/2 text-[7px] text-slate-400">Sun</div></div>
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
                  APPOINTMENT BOOKING
                </span>
                <button className="w-10 h-10 bg-[#1E5F3A] rounded-full flex items-center justify-center hover:bg-[#15472B] transition-colors shrink-0">
                  <ArrowRight className="w-5 h-5 text-white" />
                </button>
              </div>
              
              <h3 className="text-[32px] font-bold mt-2 mb-8 leading-[1.2] pr-4">
                Patient books. You get a PDF. Receptionist handles the rest.
              </h3>
              
              <div className="w-full h-px bg-slate-200 mb-8"></div>
              
              <ul className="space-y-5 mb-12 relative z-10">
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">Patient books from WhatsApp reminder — no app, no login needed</span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">Online patients get priority queue over walk-ins automatically</span>
                </li>
                <li className="flex items-start gap-4">
                  <div className="mt-1 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center shrink-0">
                    <Check className="w-3.5 h-3.5 text-green-700 stroke-[3]" />
                  </div>
                  <span className="text-[15px] text-slate-700 leading-snug font-medium">Midnight PDF sent to doctor — organized list for next day</span>
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
                        <div className="text-xs font-bold text-slate-800">CareRemind</div>
                        <div className="text-[9px] text-green-500">Online</div>
                      </div>
                    </div>
                    {/* Chat Area */}
                    <div className="p-3 flex flex-col gap-3 overflow-y-auto text-[10px] flex-1 pb-6">
                      <div className="bg-[#1E5F3A] text-white p-2.5 rounded-xl rounded-tr-sm max-w-[85%] shadow-sm self-end">
                        📋 Reminder: Your follow-up with Dr. Abhishek is tomorrow at 10:30 AM. Tap below to book.
                      </div>
                      <div className="bg-white border border-slate-100 p-2.5 rounded-xl rounded-tl-sm max-w-[85%] shadow-sm self-start text-slate-800">
                        Your slot for 10:30 AM is confirmed ✅<br/>
                        Payment received ₹200
                      </div>
                      <div className="bg-[#1E5F3A] text-white p-2.5 rounded-xl rounded-tr-sm max-w-[85%] shadow-sm self-end">
                        How many booked tomorrow?
                      </div>
                      <div className="bg-white border border-slate-100 p-2.5 rounded-xl rounded-tl-sm max-w-[85%] shadow-sm self-start text-slate-800">
                        12 online bookings confirmed.<br/>
                        5 walk-in slots remaining.
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

      {/* Footer Section */}
      <FooterDemo />
    </div>
  );
}
