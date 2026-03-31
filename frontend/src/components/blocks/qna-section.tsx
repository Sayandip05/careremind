import { useState } from "react";
import { ChevronDown } from "lucide-react";

export function QnASection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      question: "How exactly does CareRemind help me?",
      answer: "CareRemind automates your patient follow-ups. You simply send a WhatsApp photo of your daily register, and our AI extracts the details to send automated, personalized WhatsApp reminders to your patients, saving your staff hours of manual calling."
    },
    {
      question: "Does CareRemind help employees with claims?",
      answer: "CareRemind is focused on clinic-to-patient communication and appointment reminders. We do not currently handle insurance claims or employee benefits."
    },
    {
      question: "Why should I trust CareRemind with my patient's data?",
      answer: "We take data privacy very seriously. All patient data extracted from your notepad is encrypted and processed securely. We comply with standard healthcare data protection regulations to ensure your patients' information is safe."
    },
    {
      question: "Is CareRemind free?",
      answer: "We offer a 14-day free trial so you can experience the benefits firsthand. After that, we have affordable subscription plans tailored for solo clinics and larger practices."
    },
    {
      question: "Do you have a mobile app?",
      answer: "Currently, CareRemind operates primarily through WhatsApp for your convenience. You don't need to download a separate app to send us your register photos. We also provide a web dashboard for you to track analytics."
    },
    {
      question: "Do you provide solutions for clinics of all sizes?",
      answer: "Yes! While CareRemind is loved by solo doctors, our platform is scalable and can handle the reminder volume for multi-doctor clinics and larger healthcare facilities."
    },
    {
      question: "What do you mean by automated reminders?",
      answer: "Once our AI processes your register, it schedules WhatsApp messages to be sent to those patients at the optimal time (e.g., a day before their follow-up date), without any manual intervention from your team."
    }
  ];

  return (
    <section className="w-full py-16 md:py-24 bg-[#f9fafb]">
      <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row gap-12 md:gap-24">
        
        {/* Left Side - Heading */}
        <div className="md:w-1/3">
          <h2 className="text-4xl md:text-5xl font-serif font-bold text-[#1e293b] leading-tight sticky top-24">
            Got questions?<br />
            We've got answers
          </h2>
        </div>

        {/* Right Side - Accordion */}
        <div className="md:w-2/3">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            {faqs.map((faq, index) => (
              <div 
                key={index} 
                className={`border-b border-slate-100 last:border-0 ${openIndex === index ? 'bg-slate-50/50' : 'bg-white'}`}
              >
                <button
                  className="w-full text-left px-6 py-5 flex items-center justify-between focus:outline-none"
                  onClick={() => setOpenIndex(openIndex === index ? null : index)}
                >
                  <span className="font-medium text-slate-800 pr-8">{faq.question}</span>
                  <div className={`w-8 h-8 rounded-full border border-slate-200 flex items-center justify-center shrink-0 transition-transform duration-200 ${openIndex === index ? 'rotate-180 bg-white' : 'bg-transparent'}`}>
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  </div>
                </button>
                
                <div 
                  className={`overflow-hidden transition-all duration-300 ease-in-out ${openIndex === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}
                >
                  <div className="px-6 pb-5 text-slate-600 leading-relaxed">
                    {faq.answer}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}
