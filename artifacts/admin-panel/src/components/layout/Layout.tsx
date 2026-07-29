import { Sidebar } from "./Sidebar"
import { ReactNode } from "react"
import { useLocation } from "wouter"

const PAGE_TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/users": "Users",
  "/settings": "Settings",
  "/broadcast": "Broadcast",
}

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation()
  
  if (location === "/login") {
    return <main className="min-h-screen bg-background">{children}</main>
  }

  const pageTitle = PAGE_TITLES[location] ?? location.replace("/", "").replace("-", " ")

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      <Sidebar />
      {/* Desktop: offset for sidebar. Mobile: no offset */}
      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        <header className="h-14 md:h-16 border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10 flex items-center px-4 md:px-8">
          <h2 className="text-base md:text-lg font-semibold text-foreground capitalize">
            {pageTitle}
          </h2>
        </header>
        {/* pb-20 on mobile to clear the bottom nav */}
        <main className="flex-1 p-4 md:p-8 pb-24 md:pb-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
