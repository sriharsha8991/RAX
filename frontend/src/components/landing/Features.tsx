import { motion } from 'framer-motion'
import {
  GitBranch,
  Brain,
  ShieldCheck,
  BarChart3,
  Radio,
  MessageSquareText,
} from 'lucide-react'

const features = [
  {
    icon: GitBranch,
    title: 'Knowledge Graph Matching',
    description:
      'Skills mapped as a graph, not a checklist. Partial matches through related skills are rewarded.',
  },
  {
    icon: Brain,
    title: 'Semantic Understanding',
    description:
      'Catches vocabulary mismatches. "ML Engineer" and "Machine Learning Developer" are equivalent.',
  },
  {
    icon: ShieldCheck,
    title: 'Bias-Aware Screening',
    description:
      'Names, institutions, and gender signals anonymized before any scoring begins.',
  },
  {
    icon: BarChart3,
    title: 'Explainable Scores',
    description:
      'Every score comes with a breakdown: what matched, what\'s missing, and why.',
  },
  {
    icon: Radio,
    title: 'Real-Time Pipeline',
    description:
      'Watch resumes get parsed, embedded, matched, and scored live via WebSocket.',
  },
  {
    icon: MessageSquareText,
    title: 'AI Feedback',
    description:
      'Generate constructive, personalized rejection feedback referencing specific skill gaps.',
  },
]

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

export default function Features() {
  return (
    <section id="features" className="py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Why RAX?
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Every feature designed to make hiring fair, fast, and explainable.
          </p>
        </div>

        {/* Grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          className="mx-auto mt-16 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={item}
              className="group rounded-xl border border-border bg-surface p-6 transition-all hover:border-primary/30 hover:shadow-md"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                <feature.icon size={20} />
              </div>
              <h3 className="text-base font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
