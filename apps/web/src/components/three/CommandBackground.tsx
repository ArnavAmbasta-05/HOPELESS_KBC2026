import React, { useMemo, useRef, useState, useEffect, Suspense } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Points, PointMaterial, Float, Icosahedron, Torus } from "@react-three/drei";
import * as THREE from "three";

/* A drifting constellation of points filling a spherical shell. */
function Constellation({ color, count = 1700 }: { color: string; count?: number }) {
  const ref = useRef<THREE.Points>(null!);

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      // random point in a spherical shell (radius 2.2 - 6)
      const r = 2.2 + Math.random() * 3.8;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, [count]);

  useFrame((state, delta) => {
    if (!ref.current) return;
    ref.current.rotation.y += delta * 0.018;
    ref.current.rotation.x += delta * 0.006;
    // gentle parallax toward the pointer
    const { x, y } = state.pointer;
    ref.current.rotation.y += x * delta * 0.05;
    ref.current.rotation.x += -y * delta * 0.05;
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={color}
        size={0.022}
        sizeAttenuation
        depthWrite={false}
        opacity={0.85}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

/* A few slow, luminous wireframe solids that drift behind the content. */
function FloatingSolids({ color, color2 }: { color: string; color2: string }) {
  return (
    <group>
      <Float speed={1.1} rotationIntensity={0.9} floatIntensity={1.3}>
        <Icosahedron args={[1.15, 0]} position={[-3.1, 1.2, -1]}>
          <meshBasicMaterial color={color} wireframe transparent opacity={0.16} />
        </Icosahedron>
      </Float>
      <Float speed={0.8} rotationIntensity={0.7} floatIntensity={1.0}>
        <Torus args={[0.85, 0.055, 16, 60]} position={[3.4, -1.1, -1.4]} rotation={[0.6, 0.4, 0]}>
          <meshBasicMaterial color={color2} wireframe transparent opacity={0.18} />
        </Torus>
      </Float>
      <Float speed={1.4} rotationIntensity={1.2} floatIntensity={1.6}>
        <Icosahedron args={[0.6, 0]} position={[2.2, 1.9, -0.5]}>
          <meshBasicMaterial color={color2} wireframe transparent opacity={0.2} />
        </Icosahedron>
      </Float>
      <Float speed={0.6} rotationIntensity={0.5} floatIntensity={0.8}>
        <Icosahedron args={[0.9, 0]} position={[-2.6, -1.8, -1.2]}>
          <meshBasicMaterial color={color} wireframe transparent opacity={0.13} />
        </Icosahedron>
      </Float>
    </group>
  );
}

function Rig() {
  const { camera } = useThree();
  useFrame((state) => {
    // subtle camera sway follows the pointer for depth
    camera.position.x += (state.pointer.x * 0.5 - camera.position.x) * 0.02;
    camera.position.y += (state.pointer.y * 0.3 - camera.position.y) * 0.02;
    camera.lookAt(0, 0, 0);
  });
  return null;
}

interface Props {
  /** [accent, accent2] from the active role */
  accent: [string, string];
}

/**
 * Fixed, non-interactive WebGL field rendered behind the whole shell.
 * Falls back silently (renders nothing) if WebGL is unavailable or the
 * user prefers reduced motion.
 */
export const CommandBackground: React.FC<Props> = ({ accent }) => {
  const [enabled, setEnabled] = useState(true);

  useEffect(() => {
    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // crude WebGL capability probe
    let webgl = true;
    try {
      const c = document.createElement("canvas");
      webgl = !!(c.getContext("webgl2") || c.getContext("webgl"));
    } catch {
      webgl = false;
    }
    setEnabled(!reduce && webgl);
  }, []);

  if (!enabled) {
    // static aurora fallback
    return (
      <div
        aria-hidden
        className="fixed inset-0 -z-10 pointer-events-none"
        style={{
          background:
            "radial-gradient(60% 50% at 15% 0%, rgba(34,211,238,0.10), transparent 60%), radial-gradient(55% 45% at 90% 10%, rgba(168,85,247,0.10), transparent 60%), #04060f",
        }}
      />
    );
  }

  return (
    <div aria-hidden className="fixed inset-0 -z-10 pointer-events-none">
      {/* layered gradient wash that lives under the canvas */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 50% at 12% -5%, rgba(34,211,238,0.12), transparent 58%), radial-gradient(55% 45% at 92% 8%, rgba(168,85,247,0.12), transparent 58%), radial-gradient(70% 60% at 50% 120%, rgba(45,212,191,0.07), transparent 60%), #04060f",
        }}
      />
      <Canvas
        camera={{ position: [0, 0, 6], fov: 60 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        style={{ position: "absolute", inset: 0 }}
      >
        <Suspense fallback={null}>
          <Constellation color={accent[0]} />
          <FloatingSolids color={accent[0]} color2={accent[1]} />
          <Rig />
        </Suspense>
      </Canvas>
      {/* vignette to keep edges calm and text legible */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(120% 120% at 50% 50%, transparent 55%, rgba(4,6,15,0.55) 100%)",
        }}
      />
    </div>
  );
};
