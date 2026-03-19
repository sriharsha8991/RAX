import { motion } from 'framer-motion'
import { Upload, ScanSearch, GitMerge, ListChecks } from 'lucide-react'

const steps = [
  {
    icon: Upload,
    title: 'Upload Resumes',
    description: 'Drag and drop PDF or DOCX files — bulk upload supported.',
  },
  {
    icon: ScanSearch,
    title: 'AI Parses & Anonymizes',
    description: 'Gemini extracts skills; bias filter anonymizes identity signals.',
  },
  {
    icon: GitMerge,
    title: 'Graph + Vector Scoring',
    description: 'Neo4j structural match + Qdrant semantic similarity → fused score.',
  },
  {
    icon: ListChecks,
    title: 'Review & Act',
    description: 'Ranked candidates with explanations. Generate feedback or shortlist.',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-surface py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            From Upload to Decision in Seconds
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            A transparent, four-step pipeline you can watch in real time.
          </p>
        </div>

        {/* Steps */}
        <div className="mx-auto mt-16 max-w-4xl">
          {/* Desktop: horizontal */}
          <div className="hidden gap-0 md:grid md:grid-cols-4">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.12 }}
                className="relative flex flex-col items-center text-center"
              >
                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="absolute top-6 left-[calc(50%+24px)] h-px w-[calc(100%-48px)] bg-border" />
                )}

                {/* Step circle */}
                <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-full border-2 border-primary bg-background">
                  <step.icon size={20} className="text-primary" />
                </div>

                {/* Step number */}
                <div className="mt-3 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                  {i + 1}
                </div>

                <h3 className="mt-3 text-sm font-semibold text-foreground">
                  {step.title}
                </h3>
                <p className="mt-1.5 px-2 text-xs leading-relaxed text-muted-foreground">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Mobile: vertical timeline */}
          <div className="space-y-8 md:hidden">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="relative flex gap-4 pl-2"
              >
                {/* Vertical line */}
                {i < steps.length - 1 && (
                  <div className="absolute left-[23px] top-[48px] h-[calc(100%-16px)] w-px bg-border" />
                )}

                {/* Circle */}
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 border-primary bg-background">
                  <step.icon size={18} className="text-primary" />
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                      {i + 1}
                    </span>
                    <h3 className="text-sm font-semibold text-foreground">
                      {step.title}
                    </h3>
                  </div>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
