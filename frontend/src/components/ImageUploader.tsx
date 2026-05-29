"use client";

import { useState, useRef } from "react";
import { UploadCloud, Camera } from "lucide-react";
import { motion } from "framer-motion";

export default function ImageUploader({ onUpload }: { onUpload: (file: File) => void }) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative w-full max-w-xl mx-auto mt-12 p-12 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center transition-colors duration-300 ${dragActive ? "border-amber-500 bg-amber-500/5" : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-800/50"}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input 
        ref={inputRef}
        type="file" 
        accept="image/*" 
        onChange={handleChange} 
        className="hidden" 
      />
      <div className="bg-zinc-800 p-4 rounded-full mb-6">
        <Camera className="w-8 h-8 text-zinc-300" />
      </div>
      <h3 className="font-serif text-2xl mb-2">Upload a Selfie</h3>
      <p className="text-zinc-400 text-center mb-8 max-w-sm">
        For best results, face the camera directly with good lighting and your ears visible.
      </p>
      
      <button 
        onClick={() => inputRef.current?.click()}
        className="px-8 py-3 bg-zinc-100 text-zinc-950 font-medium rounded-full hover:bg-white transition-colors flex items-center gap-2"
      >
        <UploadCloud className="w-5 h-5" />
        Choose Image
      </button>
    </motion.div>
  );
}
