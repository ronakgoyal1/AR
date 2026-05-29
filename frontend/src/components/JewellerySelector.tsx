"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

export type Earring = {
  id: string;
  name: string;
  color: string;
  price: string;
};

export const SAMPLE_EARRINGS: Earring[] = [
  { id: "e1", name: "Classic Gold Hoops", color: "Gold", price: "$250" },
  { id: "e2", name: "Pearl Drops", color: "Silver/Pearl", price: "$320" },
  { id: "e3", name: "Diamond Studs", color: "Platinum", price: "$850" },
];

export default function JewellerySelector({ 
  selectedId, 
  onSelect 
}: { 
  selectedId: string | null; 
  onSelect: (id: string) => void;
}) {
  return (
    <div className="w-full mt-8">
      <h3 className="font-serif text-xl mb-4">Select Jewellery</h3>
      <div className="flex gap-4 overflow-x-auto pb-4 snap-x custom-scrollbar">
        {SAMPLE_EARRINGS.map((item) => (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`relative flex-shrink-0 w-48 p-4 rounded-xl border text-left transition-all snap-start ${
              selectedId === item.id 
                ? "border-amber-500 bg-amber-500/10" 
                : "border-zinc-800 bg-zinc-900/30 hover:border-zinc-700"
            }`}
          >
            {selectedId === item.id && (
              <div className="absolute top-3 right-3 bg-amber-500 text-zinc-950 p-1 rounded-full">
                <Check className="w-3 h-3" />
              </div>
            )}
            <div className="w-full h-32 bg-zinc-800 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
              {/* Placeholder for real earring image */}
              <div className="w-12 h-16 border-2 border-dashed border-zinc-600 rounded-full opacity-50"></div>
            </div>
            <h4 className="font-medium text-zinc-100">{item.name}</h4>
            <p className="text-sm text-zinc-400 mt-1">{item.color}</p>
            <p className="text-sm font-semibold gold-gradient-text mt-2">{item.price}</p>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
