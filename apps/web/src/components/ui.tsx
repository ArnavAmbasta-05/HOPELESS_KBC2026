import React, { useRef, useState, useEffect } from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useSpring,
  useReducedMotion,
  type Variants,
} from "framer-motion";
import clsx from "clsx";

/* ----------------------------------------------------------------------------
 * Motion presets
 * ------------------------------------------------------------------------- */
export const easeOutExpo = [0.16, 1, 0.3, 1] as const;

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: easeOutExpo } },
};

export const stagger: Variants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.04 } },
};

/* ----------------------------------------------------------------------------
 * Reveal — scroll-triggered entrance. Wrap any block.
 * ------------------------------------------------------------------------- */
export const Reveal: React.FC<{
  children: React.ReactNode;
  className?: string;
  delay?: number;
  y?: number;
  as?: "div" | "section" | "li";
}> = ({ children, className, delay = 0, y = 26, as = "div" }) => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-12% 0px -8% 0px" });
  const reduce = useReducedMotion();
  const MotionTag = motion[as] as typeof motion.div;
  return (
    <MotionTag
      ref={ref as any}
      className={className}
      initial={reduce ? false : { opacity: 0, y }}
      animate={inView ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.6, ease: easeOutExpo, delay }}
    >
      {children}
    </MotionTag>
  );
};

/* Container that staggers its direct Reveal/motion children. */
export const RevealGroup: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className }) => {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-10% 0px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      variants={stagger}
      initial="hidden"
      animate={inView ? "show" : "hidden"}
    >
      {children}
    </motion.div>
  );
};

export const Item: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => (
  <motion.div variants={fadeUp} className={className}>
    {children}
  </motion.div>
);

/* ----------------------------------------------------------------------------
 * AnimatedNumber — count-up when scrolled into view.
 * ------------------------------------------------------------------------- */
