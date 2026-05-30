"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Download, RefreshCcw, MessageCircle, Heart, Share2, X, ZoomIn, ZoomOut, Sparkles } from "lucide-react";

type Variation = {
  image: string;
  score: number;
  scale: number;
};

export default function PreviewCanvas({
  originalImage,
  variations,
  productName,
  faceShape,
  onReset
}: {
  originalImage: string;
  variations: Variation[];
  productName: string;
  faceShape?: string | null;
  onReset: () => void;
}) {
  const [showOriginal, setShowOriginal] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showConsultCTA, setShowConsultCTA] = useState(false);
  const [isZoomed, setIsZoomed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowConsultCTA(true);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const activeImage = showOriginal ? originalImage : variations[selectedIndex].image;

  const handleWhatsApp = () => {
    const message = `Hi! I just tried the ${productName} using the Aura Virtual Try-On feature and would love to know more about pricing, availability, customization, and styling recommendations.`;
    const encodedMessage = encodeURIComponent(message);
    const whatsappUrl = `https://wa.me/1234567890?text=${encodedMessage}`;
    window.open(whatsappUrl, '_blank');
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Aura Virtual Try-On: ${productName}`,
          text: `Check out how the ${productName} looks on me!`,
          url: window.location.href, 
        });
      } catch (err) {
        console.error("Share failed:", err);
      }
    } else {
      alert("Sharing is not supported on this browser.");
    }
  };

  const getRecommendationText = () => {
    if (!faceShape) return null;
    switch(faceShape) {
      case "Round": return "Danglers and drops complement round faces beautifully.";
      case "Square": return "Hoops and rounded studs soften square jawlines.";
      case "Heart": return "Chandelier and teardrop shapes balance heart faces.";
      case "Oval": return "Your oval shape perfectly suits almost any style!";
      default: return "This piece highlights your features elegantly.";
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 flex flex-col items-center">
      
      <AnimatePresence>
        {showConsultCTA && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, height: 0 }}
            className="w-full bg-gradient-to-r from-amber-500/10 to-amber-600/10 border border-amber-500/20 rounded-2xl p-4 mb-6 flex flex-col sm:flex-row items-center justify-between gap-4"
          >
            <div>
              <h4 className="font-serif font-medium text-amber-500 text-lg">Looking for advice?</h4>
              <p className="text-zinc-400 text-sm">Connect with our luxury stylists for bespoke recommendations.</p>
            </div>
            <button 
              onClick={handleWhatsApp}
              className="px-6 py-2 bg-amber-500 text-zinc-950 font-medium rounded-full hover:bg-amber-400 transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              <MessageCircle className="w-4 h-4" />
              Consult Stylist
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {faceShape && (
        <div className="w-full flex items-center gap-2 mb-4 px-2">
          <Sparkles className="w-5 h-5 text-amber-500" />
          <span className="text-zinc-300 text-sm font-medium">
            Stylist Note for <span className="text-white font-serif">{faceShape}</span> Face: {getRecommendationText()}
          </span>
        </div>
      )}

      <div className="relative w-full aspect-[3/4] md:aspect-square max-h-[60vh] bg-zinc-900 rounded-2xl overflow-hidden shadow-2xl border border-zinc-800 group">
        <AnimatePresence mode="wait">
          <motion.img
            key={activeImage}
            initial={{ opacity: 0, scale: isZoomed ? 2 : 1 }}
            animate={{ opacity: 1, scale: isZoomed ? 2 : 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            drag={isZoomed}
            dragConstraints={{ left: -200, right: 200, top: -200, bottom: 200 }}
            src={activeImage}
            alt="Try-on Preview"
            className={`w-full h-full ${isZoomed ? "cursor-grab active:cursor-grabbing" : "object-contain"}`}
          />
        </AnimatePresence>

        <button 
          onPointerDown={() => setShowOriginal(true)}
          onPointerUp={() => setShowOriginal(false)}
          onPointerLeave={() => setShowOriginal(false)}
          className="absolute bottom-4 left-4 px-4 py-2 bg-zinc-950/80 backdrop-blur-md border border-zinc-700 text-sm font-medium rounded-full text-zinc-300 hover:text-white transition-colors z-10"
        >
          Hold to compare
        </button>

        <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
          <button 
            onClick={() => setIsZoomed(!isZoomed)}
            className="p-3 bg-zinc-950/80 backdrop-blur-md border border-zinc-700 rounded-full text-zinc-300 hover:text-white transition-colors"
            title="Zoom"
          >
            {isZoomed ? <ZoomOut className="w-5 h-5" /> : <ZoomIn className="w-5 h-5" />}
          </button>
           <button 
            onClick={handleShare}
            className="p-3 bg-zinc-950/80 backdrop-blur-md border border-zinc-700 rounded-full text-zinc-300 hover:text-white transition-colors opacity-0 group-hover:opacity-100 transition-opacity"
            title="Share"
          >
            <Share2 className="w-5 h-5" />
          </button>
           <a 
            href={variations[selectedIndex].image}
            download="aura-tryon.jpg"
            className="p-3 bg-zinc-950/80 backdrop-blur-md border border-zinc-700 rounded-full text-zinc-300 hover:text-white transition-colors flex opacity-0 group-hover:opacity-100 transition-opacity"
            title="Download"
          >
            <Download className="w-5 h-5" />
          </a>
        </div>
      </div>

      <div className="w-full mt-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex gap-2">
          {variations.map((v, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedIndex(idx)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedIndex === idx 
                  ? "bg-zinc-100 text-zinc-950" 
                  : "bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800"
              }`}
            >
              Fit {idx + 1}
              {idx === 0 && <span className="ml-2 text-xs text-amber-600 bg-amber-500/20 px-2 py-0.5 rounded-full">Best</span>}
            </button>
          ))}
        </div>

        <div className="flex gap-3 w-full md:w-auto mt-4 md:mt-0">
          <button 
            onClick={onReset}
            className="p-3 bg-zinc-900 text-zinc-400 hover:text-white rounded-full transition-colors border border-zinc-800"
            title="Try another"
          >
            <RefreshCcw className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => setShowSaveModal(true)}
            className="px-6 py-3 bg-zinc-800 text-white font-medium rounded-full hover:bg-zinc-700 transition-all flex items-center justify-center gap-2 flex-1 md:flex-none border border-zinc-700"
          >
            <Heart className="w-5 h-5" />
            Save Look
          </button>
          
          <button
            onClick={handleWhatsApp}
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-500 text-white font-medium rounded-full hover:from-green-500 hover:to-green-400 transition-all flex items-center justify-center gap-2 flex-1 md:flex-none shadow-lg shadow-green-900/20"
          >
            <MessageCircle className="w-5 h-5" />
            WhatsApp Us
          </button>
        </div>
      </div>

      <AnimatePresence>
        {showSaveModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-3xl p-8 relative"
            >
              <button 
                onClick={() => setShowSaveModal(false)}
                className="absolute top-6 right-6 text-zinc-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
              
              <h3 className="font-serif text-2xl mb-2 text-white">Save Your Lookbook</h3>
              <p className="text-zinc-400 text-sm mb-6">Enter your details to receive your high-res try-on images and styling tips.</p>
              
              <form onSubmit={(e) => { e.preventDefault(); setShowSaveModal(false); alert("Lookbook Saved! (Mock API Call)"); }} className="flex flex-col gap-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-1">WhatsApp Number *</label>
                  <input required type="tel" placeholder="+1 (555) 000-0000" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-amber-500 transition-colors" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-1">Email (Optional)</label>
                  <input type="email" placeholder="you@example.com" className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-amber-500 transition-colors" />
                </div>
                <button type="submit" className="w-full mt-2 px-6 py-4 bg-amber-500 text-zinc-950 font-bold rounded-xl hover:bg-amber-400 transition-colors">
                  Send My Lookbook
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
