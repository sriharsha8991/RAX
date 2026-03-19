import { useTheme } from '@/components/ThemeProvider'
import { Sun, Moon } from 'lucide-react'

const productLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Scoring', href: '#scoring' },
  { label: 'FAQ', href: '#faq' },
]

const resourceLinks = [
  { label: 'Documentation', href: '#' },
  { label: 'Architecture', href: '#' },
  { label: 'GitHub', href: '#' },
]

const teamLinks = [
  { label: 'About Us', href: '#' },
  { label: 'Contact', href: '#' },
]

export default function Footer() {
  const { theme, toggleTheme } = useTheme()

  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8 lg:py-16">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <span className="text-sm font-bold text-primary-foreground">R</span>
              </div>
              <span className="text-lg font-bold text-foreground">RAX</span>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              AI-powered hiring that's fair, fast, and explainable.
            </p>
            <button
              onClick={toggleTheme}
              className="mt-4 inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <>
                  <Moon size={14} />
                  Dark mode
                </>
              ) : (
                <>
                  <Sun size={14} />
                  Light mode
                </>
              )}
            </button>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-foreground">Product</h4>
            <ul className="mt-3 space-y-2">
              {productLinks.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-foreground">Resources</h4>
            <ul className="mt-3 space-y-2">
              {resourceLinks.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Team */}
          <div>
            <h4 className="text-sm font-semibold text-foreground">Team</h4>
            <ul className="mt-3 space-y-2">
              {teamLinks.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 border-t border-border pt-6 text-center">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} RAX — Built for fair hiring.
          </p>
        </div>
      </div>
    </footer>
  )
}