export const AnimatedNumber: React.FC<{
  value: number;
  decimals?: number;
  duration?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
}> = ({ value, decimals = 0, duration = 1.4, className, prefix = "", suffix = "" }) => {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-20% 0px" });
  const reduce = useReducedMotion();
  const [display, setDisplay] = useState(reduce ? value : 0);

  useEffect(() => {
    if (!inView || reduce) {
      if (reduce) setDisplay(value);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min((now - start) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(value * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, value, duration, reduce]);

  const formatted = display.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span ref={ref} className={className}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
};

/* ----------------------------------------------------------------------------
 * Tilt — 3D pointer-reactive hover surface with a glare highlight.
 * ------------------------------------------------------------------------- */
export const Tilt: React.FC<{
  children: React.ReactNode;
  className?: string;
  max?: number;
  glare?: boolean;
}> = ({ children, className, max = 8, glare = true }) => {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const rx = useSpring(0, { stiffness: 220, damping: 18 });
  const ry = useSpring(0, { stiffness: 220, damping: 18 });

  const onMove = (e: React.MouseEvent) => {
    if (reduce || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;
    ry.set((px - 0.5) * max * 2);
    rx.set((0.5 - py) * max * 2);
    ref.current.style.setProperty("--mx", `${px * 100}%`);
    ref.current.style.setProperty("--my", `${py * 100}%`);
  };
  const onLeave = () => {
    rx.set(0);
    ry.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={{ rotateX: rx, rotateY: ry, transformPerspective: 900 }}
      className={clsx("tilt-surface relative", className)}
    >
      {children}
      {glare && <span className="tilt-glare" />}
    </motion.div>
  );
};

/* ----------------------------------------------------------------------------
 * SectionHeader — kicker + title + optional action
 * ------------------------------------------------------------------------- */
export const SectionHeader: React.FC<{
  kicker?: string;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  right?: React.ReactNode;
  className?: string;
}> = ({ kicker, title, subtitle, icon, right, className }) => (
  <div className={clsx("flex flex-col md:flex-row md:items-end justify-between gap-4", className)}>
    <div className="space-y-2">
      {kicker && (
        <div className="flex items-center gap-2">
          {icon && <span className="text-cyan-300/80">{icon}</span>}
          <span className="kicker" style={{ color: "var(--role-accent)" }}>
            {kicker}
          </span>
        </div>
      )}
      <h1 className="font-display text-2xl md:text-[28px] font-bold text-white tracking-tight leading-tight">
        {title}
      </h1>
      {subtitle && <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">{subtitle}</p>}
    </div>
    {right && <div className="shrink-0">{right}</div>}
  </div>
);

/* ----------------------------------------------------------------------------
 * Pill
 * ------------------------------------------------------------------------- */
export const Pill: React.FC<{
  children: React.ReactNode;
  tone?: "cyan" | "emerald" | "amber" | "rose" | "violet" | "slate";
  className?: string;
}> = ({ children, tone = "slate", className }) => {
  const tones: Record<string, string> = {
    cyan: "bg-cyan-500/15 text-cyan-200 border-cyan-400/30",
    emerald: "bg-emerald-500/15 text-emerald-200 border-emerald-400/30",
    amber: "bg-amber-500/15 text-amber-200 border-amber-400/30",
    rose: "bg-rose-500/15 text-rose-200 border-rose-400/30",
    violet: "bg-violet-500/15 text-violet-200 border-violet-400/30",
    slate: "bg-white/5 text-slate-300 border-white/10",
  };
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border",
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
};

/* ----------------------------------------------------------------------------
 * LiveDot
 * ------------------------------------------------------------------------- */
export const LiveDot: React.FC<{ color?: string; className?: string }> = ({
  color = "#34d399",
  className,
}) => (
  <span
    className={clsx("inline-block w-2 h-2 rounded-full radar-dot", className)}
    style={{ color, backgroundColor: color }}
  />
);

/* ----------------------------------------------------------------------------
 * Buttons
 * ------------------------------------------------------------------------- */
export const PrimaryButton: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { icon?: React.ReactNode }
> = ({ children, className, icon, ...rest }) => (
  <motion.button
    whileTap={{ scale: 0.97 }}
    whileHover={{ y: -1 }}
    className={clsx(
      "btn-sheen inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white",
      "shadow-lg shadow-cyan-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
      className
    )}
    style={{
      backgroundImage: "linear-gradient(110deg, var(--role-accent), var(--role-accent-2))",
    }}
    {...(rest as any)}
  >
    {icon}
    {children}
  </motion.button>
);

export const GhostButton: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & { icon?: React.ReactNode }
> = ({ children, className, icon, ...rest }) => (
  <motion.button
    whileTap={{ scale: 0.97 }}
    className={clsx(
      "inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-slate-200",
      "bg-white/5 border border-white/10 hover:border-white/20 hover:bg-white/10 hover:text-white transition-all",
      className
    )}
    {...(rest as any)}
  >
    {icon}
    {children}
  </motion.button>
);

/* ----------------------------------------------------------------------------
 * StatCard — animated metric tile with tilt + rail
 * ------------------------------------------------------------------------- */
export const StatCard: React.FC<{
  label: string;
  value: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  hint?: React.ReactNode;
  icon?: React.ReactNode;
  tone?: string; // hex accent for the icon
}> = ({ label, value, decimals, suffix, prefix, hint, icon, tone = "#22d3ee" }) => (
  <Tilt className="h-full" max={6}>
    <div className="rail-card glass-panel glass-panel-hover h-full p-5 rounded-2xl space-y-3">
      <div className="flex items-center justify-between">
        <span className="kicker">{label}</span>
        <span
          className="w-9 h-9 rounded-xl flex items-center justify-center border"
          style={{
            color: tone,
            backgroundColor: `${tone}1f`,
            borderColor: `${tone}40`,
          }}
        >
          {icon}
        </span>
      </div>
      <div className="font-display text-3xl font-bold text-white">
        <AnimatedNumber value={value} decimals={decimals} prefix={prefix} suffix={suffix} />
      </div>
      {hint && <p className="text-[11px] text-slate-400 leading-relaxed">{hint}</p>}
    </div>
  </Tilt>
);

/* ----------------------------------------------------------------------------
 * Panel — standard glass container with optional featured aurora ring
 * ------------------------------------------------------------------------- */
export const Panel: React.FC<{
  children: React.ReactNode;
  className?: string;
  featured?: boolean;
  hover?: boolean;
}> = ({ children, className, featured, hover }) => (
  <div
    className={clsx(
      "glass-panel rounded-2xl",
      featured && "aurora-ring",
      hover && "glass-panel-hover rail-card",
      className
    )}
  >
    {children}
  </div>
);
