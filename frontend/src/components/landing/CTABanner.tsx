import { ArrowRight } from 'lucide-react'

export default function CTABanner() {
  return (
    <section className="py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-teal-600 to-teal-800 px-8 py-16 text-center dark:from-teal-700 dark:to-teal-900 sm:px-16">
          {/* Decorative circles */}
          <div className="pointer-events-none absolute -top-24 -right-24 h-64 w-64 rounded-full bg-white/10" />
          <div className="pointer-events-none absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-white/5" />

          <h2 className="relative text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to Hire Smarter?
          </h2>
          <p className="relative mx-auto mt-4 max-w-lg text-base leading-relaxed text-teal-100">
            Start screening with explainable AI — no setup required, no credit card,
            completely free.
          </p>
          <div className="relative mt-8">
            <a
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-teal-700 transition-colors hover:bg-teal-50"
            >
              Create Free Account
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
