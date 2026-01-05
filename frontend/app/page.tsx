import ArchitecturalScene from "@/components/visuals/ArchitecturalScene";
import VastuForm from "@/components/ui/VastuForm";

export default function Home() {
  return (
    <main className="min-h-screen relative flex flex-col justify-center overflow-hidden">
      {/* 3D Background */}
      <ArchitecturalScene />

      {/* Content Layer */}
      <div className="relative z-10 w-full">
        <VastuForm />
      </div>
    </main>
  );
}
