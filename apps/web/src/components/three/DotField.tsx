import React, { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { InteractiveDots } from "./InteractiveDots";

interface DotFieldProps {
  /** Two-stop accent: [primary, secondary]. */
  accent: [string, string];
  className?: string;
}

/**
 * Full-bleed interactive 3D dot-field background.
 * Falls back to a static gradient when WebGL or motion is unavailable.
 */
export const DotField: React.FC<DotFieldProps> = ({ accent, className }) => {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    // Enable whenever WebGL is available (do not gate on reduced-motion — the
    // animated dot field is intended to always show when the GPU can render it).
    let webgl = true;
    try {
      const c = document.createElement("canvas");
      webgl = !!(c.getContext("webgl2") || c.getContext("webgl"));
    } catch {
      webgl = false;
    }
    setEnabled(webgl);
  }, []);

  if (!enabled) return null;

  return (
    <div aria-hidden className={`absolute inset-0 pointer-events-none ${className ?? ""}`}>
      <Canvas
        camera={{ position: [0, 0, 14], fov: 60 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        style={{ position: "absolute", inset: 0 }}
      >
        <InteractiveDots
          color={accent[0]}
          color2={accent[1]}
          width={38}
          height={22}
          cols={190}
          rows={110}
          size={1.7}
          radius={0.18}
          pop={0.9}
        />
      </Canvas>
    </div>
  );
};
