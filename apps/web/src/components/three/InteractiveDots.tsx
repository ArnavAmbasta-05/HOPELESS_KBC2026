import { useMemo, useRef, useEffect } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

/**
 * InteractiveDots — a live, 3D, hover-reactive dot field.
 *
 * - 3D: a perspective grid of points with per-dot depth.
 * - Live: a continuous sine/cosine wave displaces each dot's z every frame.
 * - Hover: the window pointer is projected to screen space; dots near the
 *   cursor pop toward the camera, grow and brighten (smooth falloff).
 *
 * Tracks `window` pointermove (not canvas pointer events) so it still reacts to
 * the cursor when rendered behind click-through UI (pointer-events: none).
 */

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform vec2  uMouse;   // pointer in NDC (-1..1)
  uniform float uAspect;
  uniform float uSize;
  uniform float uRadius;  // influence radius in NDC
  uniform float uPop;     // view-space pop toward camera near the cursor
  uniform float uWave;    // wave amplitude
  attribute float aScale; // per-dot size/brightness variation
  varying float vBright;
  varying float vInfluence;

  void main() {
    vec3 p = position;

    // live wave motion (gives the flat grid 3D life); per-dot phase via aScale
    float w = sin(p.x * 0.35 + uTime * 0.8 + aScale * 6.28) * 0.5
            + cos(p.y * 0.40 + uTime * 0.6 + aScale * 3.14) * 0.5;
    p.z += w * uWave;

    vec4 mv = modelViewMatrix * vec4(p, 1.0);

    // screen-space proximity to the pointer
    vec4 clip = projectionMatrix * mv;
    vec2 ndc = clip.xy / clip.w;
    vec2 d = ndc - uMouse;
    d.x *= uAspect;
    float influence = smoothstep(uRadius, 0.0, length(d));
    vInfluence = influence;

    // pop toward camera near the cursor
    mv.z += influence * uPop;

    // natural brightness variation + a gentle idle twinkle
    float twinkle = 0.85 + 0.15 * sin(uTime * 1.5 + aScale * 12.0);
    vBright = (0.30 + aScale * 0.45) * twinkle + influence * 0.45;

    gl_Position = projectionMatrix * mv;
    // perspective-attenuated point size (kept in a sane pixel range)
    gl_PointSize = uSize * (0.55 + aScale * 0.6) * (1.0 + influence * 1.0) * (42.0 / max(0.001, -mv.z));
  }
`;

const fragmentShader = /* glsl */ `
  uniform vec3 uColor;
  uniform vec3 uColor2;
  varying float vBright;
  varying float vInfluence;

  void main() {
    vec2 c = gl_PointCoord - 0.5;
    float dist = length(c);
    if (dist > 0.5) discard;
    float alpha = smoothstep(0.5, 0.0, dist);
    vec3 col = mix(uColor, uColor2, vInfluence * 0.5);
    col = mix(col, vec3(1.0), vInfluence * 0.25); // subtle brighten on hover
    gl_FragColor = vec4(col * vBright, alpha * clamp(0.55 + vBright * 0.5, 0.0, 1.0));
  }
`;

interface InteractiveDotsProps {
  color: string;
  color2: string;
  cols?: number;
  rows?: number;
  width?: number;
  height?: number;
  depth?: number;
  size?: number;
  radius?: number;
  pop?: number;
  wave?: number;
}

export function InteractiveDots({
  color,
  color2,
  cols = 150,
  rows = 86,
  width = 30,
  height = 18,
  depth = 3,
  size = 1.7,
  radius = 0.22,
  pop = 2.1,
  wave = 1.0,
}: InteractiveDotsProps) {
  const ref = useRef<THREE.Points>(null!);
  // start the cursor far off-screen so no hover glow shows until the user moves
  const mouseTarget = useRef(new THREE.Vector2(10, 10));
  const { size: viewport } = useThree();

  const geometry = useMemo(() => {
    const count = cols * rows;
    const positions = new Float32Array(count * 3);
    const scales = new Float32Array(count);
    let i = 0;
    let s = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        // slight jitter so the grid doesn't look mechanical
        const jx = (Math.random() - 0.5) * (width / cols) * 0.8;
        const jy = (Math.random() - 0.5) * (height / rows) * 0.8;
        positions[i++] = (c / (cols - 1)) * width - width / 2 + jx;
        positions[i++] = (r / (rows - 1)) * height - height / 2 + jy;
        positions[i++] = (Math.random() - 0.5) * depth; // per-dot depth → 3D
        scales[s++] = Math.random();
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.setAttribute("aScale", new THREE.BufferAttribute(scales, 1));
    return g;
  }, [cols, rows, width, height, depth]);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector2(10, 10) },
      uAspect: { value: 1 },
      uSize: { value: size },
      uRadius: { value: radius },
      uPop: { value: pop },
      uWave: { value: wave },
      uColor: { value: new THREE.Color(color) },
      uColor2: { value: new THREE.Color(color2) },
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  // keep colors in sync if the role accent changes
  useEffect(() => {
    uniforms.uColor.value.set(color);
    uniforms.uColor2.value.set(color2);
  }, [color, color2, uniforms]);

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      mouseTarget.current.set(
        (e.clientX / window.innerWidth) * 2 - 1,
        -((e.clientY / window.innerHeight) * 2 - 1)
      );
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  useFrame((state, delta) => {
    uniforms.uTime.value += delta;
    uniforms.uMouse.value.lerp(mouseTarget.current, 0.09); // smooth follow
    uniforms.uAspect.value = viewport.width / viewport.height;
    if (ref.current) {
      ref.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.05) * 0.04;
      ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.07) * 0.05;
    }
  });

  return (
    <points ref={ref} geometry={geometry} frustumCulled={false}>
      <shaderMaterial
        uniforms={uniforms}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
