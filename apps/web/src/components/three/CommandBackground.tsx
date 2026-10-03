import React, { useMemo, useRef, useState, useEffect, Suspense } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  Float,
  Icosahedron,
  Sphere,
  MeshDistortMaterial,
  Torus,
} from "@react-three/drei";
import * as THREE from "three";
import { InteractiveDots } from "./InteractiveDots";

/* The focal 3D object: a slowly morphing distorted core wrapped in a wireframe shell. */
function OperationsCore({ color, color2 }: { color: string; color2: string }) {
  const group = useRef<THREE.Group>(null!);
  const shell = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.12;
      group.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.15) * 0.15;
    }
    if (shell.current) {
      shell.current.rotation.y -= delta * 0.18;
      shell.current.rotation.z += delta * 0.05;
    }
  });

  return (
    <group ref={group} position={[3.1, 0.1, -0.5]}>
      {/* morphing inner core */}
      <Sphere args={[1.7, 96, 96]}>
        <MeshDistortMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.55}
          roughness={0.28}
          metalness={0.65}
          distort={0.42}
          speed={1.6}
          transparent
          opacity={0.92}
        />
      </Sphere>
      {/* wireframe shell */}
      <Icosahedron ref={shell as any} args={[2.35, 1]}>
        <meshBasicMaterial color={color2} wireframe transparent opacity={0.22} />
      </Icosahedron>
      {/* orbiting ring */}
      <Torus args={[3, 0.012, 16, 100]} rotation={[Math.PI / 2.2, 0.3, 0]}>
        <meshBasicMaterial color={color} transparent opacity={0.4} />
      </Torus>
    </group>
  );
}

/* Secondary floating solids scattered on the left for depth. */
function FloatingSolids({ color, color2 }: { color: string; color2: string }) {
  return (
    <group>
      <Float speed={1.1} rotationIntensity={0.9} floatIntensity={1.4}>
        <Icosahedron args={[0.8, 0]} position={[-4.3, 1.6, -1.5]}>
          <meshBasicMaterial color={color} wireframe transparent opacity={0.17} />
        </Icosahedron>
      </Float>
      <Float speed={0.8} rotationIntensity={0.7} floatIntensity={1.0}>
        <Torus args={[0.7, 0.05, 16, 60]} position={[-3.2, -1.9, -1.8]} rotation={[0.6, 0.4, 0]}>
          <meshBasicMaterial color={color2} wireframe transparent opacity={0.2} />
        </Torus>
      </Float>
      <Float speed={1.5} rotationIntensity={1.1} floatIntensity={1.6}>
        <Icosahedron args={[0.45, 0]} position={[-2.1, 2.3, -1]}>
          <meshBasicMaterial color={color2} wireframe transparent opacity={0.22} />
        </Icosahedron>
      </Float>
    </group>
  );
}

function Rig() {
  const { camera } = useThree();
  useFrame((state) => {
    camera.position.x += (state.pointer.x * 0.6 - camera.position.x) * 0.02;
    camera.position.y += (state.pointer.y * 0.4 - camera.position.y) * 0.02;
    camera.lookAt(0, 0, 0);
  });
  return null;
}

interface Props {
  accent: [string, string];
}

export const CommandBackground: React.FC<Props> = ({ accent }) => {
  const [enabled, setEnabled] = useState(true);

  useEffect(() => {
    // Only disable when WebGL is genuinely unavailable. We intentionally do NOT
    // gate on prefers-reduced-motion here: the live command-center background is
    // a core part of the product and would otherwise silently fall back to a
    // flat gradient on machines that have "reduce motion" enabled.
    let webgl = true;
    try {
      const c = document.createElement("canvas");
      webgl = !!(c.getContext("webgl2") || c.getContext("webgl"));
    } catch {
      webgl = false;
    }
    setEnabled(webgl);
  }, []);

  // hex -> rgba helper for accent-driven glows
  const rgba = (hex: string, a: number) => {
    const h = hex.replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
  };

  // A bright "reactor" glow anchored where the 3D core sits, so the right side
  // always reads as a luminous core even if WebGL is unavailable.
  const coreGlow =
    `radial-gradient(34% 44% at 79% 40%, ${rgba(accent[0], 0.34)}, transparent 62%),` +
    `radial-gradient(26% 32% at 79% 40%, ${rgba(accent[0], 0.22)}, transparent 70%),` +
    `radial-gradient(55% 50% at 97% 18%, ${rgba(accent[1], 0.16)}, transparent 60%),` +
    `radial-gradient(50% 45% at 6% -5%, ${rgba(accent[0], 0.08)}, transparent 55%),` +
    `radial-gradient(70% 60% at 50% 122%, ${rgba(accent[1], 0.07)}, transparent 60%),` +
    `#04060f`;

  if (!enabled) {
    return <div aria-hidden className="fixed inset-0 -z-10 pointer-events-none" style={{ background: coreGlow }} />;
  }

  return (
    <div aria-hidden className="fixed inset-0 -z-10 pointer-events-none">
      <div className="absolute inset-0" style={{ background: coreGlow }} />
      {/* slow breathing halo behind the core */}
      <div
        className="absolute rounded-full blur-3xl animate-float-slow"
        style={{
          right: "8%",
          top: "22%",
          width: "34vw",
          height: "34vw",
          background: `radial-gradient(circle, ${rgba(accent[0], 0.22)}, transparent 68%)`,
        }}
      />
      <Canvas
        camera={{ position: [0, 0, 7], fov: 58 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        style={{ position: "absolute", inset: 0 }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.4} />
          <pointLight position={[6, 4, 5]} intensity={120} color={accent[0]} />
          <pointLight position={[-4, -3, 2]} intensity={70} color={accent[1]} />
          <OperationsCore color={accent[0]} color2={accent[1]} />
          <FloatingSolids color={accent[0]} color2={accent[1]} />
          <InteractiveDots
            color={accent[0]}
            color2={accent[1]}
            width={30}
            height={17}
            cols={170}
            rows={96}
            size={1.6}
            radius={0.18}
            pop={0.8}
            wave={0.85}
          />
          <Rig />
        </Suspense>
      </Canvas>
      {/* readability wash — darkens the left where content lives, keeps the core glowing on the right */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(90deg, rgba(4,6,15,0.62) 0%, rgba(4,6,15,0.34) 34%, rgba(4,6,15,0.0) 62%, rgba(4,6,15,0.08) 100%)",
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(135% 135% at 50% 50%, transparent 62%, rgba(4,6,15,0.42) 100%)",
        }}
      />
    </div>
  );
};
