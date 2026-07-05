import { Sidebar } from "./Sidebar"
import { ReactNode } from "react"
import { useLocation } from "wouter"

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation()
  
  // Don't render sidebar on login page
  if (location === "/login") {
    return <main className="min-h-screen bg-background">{children}</main>
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <header className="h-16 border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10 flex items-center px-8">
          <h2 className="text-lg font-semibold text-foreground capitalize">
            {location === "/" ? "Dashboard Overview" : location.replace("/", "").replace("-", " ")}
          </h2>
        </header>
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
