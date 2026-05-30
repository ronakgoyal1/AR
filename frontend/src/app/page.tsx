"use client";

import { useState } from "react";
import ImageUploader from "@/components/ImageUploader";
import JewellerySelector, { SAMPLE_EARRINGS } from "@/components/JewellerySelector";
import PreviewCanvas from "@/components/PreviewCanvas";
import { Loader2 } from "lucide-react";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [selectedEarring, setSelectedEarring] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [faceShape, setFaceShape] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = (file: File) => {
    setSelectedFile(file);
    setOriginalImage(URL.createObjectURL(file));
    setResults(null);
    setFaceShape(null);
    setError(null);
  };

  const handleGenerate = async () => {
    if (!selectedFile || !selectedEarring) return;

    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("earring_id", selectedEarring);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/try-on`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Failed to process image");
      }

      setResults(data.results);
      setFaceShape(data.face_shape);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setOriginalImage(null);
    setResults(null);
    setFaceShape(null);
    setSelectedEarring(null);
  };

  return (
    <main className="flex-1 w-full max-w-7xl mx-auto px-6 py-12 md:py-20 flex flex-col">
      <header className="w-full text-center mb-12">
        <h1 className="font-serif text-4xl md:text-6xl font-bold tracking-tight mb-4">
          Aura <span className="gold-gradient-text">Virtual Try-On</span>
        </h1>
        <p className="text-zinc-400 text-lg md:text-xl max-w-2xl mx-auto font-light">
          Experience premium jewellery from the comfort of your home. Powered by advanced AI.
        </p>
      </header>

      {!originalImage ? (
        <ImageUploader onUpload={handleUpload} />
      ) : (
        <div className="w-full flex flex-col items-center animate-in fade-in slide-in-from-bottom-4 duration-700">
          {!results ? (
            <div className="w-full max-w-4xl flex flex-col items-center">
              <div className="w-full md:w-2/3 aspect-square md:aspect-video relative rounded-2xl overflow-hidden bg-zinc-900 border border-zinc-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={originalImage} 
                  alt="Original selfie" 
                  className="w-full h-full object-contain"
                />
              </div>
              
              <JewellerySelector 
                selectedId={selectedEarring} 
                onSelect={setSelectedEarring} 
              />

              {error && (
                <div className="mt-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl text-red-400 w-full text-center">
                  {error}
                </div>
              )}

              <div className="mt-8 flex gap-4 w-full md:w-auto">
                <button 
                  onClick={handleReset}
                  className="px-6 py-3 bg-zinc-900 text-zinc-300 rounded-full hover:bg-zinc-800 transition-colors flex-1 md:flex-none text-center"
                >
                  Start Over
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={!selectedEarring || isProcessing}
                  className="px-8 py-3 bg-gradient-to-r from-amber-600 to-amber-500 text-white font-medium rounded-full hover:from-amber-500 hover:to-amber-400 transition-all shadow-lg shadow-amber-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 flex-[2] md:flex-none"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    "Generate Try-On"
                  )}
                </button>
              </div>
            </div>
          ) : (
            <PreviewCanvas 
              originalImage={originalImage} 
              variations={results} 
              productName={SAMPLE_EARRINGS.find(e => e.id === selectedEarring)?.name || "Earrings"}
              faceShape={faceShape}
              onReset={handleReset}
            />
          )}
        </div>
      )}
    </main>
  );
}
