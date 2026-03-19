import Navbar from '@/components/landing/Navbar'
import Hero from '@/components/landing/Hero'
import Features from '@/components/landing/Features'
import HowItWorks from '@/components/landing/HowItWorks'
import ScoringBreakdown from '@/components/landing/ScoringBreakdown'
import Comparison from '@/components/landing/Comparison'
import FAQ from '@/components/landing/FAQ'
import CTABanner from '@/components/landing/CTABanner'
import Footer from '@/components/landing/Footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <ScoringBreakdown />
        <Comparison />
        <FAQ />
        <CTABanner />
      </main>
      <Footer />
    </div>
  )
}
