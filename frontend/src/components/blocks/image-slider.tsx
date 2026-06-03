import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const slides = [
  {
    src: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=2070&auto=format&fit=crop",
    title: "Focus on Patients, Not Paperwork",
    description:
      "Let AI handle your daily follow-ups, re-bookings, and payment reminders.",
  },
  {
    src: "https://images.unsplash.com/photo-1581056771107-24ca5f033842?q=80&w=2070&auto=format&fit=crop",
    title: "100% WhatsApp Automation",
    description:
      "Reach your patients where they already are. No apps to download or portals to log into.",
  },
  {
    src: "https://images.unsplash.com/photo-1530497610245-94d3c16cda28?q=80&w=2070&auto=format&fit=crop",
    title: "Eliminate No-Shows",
    description:
      "Keep your clinic running at maximum capacity with timely automated reminders.",
  },
  {
    src: "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?q=80&w=2053&auto=format&fit=crop",
    title: "Instant Setup & Reporting",
    description:
      "Get started in minutes and receive daily PDF reports right to your phone.",
  },
];

const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? "100%" : "-100%",
    opacity: 0.5,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction < 0 ? "100%" : "-100%",
    opacity: 0.5,
  }),
};

export function ImageSlider() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const [isHovered, setIsHovered] = useState(false);

  const nextSlide = useCallback(() => {
    setDirection(1);
    setCurrentIndex((prevIndex) =>
      prevIndex === slides.length - 1 ? 0 : prevIndex + 1,
    );
  }, []);

  const prevSlide = useCallback(() => {
    setDirection(-1);
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? slides.length - 1 : prevIndex - 1,
    );
  }, []);

  useEffect(() => {
    if (isHovered) return;
    const timer = setInterval(() => {
      nextSlide();
    }, 5000);
    return () => clearInterval(timer);
  }, [nextSlide, isHovered]);

  const goToSlide = (index: number) => {
    if (index === currentIndex) return;
    setDirection(index > currentIndex ? 1 : -1);
    setCurrentIndex(index);
  };

  return (
    <div
      className="relative w-full h-[400px] sm:h-[450px] md:h-[600px] lg:h-[700px] rounded-none sm:rounded-[32px] overflow-hidden shadow-none sm:shadow-2xl group cursor-pointer bg-slate-900"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="absolute inset-0 w-full h-full flex items-center justify-center">
        <AnimatePresence initial={false} custom={direction}>
          <motion.div
            key={currentIndex}
            custom={direction}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{
              type: "tween",
              duration: 0.6,
              ease: [0.25, 0.1, 0.25, 1],
            }}
            className="absolute inset-0 w-full h-full"
          >
            <img
              src={slides[currentIndex].src}
              alt={slides[currentIndex].title}
              className="w-full h-full object-cover"
            />
            {/* Gradient Overlay for text readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/50 to-transparent flex flex-col justify-end p-6 sm:p-8 md:p-14">
              <motion.h3
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.5, ease: "easeOut" }}
                className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2 sm:mb-3 md:mb-4 tracking-tight drop-shadow-md pr-12 sm:pr-0"
              >
                {slides[currentIndex].title}
              </motion.h3>
              <motion.p
                initial={{ y: 30, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5, ease: "easeOut" }}
                className="text-sm sm:text-base md:text-xl text-slate-200 max-w-2xl leading-relaxed drop-shadow-md pr-8 sm:pr-0"
              >
                {slides[currentIndex].description}
              </motion.p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation Overlays */}
      <div className="absolute inset-0 flex items-center justify-between p-2 sm:p-4 pointer-events-none opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
        <button
          onClick={(e) => {
            e.stopPropagation();
            prevSlide();
          }}
          className="w-10 h-10 sm:w-12 sm:h-12 bg-black/30 backdrop-blur-md hover:bg-black/50 border border-white/10 rounded-full flex items-center justify-center text-white pointer-events-auto transition-colors z-20"
        >
          <ChevronLeft className="w-5 h-5 sm:w-6 sm:h-6" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            nextSlide();
          }}
          className="w-10 h-10 sm:w-12 sm:h-12 bg-black/30 backdrop-blur-md hover:bg-black/50 border border-white/10 rounded-full flex items-center justify-center text-white pointer-events-auto transition-colors z-20"
        >
          <ChevronRight className="w-5 h-5 sm:w-6 sm:h-6" />
        </button>
      </div>

      {/* Pagination Indicators */}
      <div className="absolute bottom-6 md:bottom-8 right-6 md:right-12 flex items-center gap-2 z-20">
        {slides.map((_, idx) => (
          <button
            key={idx}
            onClick={(e) => {
              e.stopPropagation();
              goToSlide(idx);
            }}
            className={cn(
              "h-2 rounded-full transition-all duration-300",
              currentIndex === idx
                ? "w-8 bg-green-500"
                : "w-2 bg-white/50 hover:bg-white/80",
            )}
            aria-label={`Go to slide ${idx + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
