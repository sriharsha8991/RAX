import { motion } from 'framer-motion'
import { ArrowRight, Play } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-28">
      {/* Background gradient + dot grid */}
      <div className="pointer-events-none absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-50 via-background to-background dark:from-teal-950/20 dark:via-background dark:to-background" />
        <div
          className="absolute inset-0 opacity-[0.4] dark:opacity-[0.15]"
          style={{
            backgroundImage: 'radial-gradient(circle, var(--color-border) 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }}
        />
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Left column — copy */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className="max-w-xl"
          >
            {/* Eyebrow */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3.5 py-1.5">
              <div className="h-1.5 w-1.5 rounded-full bg-accent" />
              <span className="text-xs font-semibold tracking-wide text-accent">
                AI-Powered Hiring
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl font-bold leading-[1.1] tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Hire for Skills,{' '}
              <span className="text-primary">Not Keywords</span>
            </h1>

            {/* Subheadline */}
            <p className="mt-6 text-lg leading-relaxed text-muted-foreground">
              RAX replaces keyword-matching ATS with explainable AI.
              Understand <em>why</em> a candidate fits through knowledge graph
              reasoning and semantic intelligence.
            </p>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <a
                href="/register"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-hover"
              >
                Start Screening
                <ArrowRight size={16} />
              </a>
              <a
                href="#how-it-works"
                className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
              >
                <Play size={14} />
                See How It Works
              </a>
            </div>

            {/* Trust line */}
            <p className="mt-6 text-xs text-muted-foreground">
              Free to use · No credit card · Setup in 2 minutes
            </p>
          </motion.div>

          {/* Right column — visual */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
            className="relative hidden lg:block"
          >
            <div className="relative rounded-2xl border border-border bg-surface p-6 shadow-xl">
              {/* Mock dashboard header */}
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-destructive/60" />
                  <div className="h-3 w-3 rounded-full bg-warning/60" />
                  <div className="h-3 w-3 rounded-full bg-success/60" />
                </div>
                <div className="rounded bg-muted px-3 py-1 text-[10px] text-muted-foreground">
                  RAX Dashboard
                </div>
              </div>

              {/* Mock candidate card */}
              <div className="rounded-xl border border-border bg-background p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs text-muted-foreground">Top Candidate</div>
                    <div className="mt-1 text-sm font-semibold text-foreground">[CANDIDATE_42]</div>
                    <div className="mt-0.5 text-xs text-muted-foreground">Senior Full-Stack Engineer</div>
                  </div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-primary">
                    <span className="text-sm font-bold text-primary">92</span>
                  </div>
                </div>

                {/* Score bars */}
                <div className="mt-4 space-y-2.5">
                  {[
                    { label: 'Structural Match', pct: 95, color: 'bg-primary' },
                    { label: 'Semantic Similarity', pct: 88, color: 'bg-info' },
                    { label: 'Experience', pct: 82, color: 'bg-warning' },
                    { label: 'Education', pct: 100, color: 'bg-accent' },
                  ].map((bar) => (
                    <div key={bar.label}>
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-muted-foreground">{bar.label}</span>
                        <span className="font-medium text-foreground">{bar.pct}%</span>
                      </div>
                      <div className="mt-1 h-1.5 w-full rounded-full bg-muted">
                        <motion.div
                          className={`h-full rounded-full ${bar.color}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${bar.pct}%` }}
                          transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Skills tags */}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'GraphQL'].map((skill) => (
                    <span
                      key={skill}
                      className="rounded-md bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Floating graph nodes */}
              <div className="absolute -top-4 -right-4 flex h-10 w-10 items-center justify-center rounded-full border border-border bg-background text-[10px] font-semibold text-primary shadow-lg">
                JS
              </div>
              <div className="absolute -bottom-3 -left-3 flex h-8 w-8 items-center justify-center rounded-full border border-border bg-background text-[9px] font-semibold text-accent shadow-lg">
                AI
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
