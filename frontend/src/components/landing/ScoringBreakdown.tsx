import { motion } from 'framer-motion'

const dimensions = [
  {
    label: 'Structural Skill Match',
    weight: 50,
    color: 'bg-primary',
    desc: 'Direct + similar skill matches via knowledge graph traversal.',
  },
  {
    label: 'Semantic Similarity',
    weight: 30,
    color: 'bg-info',
    desc: 'Cosine similarity between resume and job description embeddings.',
  },
  {
    label: 'Experience Match',
    weight: 15,
    color: 'bg-warning',
    desc: 'Years-per-skill comparison against job requirements.',
  },
  {
    label: 'Education Match',
    weight: 5,
    color: 'bg-accent',
    desc: 'Degree level comparison — tiebreaker, not gatekeeper.',
  },
]

export default function ScoringBreakdown() {
  return (
    <section id="scoring" className="py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-3xl">
          {/* Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Multi-Dimensional. Not a Single Number.
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              Each candidate is evaluated across four weighted components for a fair,
              explainable score.
            </p>
          </div>

          {/* Stacked bar */}
          <motion.div
            initial={{ opacity: 0, scaleX: 0 }}
            whileInView={{ opacity: 1, scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mt-12 origin-left"
          >
            <div className="flex h-6 overflow-hidden rounded-full">
              {dimensions.map((dim) => (
                <div
                  key={dim.label}
                  className={`${dim.color} flex items-center justify-center`}
                  style={{ width: `${dim.weight}%` }}
                >
                  <span className="text-[10px] font-bold text-white drop-shadow-sm">
                    {dim.weight}%
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Legend */}
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {dimensions.map((dim, i) => (
              <motion.div
                key={dim.label}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: i * 0.08 }}
                className="flex items-start gap-3"
              >
                <div className={`mt-1.5 h-3 w-3 shrink-0 rounded-full ${dim.color}`} />
                <div>
                  <div className="text-sm font-semibold text-foreground">
                    {dim.label}{' '}
                    <span className="font-normal text-muted-foreground">
                      ({dim.weight}%)
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">
                    {dim.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Formula */}
          <div className="mt-10 rounded-xl border border-border bg-surface p-4 text-center">
            <code className="text-xs text-muted-foreground sm:text-sm">
              Final Score = 0.50 × Structural + 0.30 × Semantic + 0.15 × Experience + 0.05 × Education
            </code>
          </div>
        </div>
      </div>
    </section>
  )
}
