"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Compass, Layers, Ruler, Home, ArrowRight, Loader2, Download, FileText } from "lucide-react";
import axios from "axios";
import { cn } from "@/lib/utils";

// Types matching backend
interface VastuResponse {
    images: string[];
    reports: string[];
    image_base64: string;
    prompt: string;
}

export default function VastuForm() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<VastuResponse | null>(null);

    const [formData, setFormData] = useState({
        // 1. Plot & Site
        plot: {
            length: 40,
            width: 30,
            unit: "ft",
            shape: "rectangle",
            facing: "N"
        },
        // 2. Building
        building: {
            floors: "G",
            building_type: "independent_house"
        },
        // 3. Rooms
        rooms: {
            bedrooms: 2,
            bathrooms: 2,
            kitchen: true,
            living_room: true,
            dining_area: true,
            pooja_room: true,
            study_room: false,
            balcony: false,
            parking: true
        },
        // 4. Vastu Preference
        vastu_preference: "Balanced",
        // 5. Entrance
        entrance: {
            main_entrance_preference: [],
            separate_service_entry: false
        },
        // 6. Room Sizes
        room_sizes: {
            master_bedroom: "medium",
            kitchen: "medium",
            living_room: "medium"
        },
        // 7. Lifestyle
        lifestyle: {
            layout_style: "modern",
            open_kitchen: true,
            natural_light_priority: "medium"
        },
        // 8. Output
        output: {
            number_of_plans: 3,
            output_format: "2D",
            export_format: ["PDF"]
        }
    });

    const updateNested = (section: string, key: string, value: any) => {
        setFormData(prev => ({
            ...prev,
            [section]: {
                ...(prev as any)[section],
                [key]: value
            }
        }));
    };

    const updatePlot = (key: string, value: any) => updateNested('plot', key, value);
    const updateBuilding = (key: string, value: any) => updateNested('building', key, value);
    const updateRooms = (key: string, value: any) => updateNested('rooms', key, value);
    const updateDesign = (key: string, value: any) => updateNested('lifestyle', key, value);

    const generateDesign = async () => {
        setLoading(true);
        setResult(null);
        try {
            // New Payload Construction mapping directly to UserInput schema
            const payload = {
                plot: formData.plot,
                building: formData.building,
                rooms: formData.rooms,
                vastu_preference: formData.vastu_preference,
                entrance: formData.entrance,
                room_sizes: formData.room_sizes,
                lifestyle: formData.lifestyle,
                output: formData.output,
                // Legacy support just in case
                design: { style: formData.lifestyle.layout_style, layout_type: 'custom', natural_lighting: formData.lifestyle.natural_light_priority, visualization: '2D' },
                vastu_level: formData.vastu_preference
            };

            // Use environment variable for API URL or default to localhost
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
            const response = await axios.post(`${apiUrl}/generate-design`, payload);
            setResult(response.data);
        } catch (error) {
            console.error("Generation failed:", error);
            alert("Failed to generate design. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = (base64Pdf: string, index: number) => {
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${base64Pdf}`;
        link.download = `Vastu_Report_Option_${index + 1}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="w-full max-w-6xl mx-auto px-4 py-8 z-10 relative">
            <AnimatePresence mode="wait">
                {!result ? (
                    <motion.div
                        key="form"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start"
                    >
                        {/* Left: Branding & Info */}
                        <div className="space-y-6 lg:sticky lg:top-24">
                            <h1 className="text-5xl md:text-7xl font-light tracking-tighter text-white">
                                VASTU <span className="text-gradient-gold font-serif italic">AI</span>
                            </h1>
                            <p className="text-lg text-white/60 font-light max-w-md">
                                Generative architectural intelligence tailored to ancient Vedic principles.
                                Input your detailed requirements for a fully optimized blueprint.
                            </p>
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2 text-sm text-gold-500/80 border border-gold-500/30 px-3 py-1 rounded-full bg-gold-500/5">
                                    <span className="w-2 h-2 rounded-full bg-[#d4af37] animate-pulse" /> Advanced Mode
                                </div>
                            </div>
                        </div>

                        {/* Right: Glass Form - Accordion Style */}
                        <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group space-y-8">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-[#d4af37]/10 blur-3xl -z-10 transition-all duration-700 group-hover:bg-[#d4af37]/20" />

                            {/* Section 1: Plot Details */}
                            <div className="space-y-4">
                                <h3 className="text-[#d4af37] text-sm uppercase tracking-widest border-b border-white/10 pb-2 flex items-center gap-2">
                                    <Ruler className="w-4 h-4" /> 1. Plot & Site
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Length</label>
                                        <input type="number" value={formData.plot.length}
                                            onChange={(e) => updatePlot('length', Number(e.target.value))}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white" />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Width</label>
                                        <input type="number" value={formData.plot.width}
                                            onChange={(e) => updatePlot('width', Number(e.target.value))}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white" />
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Unit</label>
                                        <select value={formData.plot.unit} onChange={(e) => updatePlot('unit', e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="ft">Feet</option>
                                            <option value="m">Meters</option>
                                        </select>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Facing</label>
                                        <select value={formData.plot.facing} onChange={(e) => updatePlot('facing', e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="N">North</option>
                                            <option value="S">South</option>
                                            <option value="E">East</option>
                                            <option value="W">West</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Section 2: Building */}
                            <div className="space-y-4">
                                <h3 className="text-[#d4af37] text-sm uppercase tracking-widest border-b border-white/10 pb-2 flex items-center gap-2">
                                    <Layers className="w-4 h-4" /> 2. Building
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Floors</label>
                                        <select value={formData.building.floors} onChange={(e) => updateBuilding('floors', e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="G">Ground Only</option>
                                            <option value="G+1">G + 1</option>
                                            <option value="G+2">G + 2</option>
                                        </select>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Type</label>
                                        <select value={formData.building.building_type} onChange={(e) => updateBuilding('building_type', e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="independent_house">Independent House</option>
                                            <option value="villa">Villa</option>
                                            <option value="duplex">Duplex</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Section 3: Rooms */}
                            <div className="space-y-4">
                                <h3 className="text-[#d4af37] text-sm uppercase tracking-widest border-b border-white/10 pb-2 flex items-center gap-2">
                                    <Home className="w-4 h-4" /> 3. Room Requirements
                                </h3>
                                <div className="flex gap-4">
                                    <div className="flex-1 space-y-1">
                                        <label className="text-xs text-white/50">Bedrooms</label>
                                        <input type="number" value={formData.rooms.bedrooms}
                                            onChange={(e) => updateRooms('bedrooms', Number(e.target.value))}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white" />
                                    </div>
                                    <div className="flex-1 space-y-1">
                                        <label className="text-xs text-white/50">Bathrooms</label>
                                        <input type="number" value={formData.rooms.bathrooms}
                                            onChange={(e) => updateRooms('bathrooms', Number(e.target.value))}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white" />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    {[
                                        { key: 'pooja_room', label: 'Pooja Room' },
                                        { key: 'study_room', label: 'Study Room' },
                                        { key: 'parking', label: 'Parking' },
                                        { key: 'balcony', label: 'Balcony' }
                                    ].map((room) => (
                                        <label key={room.key} className="flex items-center gap-2 text-sm text-white/80 cursor-pointer hover:text-[#d4af37]">
                                            <input type="checkbox"
                                                checked={formData.rooms[room.key as keyof typeof formData.rooms] as boolean}
                                                onChange={(e) => updateRooms(room.key, e.target.checked)}
                                                className="w-4 h-4 rounded border-white/20 bg-black/40 text-[#d4af37] focus:ring-[#d4af37]/50" />
                                            {room.label}
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Section 4: Preferences */}
                            <div className="space-y-4">
                                <h3 className="text-[#d4af37] text-sm uppercase tracking-widest border-b border-white/10 pb-2 flex items-center gap-2">
                                    <Compass className="w-4 h-4" /> 4. Preferences
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Vastu Level</label>
                                        <select value={formData.vastu_preference} onChange={(e) => setFormData({ ...formData, vastu_preference: e.target.value })}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="High">High (Strict)</option>
                                            <option value="Medium">Medium (Balanced)</option>
                                            <option value="Low">Low (Flexible)</option>
                                        </select>
                                    </div>
                                    <div className="space-y-1">
                                        <label className="text-xs text-white/50">Style</label>
                                        <select value={formData.lifestyle.layout_style} onChange={(e) => updateDesign('layout_style', e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white [&>option]:bg-black">
                                            <option value="modern">Modern</option>
                                            <option value="traditional">Traditional</option>
                                            <option value="minimalist">Minimalist</option>
                                        </select>
                                    </div>
                                </div>
                            </div>


                            <button
                                onClick={generateDesign}
                                disabled={loading}
                                className="w-full bg-[#d4af37] hover:bg-[#b08d26] text-black font-bold py-4 rounded-xl flex items-center justify-center gap-3 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" /> Constructing Blueprint...
                                    </>
                                ) : (
                                    <>
                                        Generate Design <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div >
                ) : (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-8"
                    >
                        <div className="flex justify-between items-end">
                            <div>
                                <h2 className="text-4xl font-light text-white mb-2">Generated Proposals</h2>
                                <p className="text-white/50">Found 3 optimal configurations based on {formData.plot.facing} orientation.</p>
                            </div>
                            <button onClick={() => setResult(null)} className="text-[#d4af37] hover:text-white transition-colors underline underline-offset-4">
                                Modify Requirements
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {result.images.map((img, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="glass-panel rounded-xl overflow-hidden group"
                                >
                                    <div className="aspect-[4/3] bg-black/50 relative">
                                        <img src={`data:image/png;base64,${img}`} alt={`Option ${idx + 1}`} className="w-full h-full object-contain p-4" />
                                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
                                    </div>

                                    <div className="p-6 space-y-4">
                                        <div className="flex justify-between items-center">
                                            <h3 className="text-lg font-bold text-white">Option {String.fromCharCode(65 + idx)}</h3>
                                            <span className="text-xs bg-[#d4af37]/10 text-[#d4af37] px-2 py-1 rounded">
                                                {idx === 0 ? "Strict Vastu" : idx === 1 ? "Balanced" : "Relaxed"}
                                            </span>
                                        </div>

                                        <button
                                            onClick={() => downloadReport(result.reports[idx], idx)}
                                            className="w-full border border-white/10 hover:bg-white/5 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors text-sm"
                                        >
                                            <Download className="w-4 h-4" /> Download PDF Report
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence >
        </div >
    );
}
