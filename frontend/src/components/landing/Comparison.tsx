import { motion } from 'framer-motion'
import { X, Check } from 'lucide-react'

const rows = [
  { aspect: 'Matching Method', ats: 'Keyword string matching', rax: 'Knowledge graph + vector similarity' },
  { aspect: 'Score Type', ats: 'Binary pass / fail', rax: 'Multi-dimensional weighted score' },
  { aspect: 'Explainability', ats: 'No explanation given', rax: 'Full breakdown with reasoning' },
  { aspect: 'Synonym Handling', ats: 'Misses vocabulary mismatches', rax: 'Semantic embeddings catch synonyms' },
  { aspect: 'Bias Protection', ats: 'Institutions visible to scorer', rax: 'Names & institutions anonymized' },
  { aspect: 'Skill Relationships', ats: 'Flat keyword list', rax: 'Auto-enriching skill taxonomy graph' },
]

export default function Comparison() {
  return (
    <section className="bg-surface py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Traditional ATS vs. RAX
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            See what changes when you move from keyword filters to AI reasoning.
          </p>
        </div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mx-auto mt-12 max-w-3xl overflow-hidden rounded-xl border border-border"
        >
          {/* Header row */}
          <div className="grid grid-cols-3 border-b border-border bg-muted text-sm font-semibold">
            <div className="px-4 py-3 text-muted-foreground" />
            <div className="border-l border-border px-4 py-3 text-center text-muted-foreground">
              Traditional ATS
            </div>
            <div className="border-l border-border bg-primary/5 px-4 py-3 text-center text-primary">
              RAX
            </div>
          </div>

          {/* Data rows */}
          {rows.map((row, i) => (
            <div
              key={row.aspect}
              className={`grid grid-cols-3 text-sm ${i < rows.length - 1 ? 'border-b border-border' : ''}`}
            >
              <div className="px-4 py-3.5 font-medium text-foreground">
                {row.aspect}
              </div>
              <div className="flex items-start gap-2 border-l border-border px-4 py-3.5 text-muted-foreground">
                <X size={14} className="mt-0.5 shrink-0 text-destructive/70" />
                <span>{row.ats}</span>
              </div>
              <div className="flex items-start gap-2 border-l border-border bg-primary/5 px-4 py-3.5 text-foreground">
                <Check size={14} className="mt-0.5 shrink-0 text-primary" />
                <span>{row.rax}</span>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
