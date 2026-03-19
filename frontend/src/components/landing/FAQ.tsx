import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

const faqs = [
  {
    q: 'Is RAX free to use?',
    a: 'Yes. RAX runs entirely on free-tier cloud services — Supabase, Neo4j AuraDB, Qdrant Cloud, and Google Gemini API. No credit card required.',
  },
  {
    q: 'What file formats are supported?',
    a: 'RAX accepts PDF and DOCX resume files. You can bulk-upload multiple files at once via drag-and-drop.',
  },
  {
    q: 'How does the scoring system work?',
    a: 'Each candidate is scored across four dimensions: Structural Skill Match (50%), Semantic Similarity (30%), Experience Match (15%), and Education Match (5%). The weights are configurable per job posting.',
  },
  {
    q: 'Is candidate data anonymized?',
    a: 'Yes. Before any scoring, the bias filter removes names, gender signals, and replaces institution names with [UNIVERSITY]. Scoring never sees identifying information.',
  },
  {
    q: 'Can I customize scoring weights?',
    a: 'Yes. Weights are configurable per job posting. If you want to emphasize experience over skills for a senior role, you can adjust the percentages.',
  },
  {
    q: 'What AI model does RAX use?',
    a: 'RAX uses Google Gemini 1.5 Pro for resume parsing, skill normalization, scoring, and feedback generation. Embeddings use Gemini text-embedding-004 (768-dim vectors).',
  },
]

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <section id="faq" className="py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Frequently Asked Questions
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Everything you need to know about RAX.
          </p>
        </div>

        {/* Accordion */}
        <div className="mx-auto mt-12 max-w-2xl divide-y divide-border rounded-xl border border-border">
          {faqs.map((faq, i) => {
            const isOpen = openIndex === i
            return (
              <div key={i}>
                <button
                  onClick={() => setOpenIndex(isOpen ? null : i)}
                  className="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium text-foreground transition-colors hover:bg-muted/50"
                  aria-expanded={isOpen}
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    size={16}
                    className={cn(
                      'shrink-0 text-muted-foreground transition-transform duration-200',
                      isOpen && 'rotate-180'
                    )}
                  />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-4 text-sm leading-relaxed text-muted-foreground">
                        {faq.a}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
