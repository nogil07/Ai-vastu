"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Float, PerspectiveCamera, Grid } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function ArchitecturalStructure() {
    const groupRef = useRef<THREE.Group>(null);

    useFrame((state) => {
        if (groupRef.current) {
            groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.05;
        }
    });

    return (
        <group ref={groupRef}>
            {/* Abstract Building Blocks */}
            <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
                <mesh position={[0, 0, 0]}>
                    <boxGeometry args={[4, 3, 4]} />
                    <meshStandardMaterial color="#d4af37" wireframe transparent opacity={0.1} />
                </mesh>
                <lineSegments position={[0, 0, 0]}>
                    <edgesGeometry args={[new THREE.BoxGeometry(4, 3, 4)]} />
                    <lineBasicMaterial color="#d4af37" transparent opacity={0.3} />
                </lineSegments>
            </Float>

            {/* Floating Elements */}
            <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
                <mesh position={[3, 2, 1]} rotation={[0.5, 0.5, 0]}>
                    <boxGeometry args={[1, 1, 1]} />
                    <meshStandardMaterial color="#ffffff" wireframe transparent opacity={0.1} />
                </mesh>
                <mesh position={[-3, -1, 2]} rotation={[0.2, 0.2, 0]}>
                    <boxGeometry args={[1.5, 1.5, 1.5]} />
                    <meshStandardMaterial color="#ffffff" wireframe transparent opacity={0.1} />
                </mesh>
            </Float>
        </group>
    );
}

export default function ArchitecturalScene() {
    return (
        <div className="absolute inset-0 -z-10 bg-[#0a0a0a]">
            <Canvas>
                <PerspectiveCamera makeDefault position={[0, 2, 12]} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#d4af37" />

                <ArchitecturalStructure />

                {/* Floor Grid */}
                <Grid
                    position={[0, -4, 0]}
                    args={[20, 20]}
                    cellSize={1}
                    cellThickness={0.5}
                    cellColor="#333"
                    sectionSize={5}
                    sectionThickness={1}
                    sectionColor="#d4af37"
                    fadeDistance={20}
                    fadeStrength={1}
                />

                <Environment preset="city" />
                <fog attach="fog" args={['#0a0a0a', 5, 20]} />
            </Canvas>

            {/* Overlay Gradient for Text Readability */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/80 pointer-events-none" />
        </div>
    );
}
